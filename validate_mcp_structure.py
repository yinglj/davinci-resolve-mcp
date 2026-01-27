#!/usr/bin/env python3
"""
验证 MCP 模块结构的脚本
检查 mcp_tools、mcp_resources、mcp_tasks、mcp_prompts 的完整性
"""

import os
import ast
import sys
from pathlib import Path


def check_file_syntax(filepath):
    """检查 Python 文件语法"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)


def find_decorators(filepath, decorator_name):
    """查找文件中的装饰器"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        decorators = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if (
                            hasattr(decorator.func, "attr")
                            and decorator.func.attr == decorator_name
                        ):
                            decorators.append(
                                {
                                    "function": node.name,
                                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                                    "line": node.lineno,
                                }
                            )
                    elif (
                        hasattr(decorator, "attr") and decorator.attr == decorator_name
                    ):
                        decorators.append(
                            {
                                "function": node.name,
                                "is_async": isinstance(node, ast.AsyncFunctionDef),
                                "line": node.lineno,
                            }
                        )
        return decorators
    except Exception as e:
        return []


def check_task_async(filepath):
    """检查任务是否使用 async def"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        # 检查是否有 task=True 参数
                        has_task_true = False
                        for keyword in decorator.keywords:
                            if keyword.arg == "task" and isinstance(
                                keyword.value, ast.Constant
                            ):
                                if keyword.value.value is True:
                                    has_task_true = True

                        if has_task_true and not isinstance(node, ast.AsyncFunctionDef):
                            issues.append(
                                {
                                    "function": node.name,
                                    "line": node.lineno,
                                    "issue": "Task function must be async",
                                }
                            )
        return issues
    except Exception as e:
        return [{"error": str(e)}]


def main():
    base_dir = Path(__file__).parent

    print("=" * 80)
    print("DaVinci Resolve MCP 模块结构验证")
    print("=" * 80)

    modules = {
        "mcp_tools": {
            "path": base_dir / "src" / "mcp_tools",
            "expected_decorator": "tool",
            "forbidden_decorator": "resource",
        },
        "mcp_resources": {
            "path": base_dir / "src" / "mcp_resources",
            "expected_decorator": "resource",
            "forbidden_decorator": "tool",
        },
        "mcp_tasks": {
            "path": base_dir / "src" / "mcp_tasks",
            "expected_decorator": "tool",
            "check_async": True,
        },
        "mcp_prompts": {
            "path": base_dir / "src" / "mcp_prompts",
            "expected_decorator": "prompt",
        },
    }

    all_ok = True

    for module_name, config in modules.items():
        print(f"\n{'=' * 80}")
        print(f"检查模块: {module_name}")
        print(f"{'=' * 80}")

        module_path = config["path"]
        if not module_path.exists():
            print(f"❌ 模块目录不存在: {module_path}")
            all_ok = False
            continue

        # 检查所有 Python 文件
        py_files = list(module_path.rglob("*.py"))
        print(f"\n找到 {len(py_files)} 个 Python 文件")

        for py_file in py_files:
            rel_path = py_file.relative_to(module_path)

            # 检查语法
            syntax_ok, error = check_file_syntax(py_file)
            if not syntax_ok:
                print(f"❌ 语法错误 [{rel_path}]: {error}")
                all_ok = False
                continue

            # 跳过 __init__.py
            if py_file.name == "__init__.py":
                print(f"✓ {rel_path} - 语法正确")
                continue

            # 检查装饰器
            if "expected_decorator" in config:
                decorators = find_decorators(py_file, config["expected_decorator"])
                if decorators:
                    print(
                        f"✓ {rel_path} - 找到 {len(decorators)} 个 @mcp.{config['expected_decorator']}()"
                    )

            # 检查禁止的装饰器
            if "forbidden_decorator" in config:
                forbidden = find_decorators(py_file, config["forbidden_decorator"])
                if forbidden:
                    print(
                        f"❌ {rel_path} - 发现禁止的装饰器 @mcp.{config['forbidden_decorator']}()"
                    )
                    for item in forbidden:
                        print(f"   行 {item['line']}: {item['function']}")
                    all_ok = False

            # 检查任务是否使用 async
            if config.get("check_async"):
                issues = check_task_async(py_file)
                if issues:
                    print(f"❌ {rel_path} - 任务函数必须是异步的")
                    for issue in issues:
                        if "error" in issue:
                            print(f"   错误: {issue['error']}")
                        else:
                            print(
                                f"   行 {issue['line']}: {issue['function']} - {issue['issue']}"
                            )
                    all_ok = False

    print(f"\n{'=' * 80}")
    if all_ok:
        print("✅ 所有检查通过！")
    else:
        print("❌ 发现问题，请修复上述错误")
    print(f"{'=' * 80}\n")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
