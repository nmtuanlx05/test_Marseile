import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestUserLoginMarseille:
    
    def setup_method(self):
        """Hàm này sẽ tự động chạy TRƯỚC MỖI test case để khởi tạo trình duyệt"""
        options = Options()
        options.add_argument("--start-maximized")
        # Bùa hộ mệnh chống tràn RAM trên Linux
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = 'http://localhost:5173/'

    def teardown_method(self):
        """Hàm này sẽ tự động chạy SAU MỖI test case để tắt trình duyệt"""
        time.sleep(1.5) # Dừng một chút để kịp nhìn kết quả
        self.driver.quit()

    def mo_popup_dang_nhap(self):
        """Hàm dùng chung (Helper): Mở web và bật popup đăng nhập"""
        self.driver.get(self.base_url)
        
        # Mở Sidebar bằng JavaScript để xuyên qua mọi animation
        sign_in_menu_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[normalize-space(text())='Sign In']")))
        self.driver.execute_script("arguments[0].click();", sign_in_menu_btn)
        time.sleep(1) # Chờ sidebar trượt ra
        
        # Bắt sẵn các element (thẻ HTML) của Form
        self.email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "email")))
        self.password_input = self.driver.find_element(By.ID, "password")
        self.login_submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' and normalize-space(text())='LOGIN']")


    # ================= DANH SÁCH CÁC TEST CASE =================

    def test_tc1_kiem_tra_giao_dien_sidebar_login(self):
        """TC1: Kiểm tra sự kiện bật Sidebar Login và tính toàn vẹn của giao diện form"""
        # 1. Truy cập trang chủ
        self.driver.get(self.base_url)
        
        # 2. Thực hiện hành động: Click nút Sign In trên Menu
        sign_in_menu_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[normalize-space(text())='Sign In']")))
        self.driver.execute_script("arguments[0].click();", sign_in_menu_btn)
        
        # Chờ 1 giây để hiệu ứng animation trượt Sidebar của React hoàn tất
        time.sleep(1)
        
        # 3. KẾT QUẢ MONG ĐỢI (ASSERTIONS)
        # Kiểm tra Sidebar đã trượt ra thành công (nhận diện qua Title SIGN IN)
        title_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[normalize-space(text())='SIGN IN']")))
        assert title_element.is_displayed(), "Lỗi: Sidebar Login không hiện ra hoặc thiếu Tiêu đề 'SIGN IN'"
        
        # Kiểm tra sự xuất hiện của Form (Email, Password)
        email_input = self.driver.find_element(By.ID, "email")
        assert email_input.is_displayed(), "Lỗi: Giao diện Sidebar thiếu ô nhập Email"
        
        password_input = self.driver.find_element(By.ID, "password")
        assert password_input.is_displayed(), "Lỗi: Giao diện Sidebar thiếu ô nhập Password"
        
        # Kiểm tra nút submit LOGIN
        login_submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' and normalize-space(text())='LOGIN']")
        assert login_submit_btn.is_displayed(), "Lỗi: Giao diện Sidebar thiếu nút LOGIN màu đen"
        
        # Kiểm tra nút chuyển đổi sang giao diện Đăng ký
        register_toggle_btn = self.driver.find_element(By.XPATH, "//button[normalize-space(text())='Don`t have an account']")
        assert register_toggle_btn.is_displayed(), "Lỗi: Giao diện Sidebar thiếu nút chuyển sang trang Đăng ký"


    def test_tc2_dang_nhap_thanh_cong(self):
        """TC2: Đăng nhập thành công với tài khoản hợp lệ"""
        self.mo_popup_dang_nhap()
        
        self.email_input.send_keys("user@gmail.com")
        self.password_input.send_keys("123456")
        self.driver.execute_script("arguments[0].click();", self.login_submit_btn)
        
        # Xác nhận: Chờ chuyển trang và tìm chữ Hello trên thanh Header
        hello_text = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Hello: user@gmail.com')]")))
        assert hello_text.is_displayed()


    def test_tc3_bo_trong_email(self):
        """TC3: Bỏ trống trường Email (Check Yup Validation)"""
        self.mo_popup_dang_nhap()
        
        self.email_input.send_keys("")
        self.password_input.send_keys("123456")
        self.driver.execute_script("arguments[0].click();", self.login_submit_btn)
        
        # Xác nhận: Yup Formik bắt lỗi tại giao diện
        yup_error = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[normalize-space(text())='Email is required']")))
        assert yup_error.is_displayed()


    def test_tc4_bo_trong_password(self):
        """TC4: Bỏ trống trường Mật khẩu (Check Yup Validation)"""
        self.mo_popup_dang_nhap()
        
        self.email_input.send_keys("user@gmail.com")
        self.password_input.send_keys("")
        self.driver.execute_script("arguments[0].click();", self.login_submit_btn)
        
        # Xác nhận:
        yup_error = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[normalize-space(text())='Password is required']")))
        assert yup_error.is_displayed()


    def test_tc5_sai_dinh_dang_email(self):
        """TC5: Nhập sai định dạng Email (Check Yup Validation)"""
        self.mo_popup_dang_nhap()
        
        self.email_input.send_keys("tuangmail.com") # Thiếu @
        self.password_input.send_keys("123456")
        self.driver.execute_script("arguments[0].click();", self.login_submit_btn)
        
        # Xác nhận:
        yup_error = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[normalize-space(text())='Invalid email']")))
        assert yup_error.is_displayed()


    def test_tc6_mat_khau_sai_dinh_dang(self):
        """TC6: Nhập mật khẩu không đúng định dạng (Nhỏ hơn 6 ký tự)"""
        self.mo_popup_dang_nhap()
        
        self.email_input.send_keys("user@gmail.com")
        self.password_input.send_keys("12345") # Chỉ có 5 ký tự
        self.driver.execute_script("arguments[0].click();", self.login_submit_btn)
        
        # Xác nhận:
        yup_error = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[normalize-space(text())='Password must be at least 6 characters']")))
        assert yup_error.is_displayed()


    def test_tc7_tai_khoan_chua_dang_ky(self):
        """TC7: Nhập Email và Mật khẩu chưa đăng ký (Check Backend Toastify Error)"""
        self.mo_popup_dang_nhap()
        
        self.email_input.send_keys("chua_dang_ky_123@gmail.com")
        self.password_input.send_keys("matkhaunao_do_456")
        self.driver.execute_script("arguments[0].click();", self.login_submit_btn)
        
        # Chờ Backend chạy xong (Trạng thái nút thoát khỏi chữ LOADING...)
        self.wait.until(EC.text_to_be_present_in_element((By.XPATH, "//button[@type='submit']"), "LOGIN"))
        
        # Xác nhận: Component Toast của React phải hiện lên để báo lỗi
        toast_element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".Toastify__toast")))
        assert toast_element.is_displayed()