import sqlite3
import os
import json
from datetime import datetime, timezone

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer

DB_PATH = os.path.join(os.path.dirname(__file__), "sales.db")
SERVER_VERSION = "2.0.0"

# --- Authentication Configuration ---
AUTH_TOKEN = os.getenv("HW_AUTH_TOKEN", "order-secret-key-123")
VALID_TOKENS = {
    AUTH_TOKEN: "dev-client"
}

class HomeworkTokenVerifier(TokenVerifier):
    """Kiểm tra token xác thực Bearer Token."""
    async def verify_token(self, token: str) -> AccessToken | None:
        client_id = VALID_TOKENS.get(token)
        if client_id is None:
            print(f"❌ Verification failed for token: {token}")
            return None
        print(f"✅ Token verified successfully for client_id: {client_id}")
        return AccessToken(token=token, client_id=client_id, scopes=["sales:read"])

# --- Initialize Secure MCP Server ---
mcp = MCPServer(
    "sales-manager",
    auth=AuthSettings(
        issuer_url="http://localhost:8090",
        resource_server_url="http://localhost:8090",
    ),
    token_verifier=HomeworkTokenVerifier(),
    instructions=f"Sales SQLite Manager MCP Server v{SERVER_VERSION}."
)

# --- Helper DB function ---
def execute_query(query: str, params: tuple = ()) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ─── BÀI 1: Tool Tra cứu Tồn kho ───
@mcp.tool()
def check_inventory(product_name: str) -> str:
    """Tra cứu số lượng hàng tồn của một sản phẩm trong kho.
    
    Args:
        product_name: Tên sản phẩm cần tra cứu (ví dụ: Laptop, Mouse, Keyboard, Monitor, Cable)
    """
    rows = execute_query("SELECT stock_count FROM inventory WHERE product_name = ?", (product_name,))
    if not rows:
        return f"Sản phẩm '{product_name}' không tồn tại trong kho hàng."
    return f"Sản phẩm '{product_name}' hiện còn {rows[0][0]} cái trong kho."

# ─── BÀI 3: Tool v1 (Tương thích ngược) ───
@mcp.tool()
def get_order_status(order_id: str) -> str:
    """[v1] Tra cứu trạng thái đơn hàng. Trả về kết quả chuỗi văn bản đơn giản.
    Lưu ý: Tool này đã cũ (deprecated), vui lòng dùng get_order_status_v2.
    
    Args:
        order_id: Mã đơn hàng cần tra cứu (ví dụ: OD-101, OD-102)
    """
    rows = execute_query("SELECT customer_name, status FROM orders WHERE order_id = ?", (order_id,))
    if not rows:
        return f"Đơn hàng '{order_id}' không tồn tại."
    customer, status = rows[0]
    return f"Đơn hàng {order_id} của khách hàng {customer} có trạng thái: {status}"

# ─── BÀI 3: Tool v2 (Mới, trả về JSON chi tiết, hỗ trợ tham số tùy chọn) ───
@mcp.tool()
def get_order_status_v2(order_id: str, include_items: bool = False) -> str:
    """[v2] Tra cứu trạng thái chi tiết của đơn hàng dưới dạng cấu trúc JSON.
    Hỗ trợ hiển thị danh sách sản phẩm chi tiết.
    
    Args:
        order_id: Mã đơn hàng cần tra cứu (ví dụ: OD-101, OD-102)
        include_items: Có kèm theo danh sách sản phẩm chi tiết trong đơn hàng không (mặc định: False)
    """
    rows = execute_query("SELECT customer_name, status, total_amount FROM orders WHERE order_id = ?", (order_id,))
    if not rows:
        return json.dumps({"error": f"Đơn hàng '{order_id}' không tồn tại", "order_id": order_id, "api_version": "2.0"}, ensure_ascii=False)
    
    customer_name, status, total_amount = rows[0]
    result = {
        "api_version": "2.0",
        "order_id": order_id,
        "customer": customer_name,
        "status": status,
        "total_amount": total_amount,
        "query_time": datetime.now(timezone.utc).isoformat()
    }
    
    if include_items:
        item_rows = execute_query("SELECT product_name, quantity, price FROM order_items WHERE order_id = ?", (order_id,))
        items = [{"product_name": name, "quantity": qty, "price": prc} for name, qty, prc in item_rows]
        result["items"] = items
        
    return json.dumps(result, ensure_ascii=False)

# ─── BÀI 3: Resource công bố thông tin Server Metadata ───
@mcp.resource("server://info")
def server_info() -> str:
    """Trả về metadata của server bao gồm phiên bản, danh sách tool lỗi thời và tài liệu chuyển đổi."""
    return json.dumps({
        "server_name": "sales-manager",
        "server_version": SERVER_VERSION,
        "deprecated_tools": ["get_order_status"],
        "new_tools": ["get_order_status_v2"],
        "migration_guide": "Sử dụng get_order_status_v2 thay thế cho get_order_status. "
                           "v2 trả về JSON chi tiết và hỗ trợ tham số 'include_items'."
    }, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    
    # Kiểm tra chế độ chạy (HTTP hoặc stdio)
    # Chạy HTTP nếu truyền tham số '--http' hoặc cấu hình env 'PORT'
    is_http_mode = (len(sys.argv) > 1 and sys.argv[1] == "--http") or bool(os.getenv("PORT"))
    
    if is_http_mode:
        port = int(os.getenv("PORT", 8090))
        print(f"🚀 Starting Homework Secure MCP Server on HTTP http://0.0.0.0:{port}/mcp")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        # Chạy stdio chế độ mặc định (dành cho Claude Code, Cursor cắm trực tiếp local)
        print("Starting Homework MCP Server in stdio mode for local integration (Claude Code / Cursor)...", file=sys.stderr)
        mcp.run()
