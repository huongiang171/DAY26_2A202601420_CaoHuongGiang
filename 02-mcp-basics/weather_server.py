"""MCP SERVER minh hoạ — công bố tool `get_weather` qua giao thức MCP.

Khác với function calling: tool nằm ở một server ĐỘC LẬP. Server tự "khai
báo" tool của mình; bất kỳ MCP client nào (Claude Code, Claude Desktop,
Cursor, hoặc weather_client.py) cũng cắm vào dùng được mà không cần biết
code bên trong.

Schema của tool được TỰ ĐỘNG sinh ra từ type hints + docstring.

Chạy trực tiếp:
    pip install -r ../requirements.txt
    python weather_server.py

Đăng ký với Claude Code (làm 1 lần, dùng mãi):
    claude mcp add weather -- python /đường/dẫn/tới/weather_server.py
"""

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("weather")

_MOCK_DB = {
    "Hanoi": "29°C, trời mưa",
    "Haiphong": "33°C, mưa rào",
    "Danang": "30°C, nhiều mây",
}

_FORECAST_DB = {
    "Hanoi": "Ngày mai: 30°C, có mây. Ngày kia: 32°C, nắng.",
    "Haiphong": "Ngày mai: 31°C, mưa rào. Ngày kia: 33°C, nắng nhẹ.",
    "Danang": "Ngày mai: 32°C, nắng ráo. Ngày kia: 34°C, nắng nóng."
}

@mcp.tool()
def get_weather(city: str) -> str:
    """Lấy thời tiết hiện tại của một thành phố."""
    return f"{city}: {_MOCK_DB.get(city, '28°C, không có dữ liệu chi tiết')}"

@mcp.tool()
def get_forecast(city: str, days: int = 2) -> str:
    """Lấy dự báo thời tiết cho những ngày tới của một thành phố.
    
    Args:
        city: Tên thành phố
        days: Số ngày dự báo (mặc định 2)
    """
    forecast = _FORECAST_DB.get(city, "Không có dữ liệu dự báo cho thành phố này.")
    return f"Dự báo {days} ngày tới cho {city}: {forecast}"


if __name__ == "__main__":
    mcp.run()  # mặc định chạy qua stdio
