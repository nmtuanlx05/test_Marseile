import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestAdminProducts:
    
    def setup_method(self):
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = 'http://localhost:5173'

    def teardown_method(self):
        time.sleep(1)
        self.driver.quit()

    # ================= HELPERS =================

    def helper_login_admin(self):
        """Giả lập đăng nhập Admin qua Sidebar từ trang chủ"""
        # 1. Truy cập vào trang chủ trước
        self.driver.get(self.base_url)
        time.sleep(1) # Đợi trang web load xong
        
        # 2. Bấm nút Sign In trên thanh Header để mở Sidebar
        sign_in_menu_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space(text())='Sign In']")))
        self.driver.execute_script("arguments[0].click();", sign_in_menu_btn)
        time.sleep(1) # Chờ Sidebar trượt ra
        
        # 3. Điền thông tin tài khoản Admin
        email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "email")))
        password_input = self.driver.find_element(By.ID, "password")
        login_submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'LOGIN')]")
        
        email_input.send_keys("admin1@gmail.com")
        password_input.send_keys("123456")
        self.driver.execute_script("arguments[0].click();", login_submit_btn)
        
        # 4. Chờ đăng nhập thành công (Có chữ Hello trên Header)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Hello')]")))
        
        # 5. Sau khi trình duyệt đã lưu Token (Cookies), giờ mới chuyển hướng vào khu vực Admin
        print("\n=> Đăng nhập Admin thành công. Đang truy cập trang Quản lý Sản phẩm...")
        self.driver.get(f"{self.base_url}/admin/products")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[text()='Manage Products']")))

    def helper_clear_react_input(self, element):
        """Xóa trắng input của React chuẩn nhất bằng phím tắt"""
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)


    # ================= TEST CASES =================

    def test_tc1_kiem_tra_ui_trang_admin(self):
        """TC_ADM_001: Kiểm tra UI trang Quản lý Sản phẩm"""
        self.helper_login_admin()
        
        # Nút Add New Product phải hiển thị
        add_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '+ Add New Product')]")
        assert add_btn.is_displayed(), "Lỗi: Mất nút Thêm mới sản phẩm!"
        
        # Kiểm tra có bảng danh sách
        table = self.driver.find_element(By.TAG_NAME, "table")
        assert table.is_displayed(), "Lỗi: Không hiển thị bảng sản phẩm!"


    def test_tc2_validate_form_rong_va_sai_dinh_dang(self):
        """TC_ADM_002 & 003: Kiểm tra bộ Validate cực mạnh của Form"""
        self.helper_login_admin()
        
        # Bấm nút Add New Product để mở form
        add_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '+ Add New Product')]")))
        self.driver.execute_script("arguments[0].click();", add_btn)
        time.sleep(1)  # Chờ form load
        
        # Ánh xạ các ô input 
        name_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "name")))
        price_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "price")))
        type_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "type")))
        material_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "material")))  # FIX: Thêm material
        sku_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "sku")))
        
        print("\n=> Đang nhập dữ liệu sai để kích hoạt Validate...")
        
        # 1. Tên quá ngắn
        name_input.click()
        name_input.send_keys("ab")
        
        # 2. Giá âm
        price_input.click()
        price_input.send_keys("-50")
        
        # 3. Type quá ngắn
        type_input.click()
        type_input.send_keys("x")
        
        # 4. Material quá ngắn hoặc trống (FIX: Thêm test material)
        material_input.click()
        material_input.send_keys("a")  # Quá ngắn
        
        # 5. SKU sai định dạng
        sku_input.click()
        sku_input.send_keys("sp_loi_01")
        
        # Click ra ngoài để ép React hiển thị lỗi màu đỏ
        self.driver.find_element(By.XPATH, "//h3").click()
        
        print("=> Đang dừng 3 giây để mọi người quan sát lỗi Validate trên màn hình...")
        time.sleep(3) 
        
        print("=> Đang kiểm tra hệ thống bắt lỗi (Assertions)...")
        
        # --- KIỂM TRA THÔNG BÁO LỖI ---
        name_error = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'ít nhất 3 ký tự')]")))
        assert name_error.is_displayed(), "Lỗi: Không báo lỗi tên quá ngắn!"
        
        price_error = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Giá phải lớn hơn 0')]")))
        assert price_error.is_displayed(), "Lỗi: Không báo lỗi giá âm!"
        
        sku_error = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'SKU chỉ được chứa chữ hoa')]")))
        assert sku_error.is_displayed(), "Lỗi: Không báo lỗi sai Regex SKU!"
        
        # =========================================================
        # FIX LỖI Ở ĐÂY: QUÉT LẠI NÚT SUBMIT ĐỂ CẬP NHẬT TRẠNG THÁI
        # =========================================================
        submit_btn_updated = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and contains(., 'Save Product')]"))
        )
        
        # Kiểm tra qua thuộc tính 'disabled' sinh ra từ React
        is_disabled_attr = submit_btn_updated.get_attribute("disabled")
        
        # Check xem nếu attr là 'true' hoặc is_enabled() là False thì Pass
        is_locked = (is_disabled_attr == "true") or (not submit_btn_updated.is_enabled())
        
        assert is_locked, "Lỗi Nghiêm Trọng: Có lỗi Validate nhưng nút Save vẫn bấm được!"
        print("=> TC2 THÀNH CÔNG: Bộ Validate hoạt động xuất sắc, nút Save đã bị khóa!")


    def test_tc3_them_san_pham_happy_path(self):
        """TC_ADM_004: Thêm sản phẩm thành công - Điền ĐỦ tất cả required fields"""
        self.helper_login_admin()
        
        # Bấm nút Add New Product
        add_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '+ Add New Product')]")))
        self.driver.execute_script("arguments[0].click();", add_btn)
        time.sleep(1)  # Chờ form load
        
        # FIX: Điền tất cả required fields theo đúng thứ tự từ form
        # 1. Product Name
        name_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "name")))
        name_input.send_keys("Áo Khoác Selenium")
        
        # 2. Price
        price_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "price")))
        price_input.send_keys("150")
        
        # 3. Type
        type_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "type")))
        type_input.send_keys("Jacket")
        
        # 4. Material (FIX: Thêm field material - bắt buộc!)
        material_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "material")))
        material_input.send_keys("Cotton")
        
        # 5. SKU
        sku_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "sku")))
        sku_input.send_keys("SELE-001")
        
        # 6. Image links (FIX: Thêm field ảnh - có thể bắt buộc)
        images_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "imagesString")))
        images_input.send_keys("https://example.com/image1.jpg, https://example.com/image2.jpg")
        
        # 7. Description (FIX: Thêm field mô tả)
        desc_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "description")))
        desc_input.send_keys("Áo khoác chất lượng cao, thoáng mát, phù hợp cho mọi mùa")
        
        # 8. Điền Size & Quantity
        size_inputs = self.wait.until(lambda driver: len(driver.find_elements(By.XPATH, "//input[@placeholder='Size (S, M...)']")) > 0)
        size_inputs = self.driver.find_elements(By.XPATH, "//input[@placeholder='Size (S, M...)']")
        qty_inputs = self.driver.find_elements(By.XPATH, "//input[@placeholder='Số lượng']")
        
        self.helper_clear_react_input(size_inputs[0])
        size_inputs[0].send_keys("XL")
        self.helper_clear_react_input(qty_inputs[0])
        qty_inputs[0].send_keys("50")
        
        time.sleep(0.5)  # Chờ React update state
        
        # Submit form
        submit_btn = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//button[@type='submit' and contains(., 'Save Product')]"))
        )
        self.driver.execute_script("arguments[0].click();", submit_btn)
        
        time.sleep(1)  # Chờ API response
        
        # Xử lý Popup Alert của Trình duyệt (window.alert)
        alert = self.wait.until(EC.alert_is_present())
        assert "Thêm sản phẩm mới thành công" in alert.text, "Lỗi: Alert báo thêm thất bại!"
        alert.accept() # Bấm OK trên Alert


    def test_tc4_chinh_sua_san_pham(self):
        """TC_ADM_005: Chỉnh sửa sản phẩm và lưu lại"""
        self.helper_login_admin()
        
        # Bấm nút Edit ở sản phẩm ĐẦU TIÊN trong bảng
        edit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(@class, 'edit')])[1]")))
        self.driver.execute_script("arguments[0].click();", edit_btn)
        
        # Đợi form mở ra, sửa Giá sản phẩm
        price_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "price")))
        self.helper_clear_react_input(price_input)
        price_input.send_keys("999")
        
        # Bấm Update
        self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Update')]").click()
        
        # Xử lý Alert
        alert = self.wait.until(EC.alert_is_present())
        assert "Cập nhật sản phẩm thành công" in alert.text, "Lỗi: Không hiện Alert cập nhật thành công!"
        alert.accept()


    def test_tc5_xoa_san_pham(self):
        """TC_ADM_006: Xóa sản phẩm và test Window Confirm"""
        self.helper_login_admin()
        
        # Lấy số lượng hàng trong bảng trước khi xóa
        rows_before = len(self.driver.find_elements(By.XPATH, "//tbody/tr"))
        
        # Bấm nút Delete ở sản phẩm ĐẦU TIÊN
        delete_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(@class, 'delete')])[1]")))
        self.driver.execute_script("arguments[0].click();", delete_btn)
        
        # Xử lý window.confirm
        alert = self.wait.until(EC.alert_is_present())
        assert "Bạn chắc chắn muốn xóa" in alert.text, "Lỗi: Sai thông báo Confirm Xóa!"
        alert.accept() # Bấm OK
        
        time.sleep(1) # Chờ gọi API xóa và reload bảng
        
        # Đếm lại số hàng
        rows_after = len(self.driver.find_elements(By.XPATH, "//tbody/tr"))
        assert rows_after < rows_before, "Lỗi: Số lượng sản phẩm không giảm đi sau khi xóa!"
