import { config } from "../config.js"
import type { McpCall } from "../types.js"

type McpResponse = {
  jsonrpc?: string
  id?: number | string
  result?: unknown
  error?: { code?: number; message?: string }
}

export async function callMcp({ method, params }: McpCall) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  }
  if (config.mcpApiKey) {
    headers.Authorization = `Bearer ${config.mcpApiKey}`
  }
  const response = await fetch(config.mcpBaseUrl, {
    method: "POST",
    headers,
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: Date.now(),
      method,
      params
    })
  })
  const payload = (await response.json()) as McpResponse
  if (!response.ok) {
    throw new Error(`MCP HTTP ${response.status}`)
  }
  if (payload.error) {
    throw new Error(payload.error.message || "MCP error")
  }
  return payload.result ?? payload
}
