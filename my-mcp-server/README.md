# Bài tập về nhà: SQLite Order & Inventory Manager MCP Server

Dự án này là lời giải trọn vẹn cho các mức độ Dễ, Trung bình và Khó của bài Lab MCP. Dự án thực hiện công việc thực tế là **Quản lý Đơn hàng & Tồn kho từ cơ sở dữ liệu SQLite cục bộ (offline)**.

---

## 🌟 Tính năng & Mức độ hoàn thành

1. **Bài 1 (Dễ) — Khai báo & Thực thi Tool**:
   - `check_inventory`: Kiểm tra số lượng tồn kho của sản phẩm trong SQLite.
   - `get_order_status` (v1): Xem trạng thái đơn hàng (dạng text đơn giản).

2. **Bài 2 (Trung bình) — Giao thức HTTP & Xác thực (Auth)**:
   - Chạy trên Streamable HTTP (cổng `8090`).
   - Xác thực Bearer Token (`HW_AUTH_TOKEN` cấu hình ở môi trường).
   - Từ chối truy cập `401 Unauthorized` nếu thiếu/sai token.

3. **Bài 3 (Khó) — Phiên bản hóa (Versioning) & Metadata Resource**:
   - Resource `server://info` công bố metadata phiên bản server (`2.0.0`) và chỉ dẫn deprecation.
   - Tool mới `get_order_status_v2` trả về JSON chi tiết, hỗ trợ tham số tùy chọn `include_items`.
   - Client tự động phát hiện phiên bản qua resource metadata và chọn tool tối ưu nhất.

---

## ⚙️ Hướng dẫn cài đặt & Chạy thử nghiệm

### 1. Cài đặt thư viện

Từ thư mục gốc của repository, hãy kích hoạt môi trường ảo `.venv` và đồng bộ thư viện:

```bash
# Kích hoạt venv (Windows)
.venv\Scripts\activate

# Cài đặt các package của bài làm
pip install -r my-mcp-server/requirements.txt
```

### 2. Khởi tạo Cơ sở dữ liệu SQLite

Chạy script để tạo file `sales.db` chứa các bảng và dữ liệu mẫu:

```bash
cd my-mcp-server
$env:PYTHONIOENCODING="utf-8"
python setup_db.py
```

### 3. Kiểm thử tự động bằng Client (HTTP & Auth & Versioning)

**Bước A: Khởi chạy MCP Server ở chế độ HTTP**
Chạy lệnh sau trên Terminal 1:
```bash
cd my-mcp-server
$env:PYTHONIOENCODING="utf-8"
python server.py --http
```
*Server sẽ bắt đầu lắng nghe tại địa chỉ `http://localhost:8090/mcp`.*

**Bước B: Chạy Client Kiểm thử**
Mở một Terminal mới (Terminal 2), kích hoạt `. venv` và chạy:
```bash
cd my-mcp-server
$env:PYTHONIOENCODING="utf-8"
python client.py
```
*Client sẽ kiểm tra tự động cả 2 trường hợp: token sai (bị chặn 401) và token đúng (kết nối thành công, đọc metadata và gọi tool v2).*

---

## 🔌 Tích hợp với Claude Code / Cursor (Chế độ `stdio`)

Để tích hợp công cụ tra cứu đơn hàng này trực tiếp vào **Claude Code** hoặc **Cursor**, bạn chỉ cần chạy server ở chế độ mặc định (`stdio`):

**Đăng ký với Claude Code**:
```bash
claude mcp add sales -- python D:\HT\AI_Vinuni\Lab26\Day26-MCP-Tools-Integration-01960-NguyenThiHuyenTrang\my-mcp-server\server.py
```

Sau khi đăng ký thành công, bạn có thể hỏi Claude Code những câu như:
- *"Check inventory for Laptop"*
- *"What is the status of order OD-101?"*
- *"Show me details of order OD-103"*
