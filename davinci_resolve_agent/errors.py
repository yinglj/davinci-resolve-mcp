# errors.py

# 定义 JSON-RPC 错误码和消息
JSONRPC_ERROR_CODES = {
    "INVALID_API_KEY": {"code": -32600, "message": "无效或缺失的 API 密钥"},
    "INVALID_REQUEST": {"code": -32600, "message": "无效的 JSON-RPC 请求: {}"},
    "NOT_CONNECTED": {"code": -32600, "message": "服务器未连接"},
    "SERVER_ERROR": {"code": -32603, "message": "{}: {}"},
    "INVALID_PARAMS": {"code": -32602, "message": "无效参数: {}"},
    "INVALID_SESSION": {"code": -32600, "message": "无效会话: {}"},
    "METHOD_NOT_FOUND": {"code": -32601, "message": "方法未找到: {}"},
    "PARSE_ERROR": {"code": -32700, "message": "解析错误: {}"},
}
