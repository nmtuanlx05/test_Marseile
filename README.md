# 🚀 Marseille E-Commerce - Automation Test Project

Dự án kiểm thử tự động (Automation Testing) cho hệ thống e-commerce Marseille, sử dụng **Python, Selenium WebDriver** và framework **Pytest**. 

Dự án bao phủ các luồng nghiệp vụ cốt lõi của hệ thống:
- Đăng nhập / Đăng xuất người dùng.
- Tìm kiếm sản phẩm (Instant Search với React).
- Thêm sản phẩm vào giỏ hàng (Xử lý UI/UX Frontend).
- Quản lý sản phẩm (Thêm/Sửa/Xóa và Validate form trên trang Admin).

---

## 📋 Yêu cầu hệ thống (Prerequisites)
Trước khi cài đặt, hãy đảm bảo máy tính của bạn đã cài đặt sẵn:
1. **Python 3.8+** (Khuyến nghị Python 3.10 trở lên)
2. **Git**
3. Trình duyệt **Google Chrome**

---

## ⚙️ Hướng dẫn Cài đặt & Chạy dự án (Setup Instructions)

### Bước 1: Clone dự án về máy
Mở Terminal (trên macOS/Linux) hoặc Command Prompt / PowerShell (trên Windows) và chạy lệnh sau:

```bash
git clone [https://github.com/nmtuanlx05/test_Marseille.git](https://github.com/nmtuanlx05/test_Marseille.git)
cd test_Marseille
Bước 2: Khởi tạo Môi trường ảo (Virtual Environment)
Việc sử dụng môi trường ảo giúp tách biệt các thư viện của dự án này với hệ thống máy tính của bạn, tránh xung đột phiên bản.

💻 Đối với Windows:

DOS
python -m venv venv
venv\Scripts\activate
🍎 Đối với macOS / Linux:

Bash
python3 -m venv venv
source venv/bin/activate
(Cài đặt thành công khi bạn thấy chữ (venv) xuất hiện ở đầu dòng lệnh terminal).

Bước 3: Cài đặt các thư viện cần thiết (Requirements)
Dự án yêu cầu các thư viện sau (được liệt kê trong file requirements.txt):

Plaintext
selenium
pytest
pytest-html
webdriver-manager
Đảm bảo bạn đang ở trạng thái kích hoạt (venv). Bạn có thể cài đặt toàn bộ thư viện bằng 1 trong 2 cách sau:

Cách 1: Cài đặt thông qua file requirements.txt (Khuyến nghị)

Bash
pip install -r requirements.txt
Cách 2: Cài đặt trực tiếp qua câu lệnh (Nếu không có file)

Bash
pip install selenium pytest pytest-html webdriver-manager
🚀 Hướng dẫn Chạy Kịch bản Test (Running the Tests)
Dự án sử dụng pytest để thực thi các file test nằm trong thư mục tests/.

1. Chạy TOÀN BỘ các kịch bản test:

Bash
pytest -v
2. Chạy MỘT file test cụ thể (Ví dụ: test trang Admin):

Bash
pytest tests/test_4_add_product_byAdmin.py -v
3. Chạy test và theo dõi từng bước (Hiển thị log):
Thêm cờ -s để terminal in ra các dòng print trong code, giúp bạn dễ dàng theo dõi bot đang thực thi đến bước nào:

Bash
pytest tests/test_4_add_product_byAdmin.py -v -s
4. Xuất Báo Cáo HTML (Test Report):
Nhờ thư viện pytest-html, bạn có thể xuất kết quả test ra file giao diện web cực kỳ trực quan để làm báo cáo:

Bash
pytest -v --html=report.html
Sau khi chạy lệnh trên, hãy mở file report.
