const portValue = process.env.PORT || "3001"
const port = Number(portValue)
if (!Number.isFinite(port)) {
  throw new Error("Invalid PORT")
}

export const config = {
  port,
  mongoUri: process.env.MONGODB_URI || "mongodb://localhost:27017/davinci_resolve_librechat",
  mcpBaseUrl: process.env.MCP_BASE_URL || "http://127.0.0.1:8020/mcp",
  mcpApiKey: process.env.MCP_API_KEY || "",
  corsOrigin: process.env.CORS_ORIGIN || "*",
  jwtSecret: process.env.JWT_SECRET || "dev-secret",
  mcpHealthMethod: process.env.MCP_HEALTH_METHOD || "list_tools"
}
