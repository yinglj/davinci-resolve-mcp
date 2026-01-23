# davinci_resolve_agent/agent_delegator.py
"""
Agent delegation framework for multi-agent coordination.
Allows Director agent to delegate tasks to specialized role agents (Editor, Colorist, Sound Engineer).
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from logger import logger
from mcp_agents import create_multi_agent


class AgentDelegator:
    """
    Manages delegation of tasks between different role-based agents.
    The Director agent can delegate subtasks to specialized agents.
    """

    def __init__(self):
        self.agents = {}  # role -> agent mapping
        self.delegation_history = []  # Track delegations for debugging

    async def initialize_agents(self, shared_knowledge_base=None, shared_vector_db=None, shared_content_db=None) -> bool:
        """
        Initialize all role-based agents.
        Accepts shared knowledge base and databases to avoid re-initialization.
        Returns True if at least the Director agent was initialized successfully.
        """
        roles = ["director", "editor", "colorist", "sound_engineer"]

        for role in roles:
            try:
                agent = await create_multi_agent(
                    role=role,
                    knowledge_base=shared_knowledge_base,
                    vector_db=shared_vector_db,
                    content_db=shared_content_db
                )
                if agent:
                    self.agents[role] = agent
                    logger.info(f"Initialized {role} agent: {agent.name}")
                else:
                    logger.warning(f"Failed to initialize {role} agent")
            except Exception as e:
                logger.error(f"Error initializing {role} agent: {e}")

        # At minimum, we need a director agent
        if "director" not in self.agents:
            logger.error(
                "Director agent initialization failed - delegation framework unavailable"
            )
            return False

        logger.info(
            f"Agent delegation framework initialized with {len(self.agents)} agents"
        )
        return True

    async def delegate_task(
        self, role: str, task_description: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delegate a task to a specific role agent.

        Args:
            role: Target agent role ("editor", "colorist", "sound_engineer")
            task_description: Description of the task to perform
            context: Additional context information

        Returns:
            Dict containing the agent's response and metadata
        """
        if role not in self.agents:
            return {
                "success": False,
                "error": f"No {role} agent available",
                "role": role,
                "task": task_description,
            }

        agent = self.agents[role]
        context = context or {}

        # Format the task with context
        full_task = f"""
Task: {task_description}

Context:
{json.dumps(context, indent=2)}

Please execute this task using available tools and provide a detailed response.
"""

        try:
            # Record delegation
            delegation_record = {
                "role": role,
                "task": task_description,
                "context": context,
                "timestamp": asyncio.get_event_loop().time(),
            }
            self.delegation_history.append(delegation_record)

            # Execute the task
            response = await agent.arun(
                input=full_task,
                stream=False,
                markdown=True,
                stream_intermediate_steps=False,
            )

            result = {
                "success": True,
                "role": role,
                "task": task_description,
                "response": str(response),
                "metadata": {
                    "agent_name": agent.name,
                    "delegation_id": len(self.delegation_history) - 1,
                },
            }

            logger.info(f"Task delegated to {role} agent completed successfully")
            return result

        except Exception as e:
            logger.error(f"Task delegation to {role} agent failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "role": role,
                "task": task_description,
            }

    async def delegate_sequence(
        self,
        tasks: List[Dict[str, Any]],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute multiple tasks in sequential order.
        Stops execution if a task fails.

        Args:
            tasks: List of task definitions
            initial_context: Initial context to start with

        Returns:
            Dict containing success status and list of results
        """
        results = []
        context = initial_context or {}

        for i, task_def in enumerate(tasks):
            role = task_def.get("role")
            task_desc = task_def.get("task", "")

            # 1. Prepare Context
            # Merge global context with specific task context
            task_context = task_def.get("context", {}).copy()
            task_context.update(context)

            logger.info(
                f"Executing sequence step {i+1}/{len(tasks)}: {role} -> {task_desc}"
            )

            # 2. Dynamic Variable Substitution
            # Try to format task description with current context
            # This allows passing variables like IDs between steps if they exist in context
            try:
                task_desc = task_desc.format(**context)
            except (KeyError, ValueError):
                # If keys are missing (which is common if context doesn't have them yet),
                # we assume the placeholders are managed by WorkflowTemplate.get_tasks
                # or are meant for the Agent to interpret.
                pass

            # 3. Execute Step
            result = await self.delegate_task(role, task_desc, task_context)
            results.append(result)

            # 4. Handle Failure (Fail Fast)
            if not result.get("success", False):
                logger.error(f"Workflow sequence stopped at step {i+1} due to failure")
                return {
                    "success": False,
                    "results": results,
                    "stopped_at_index": i,
                    "error": result.get("error", "Unknown error in step execution"),
                }

        logger.info(
            f"Workflow sequence completed successfully with {len(results)} steps"
        )
        return {"success": True, "results": results}

    async def delegate_multiple_tasks(
        self, delegations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Delegate multiple tasks in parallel.
        Not recommended for dependent tasks. Use delegate_sequence instead.

        Args:
            delegations: List of delegation requests, each with 'role', 'task', 'context'

        Returns:
            List of delegation results
        """
        tasks = []
        for delegation in delegations:
            role = delegation.get("role")
            task = delegation.get("task", "")
            context = delegation.get("context", {})

            if not role or not task:
                logger.warning(f"Invalid delegation request: {delegation}")
                continue

            tasks.append(self.delegate_task(role, task, context))

        # Execute all delegations in parallel
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions in results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(
                        {"success": False, "error": str(result), "delegation_index": i}
                    )
                else:
                    processed_results.append(result)

            return processed_results

        return []

    def get_delegation_history(self) -> List[Dict[str, Any]]:
        """Get the history of all delegations performed."""
        return self.delegation_history.copy()

    def get_available_roles(self) -> List[str]:
        """Get list of available agent roles."""
        return list(self.agents.keys())

    async def cleanup(self):
        """Cleanup resources."""
        self.agents.clear()
        self.delegation_history.clear()
        logger.info("Agent delegator cleaned up")
