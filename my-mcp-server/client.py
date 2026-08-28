import asyncio
import os
import sys
import json
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SERVER_URL = "http://localhost:8090/mcp"

async def run_client(token: str, test_description: str) -> None:
    print(f"\n--- {test_description} ---")
    print(f"Connecting to: {SERVER_URL} using token: '{token}'")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        # 1. Establish HTTP Client and MCP connection
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as http_client:
            async with streamable_http_client(SERVER_URL, http_client=http_client) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    print("✅ MCP Connection Initialized successfully!")
                    
                    # 2. BÀI 3: Đọc resource metadata server://info
                    print("\n[Đọc Resource] Đang tải thông tin server://info...")
                    info = await session.read_resource("server://info")
                    meta = json.loads(info.contents[0].text)
                    print(f" * Server: {meta['server_name']} v{meta['server_version']}")
                    print(f" * Lỗi thời: {meta['deprecated_tools']}")
                    print(f" * Phiên bản mới: {meta['new_tools']}")
                    print(f" * Hướng dẫn di chuyển: {meta['migration_guide']}")
                    
                    # 3. Liệt kê danh sách các tools khả dụng
                    print("\n[Khám phá Tool] Liệt kê các tools mà Server cung cấp:")
                    tools_list = await session.list_tools()
                    tool_names = []
                    for tool in tools_list.tools:
                        print(f" - {tool.name}: {tool.description}")
                        tool_names.append(tool.name)
                        
                    # 4. BÀI 1: Gọi tool kiểm tra tồn kho
                    print("\n[Gọi Tool 1] check_inventory...")
                    for product in ["Laptop", "Monitor", "IPhone (không có)"]:
                        res = await session.call_tool("check_inventory", {"product_name": product})
                        print(f" * Tra cứu '{product}' -> {res.content[0].text}")
                        
                    # 5. BÀI 3: Gọi tool kiểm tra trạng thái đơn hàng (Chọn phiên bản động)
                    print("\n[Gọi Tool 2] get_order_status (Chọn phiên bản tự động)...")
                    order_id = "OD-101"
                    
                    # Chọn tool tối ưu dựa trên metadata được công bố
                    if "get_order_status_v2" in tool_names:
                        print(f" 👉 Phát hiện tool get_order_status_v2. Gọi v2 với include_items=True...")
                        res = await session.call_tool("get_order_status_v2", {
                            "order_id": order_id,
                            "include_items": True
                        })
                        data = json.loads(res.content[0].text)
                        print(f" * Kết quả chi tiết (JSON):\n{json.dumps(data, indent=4, ensure_ascii=False)}")
                    else:
                        print(f" 👉 Không thấy v2, gọi tool v1 cũ...")
                        res = await session.call_tool("get_order_status", {"order_id": order_id})
                        print(f" * Kết quả: {res.content[0].text}")
                        
    except httpx.HTTPStatusError as e:
        if e.response.status_code in [401, 403]:
            print(f"❌ Xác thực không thành công (HTTP {e.response.status_code}): {e.response.text.strip()}")
        else:
            print(f"❌ Lỗi HTTP: {e}")
    except Exception as e:
        print(f"❌ Kết nối thất bại: {e}")
        import traceback
        traceback.print_exc()

async def main():
    # TEST 1: Chạy với Token Sai (Kiểm tra Bài 2)
    await run_client(token="token-sai-123", test_description="TEST 1: Chạy với Token sai (Yêu cầu báo lỗi 401/403)")
    
    # TEST 2: Chạy với Token Đúng (Kiểm tra Bài 1, Bài 2, Bài 3)
    correct_token = os.getenv("HW_AUTH_TOKEN", "order-secret-key-123")
    await run_client(token=correct_token, test_description="TEST 2: Chạy với Token đúng (Quyền truy cập thành công)")

if __name__ == "__main__":
    # Đặt mã hóa UTF-8 cho stdout trên Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    asyncio.run(main())
