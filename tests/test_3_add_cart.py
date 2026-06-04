import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestAddToCartMarseille:
    
    def setup_method(self):
        """Khởi tạo trình duyệt trước mỗi Test Case"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = 'http://localhost:5173'

    def teardown_method(self):
        """Tắt trình duyệt sau mỗi Test Case"""
        time.sleep(1.5)
        self.driver.quit()

    # ================= CÁC HÀM TIỆN ÍCH (HELPERS) =================

    def helper_dang_nhap_thanh_cong(self):
        """Tự động đăng nhập ngầm để có token trước khi test Add To Cart"""
        self.driver.get(self.base_url)
        
        sign_in_menu_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space(text())='Sign In']")))
        self.driver.execute_script("arguments[0].click();", sign_in_menu_btn)
        time.sleep(1)
        
        email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "email")))
        password_input = self.driver.find_element(By.ID, "password")
        login_submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'LOGIN')]")
        
        email_input.send_keys("user@gmail.com") # User hợp lệ
        password_input.send_keys("123456")
        self.driver.execute_script("arguments[0].click();", login_submit_btn)
        
        # Chờ Header hiện chữ Hello chứng tỏ đã có token
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Hello:')]")))

    def helper_lay_the_san_pham(self, product_name="10K Yellow Gold"):
        """Tìm chính xác cái áo dựa trên HTML DOM thực tế bạn vừa gửi"""
        self.driver.get(f"{self.base_url}/shop")
        print(f"\n=> Đang chờ hiển thị áo: {product_name}")
        
        # 1. Tìm chính xác cái thẻ div chứa Tên áo
        title_xpath = f"//div[normalize-space(text())='{product_name}']"
        self.wait.until(EC.visibility_of_element_located((By.XPATH, title_xpath)))
        time.sleep(1.5) # Dừng một nhịp cho React render nốt các nút
        
        # 2. Lấy thẻ div CHA bọc cả Tên, Giá, Size và Nút Add To Cart
        # (Chính là cái <div class=""> mà bạn gửi)
        card_wrapper = self.driver.find_element(By.XPATH, f"{title_xpath}/..")
        
        # Cuộn chuột đến giữa áo
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card_wrapper)
        time.sleep(0.5)
        
        return card_wrapper

    def helper_click_add_to_cart(self, card_element):
        """Hàm click Add To Cart bao trúng 100%"""
        print("=> Đang tìm và bấm nút ADD TO CART...")
        
        # Tìm chính xác thẻ <button> nằm TRONG cái thẻ div cha vừa tìm được ở trên
        add_btn = card_element.find_element(By.XPATH, ".//button[normalize-space(text())='ADD TO CART']")
        
        # Sử dụng Javascript để chọc thẳng vào sự kiện click của thẻ button
        self.driver.execute_script("arguments[0].click();", add_btn)


    # ================= DANH SÁCH 6 TEST CASE =================

    def test_tc1_kiem_tra_giao_dien_trang_shop(self):
        """TC_USR_SHP_001: Kiểm tra giao diện hiển thị của trang /shop"""
        self.driver.get(f"{self.base_url}/shop")
        
        # 1. Banner
        banner_title = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[normalize-space(text())='The Classics Make A Comeback']")))
        assert banner_title.is_displayed(), "Lỗi: Không tìm thấy Banner chính!"
        
        # 2. Bộ lọc Default sorting
        sorting_dropdown = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Default sorting')]")
        assert sorting_dropdown.is_displayed(), "Lỗi: Không hiển thị bộ lọc!"
        
        # 3. Đảm bảo sản phẩm có được load ra
        product_cards = self.driver.find_elements(By.XPATH, "//*[normalize-space(text())='ADD TO CART']")
        assert len(product_cards) > 0, "Lỗi: Trang Shop trống trơn, API có thể đang lỗi!"


    def test_tc2_chua_dang_nhap_add_to_cart(self):
        """TC_USR_SHP_002: Thêm giỏ hàng khi CHƯA đăng nhập -> Báo lỗi & Mở form Login"""
        print("\n=> Đang chạy TC2: Lấy thông tin Card sản phẩm...")
        card = self.helper_lay_the_san_pham("10K Yellow Gold")
        
        print("=> Đã cuộn đến sản phẩm. Đang click nút ADD TO CART...")
        self.helper_click_add_to_cart(card)
        
        # Khớp với file React: toast.warning('Please login to use wishlist!');
        # Hoặc toast.warning("Please login to add product to cart!");
        print("=> Đang chờ Toast màu vàng xuất hiện...")
        toast_msg = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Please login')]")))
        assert toast_msg.is_displayed(), "Lỗi: Không hiện Toast yêu cầu đăng nhập!"
        
        # Bắt màn hình Sidebar Login tự động mở ra
        print("=> Đang kiểm tra Sidebar Login...")
        sidebar_login_title = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[normalize-space(text())='SIGN IN']")))
        assert sidebar_login_title.is_displayed(), "Lỗi: Sidebar Login không tự động mở ra!"
        
        print("=> TC2 THÀNH CÔNG!")


    def test_tc3_quen_chon_size_add_to_cart(self):
        """TC_USR_SHP_006: Đã đăng nhập nhưng quên chọn Size -> Báo lỗi"""
        self.helper_dang_nhap_thanh_cong()
        card = self.helper_lay_the_san_pham("10K Yellow Gold")
        
        # Cố tình KHÔNG chọn size, bấm Add luôn
        self.helper_click_add_to_cart(card)
        
        # Bắt Toast vàng nhắc nhở
        toast_msg = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Please choose size')]")))
        assert toast_msg.is_displayed(), "Lỗi: Hệ thống không nhắc nhở khi quên chọn size!"


    def test_tc4_kiem_tra_ui_khi_chon_size(self):
        """TC_USR_SHP_004: Kiểm tra thao tác bôi đậm (active) khi chọn Size M"""
        self.helper_dang_nhap_thanh_cong()
        card = self.helper_lay_the_san_pham("10K Yellow Gold")
        
        size_m = card.find_element(By.XPATH, ".//div[text()='M']")
        
        class_truoc_khi_click = size_m.get_attribute("class")
        self.driver.execute_script("arguments[0].click();", size_m)
        time.sleep(0.5) 
        class_sau_khi_click = size_m.get_attribute("class")
        
        assert class_truoc_khi_click != class_sau_khi_click, "Lỗi: Class CSS của ô Size không hề đổi sau khi bấm!"
        assert len(class_sau_khi_click.split()) > len(class_truoc_khi_click.split()), "Lỗi: Không gắn thêm class Active cho ô Size!"


    def test_tc5_happy_path_add_to_cart(self):
        """TC_USR_SHP_005: Happy Path -> Toast xanh & Sidebar Giỏ hàng trượt ra"""
        self.helper_dang_nhap_thanh_cong()
        card = self.helper_lay_the_san_pham("10K Yellow Gold")
        
        # 1. Chọn Size M
        size_m = card.find_element(By.XPATH, ".//div[text()='M']")
        self.driver.execute_script("arguments[0].click();", size_m)
        
        # 2. Bấm Add To Cart
        self.helper_click_add_to_cart(card)
        
        # 3. Check Toast xanh lá cây báo thành công
        toast_success = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'successfully')]")))
        assert toast_success.is_displayed(), "Lỗi: Add thành công nhưng không có Toast màu xanh!"
        
        # 4. Kiểm tra Sidebar Giỏ hàng tự trượt ra (Xác nhận qua nút CHECKOUT)
        cart_sidebar_checkout_btn = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(., 'CHECKOUT')]")))
        assert cart_sidebar_checkout_btn.is_displayed(), "Lỗi: Sidebar Giỏ hàng không tự động hiện ra!"


    def test_tc6_dong_sidebar_gio_hang(self):
        """TC_USR_SHP_007: Kiểm tra thao tác đóng thanh Sidebar Giỏ hàng"""
        self.helper_dang_nhap_thanh_cong()
        card = self.helper_lay_the_san_pham("10K Yellow Gold")
        
        # Lặp lại thao tác ở TC5 để mở giỏ hàng ra
        size_m = card.find_element(By.XPATH, ".//div[text()='M']")
        self.driver.execute_script("arguments[0].click();", size_m)
        self.helper_click_add_to_cart(card)
        
        # Đợi Sidebar mở hẳn ra
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(., 'CHECKOUT')]")))
        time.sleep(1)
        
        # Click nút đóng [X]
        close_btn = self.driver.find_element(By.XPATH, "//div[contains(@class, 'closeBtn') or contains(@class, 'boxIcon')]")
        self.driver.execute_script("arguments[0].click();", close_btn)
        time.sleep(1)
        
        # Đảm bảo logic xóa class giống hệt tính năng Search
        overlay = self.driver.find_element(By.XPATH, "//div[contains(@class, 'sideBar') or contains(@class, 'sliderSideBar')]")
        current_classes = overlay.get_attribute("class")
        
        assert "open" not in current_classes and "sliderSideBar" not in current_classes, f"Lỗi: Thanh Giỏ Hàng vẫn chưa đóng! (Class thực tế: {current_classes})"