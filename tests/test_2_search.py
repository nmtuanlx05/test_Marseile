import pytest
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestProductSearchMarseille:
    
    def setup_method(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = 'http://localhost:5173/'

    def teardown_method(self):
        time.sleep(1)
        self.driver.quit()

    def mo_overlay_search(self):
        """Mở trang chủ và bật màn hình Tìm kiếm"""
        self.driver.get(self.base_url)
        
        # Click nút Search trên Header
        search_menu_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space(text())='Search']")))
        self.driver.execute_script("arguments[0].click();", search_menu_btn)
        
        # Chờ animation overlay trượt ra
        time.sleep(1)
        
        # Ánh xạ ô input tìm kiếm
        self.search_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search for products...']")))


    # ================= 5 TEST CASE CHÍNH =================

    def test_tc1_kiem_tra_giao_dien_popup_search(self):
        """TC_USR_SRC_001: Kiểm tra hiển thị giao diện Popup/Overlay Tìm kiếm toàn màn hình"""
        self.mo_overlay_search()
        
        close_btn = self.driver.find_element(By.XPATH, "//div[contains(@class, 'closeBtn')]")
        title_element = self.driver.find_element(By.XPATH, "//h2[normalize-space(text())='What Are You Looking For?']")
        dropdown = self.driver.find_element(By.XPATH, "//select")
        search_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'SEARCH')]")
        popular_title = self.driver.find_element(By.XPATH, "//h3[normalize-space(text())='Popular Categories']")
        view_all_btn = self.driver.find_element(By.XPATH, "//button[normalize-space(text())='VIEW ALL CATEGORIES']")
        card_men = self.driver.find_element(By.XPATH, "//p[normalize-space(text())='MEN']")
        
        assert close_btn.is_displayed(), "Thiếu nút Đóng [X]"
        assert title_element.is_displayed(), "Thiếu tiêu đề chính"
        assert self.search_input.is_displayed(), "Thiếu ô nhập từ khóa"
        assert dropdown.is_displayed(), "Thiếu Dropdown Categories"
        assert search_btn.is_displayed(), "Thiếu nút SEARCH"
        assert popular_title.is_displayed(), "Thiếu Popular Categories"
        assert view_all_btn.is_displayed(), "Thiếu nút VIEW ALL CATEGORIES"
        assert card_men.is_displayed(), "Thiếu thẻ danh mục MEN"


    def test_tc2_tim_kiem_san_pham_hop_le_tu_dong(self):
        """TC_USR_SRC_002: Kiểm tra tính năng Instant Search (Tự động hiển thị kết quả khi gõ)"""
        self.mo_overlay_search()
        
        keyword = "10k"
        
        # Dùng ActionChains gõ phím
        actions = ActionChains(self.driver)
        actions.move_to_element(self.search_input)\
               .click()\
               .pause(0.5)\
               .send_keys(keyword)\
               .perform()
        
        # TỐI ƯU HÓA: KHÔNG TÌM BẰNG TEXT NỮA!
        # Dựa vào code React: <p className={styles.countText}>
        # Lệnh này sẽ tóm ngay lập tức thẻ p chứa class 'countText' ngay khi API load xong
        count_text = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p[class*='countText']")))
        
        # (Nâng cao) Tìm tất cả các thẻ Card sản phẩm để đảm bảo data thực sự đã được vẽ ra màn hình
        product_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='resultsArea'] div[class*='item']")
        
        assert count_text.is_displayed(), "Lỗi: Instant Search chạy nhưng không hiện thẻ báo số lượng sản phẩm!"
        assert len(product_cards) > 0, f"Lỗi: Có chữ báo số lượng, nhưng Card sản phẩm lại bị rỗng!"
        
        # In ra log để bạn kiểm chứng tool đã "nhìn thấy" thành công
        print(f"\n-> Báo cáo TC2: Đã tóm được text '{count_text.text}' và render được {len(product_cards)} sản phẩm!")
    
    def test_tc3_tim_kiem_tu_khoa_khong_ton_tai_tu_dong(self):
        """TC_USR_SRC_007: Tìm kiếm từ khóa sai (Tự động hiển thị thông báo lỗi)"""
        self.mo_overlay_search()
        
        # 1. Gõ chuỗi không tồn tại
        invalid_keyword = "NotExist"
        
        # Dùng ActionChains mô phỏng người thật gõ phím để kích hoạt React onChange
        actions = ActionChains(self.driver)
        actions.move_to_element(self.search_input)\
               .click()\
               .pause(0.5)\
               .send_keys(invalid_keyword)\
               .perform()
        
        # 2. KHÔNG CLICK BUTTON. Đứng chờ React render ra thông báo.
        # TỐI ƯU HÓA: Dựa vào code FE <p className={styles.noResult}> 
        # Bắt thẳng class chứa chữ 'noResult' để bỏ qua lỗi vỡ text của XPath
        no_result = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p[class*='noResult']")))
        
        assert no_result.is_displayed(), "Lỗi: Không hiển thị thông báo 'No products found.' khi gõ từ khóa rác."
        
        # In ra log để xác nhận tool đã đọc thành công
        print(f"\n-> Báo cáo TC3: Đã tìm thấy thông báo '{no_result.text}'")

    def test_tc4_dong_man_hinh_tim_kiem(self):
        """TC_USR_SRC_004: Kiểm tra tính năng đóng màn hình tìm kiếm overlay"""
        # Mở màn hình tìm kiếm lên trước
        self.mo_overlay_search()
        
        # 1. Tìm và bấm nút Đóng [X]
        close_btn = self.driver.find_element(By.XPATH, "//div[contains(@class, 'closeBtn')]")
        self.driver.execute_script("arguments[0].click();", close_btn)
        
        # 2. Dừng cứng 1 giây để chờ hiệu ứng CSS trượt màn hình lên trên hoàn tất
        time.sleep(1) 
        
        # 3. Bắt lấy cái khung chứa nội dung tìm kiếm
        overlay = self.driver.find_element(By.XPATH, "//div[contains(@class, 'slideContainer')]")
        
        # 4. Rút xuất toàn bộ chuỗi class đang gắn trên khung này tại thời điểm hiện tại
        current_classes = overlay.get_attribute("class")
        
        # 5. Khẳng định (Assert): Class 'open' bắt buộc phải bị React gỡ bỏ đi
        assert "open" not in current_classes, f"Lỗi: Màn hình chưa đóng, class vẫn chứa 'open'. Class thực tế đang là: {current_classes}"
        
        # In ra Terminal để bạn nhìn thấy tận mắt class đã bị đổi
        print(f"\n-> Báo cáo TC4: Màn hình đã đóng thành công! (Class sau khi đóng chỉ còn: {current_classes})")


    def test_tc5_dieu_huong_nut_view_all(self):
        """TC_USR_SRC_006: Kiểm tra điều hướng nút Xem tất cả danh mục"""
        self.mo_overlay_search()
        old_url = self.driver.current_url
        
        view_all_btn = self.driver.find_element(By.XPATH, "//button[normalize-space(text())='VIEW ALL CATEGORIES']")
        self.driver.execute_script("arguments[0].click();", view_all_btn)
        
        try:
            self.wait.until(EC.url_changes(old_url))
            assert self.driver.current_url != old_url
        except:
            pytest.fail("Lỗi: Nút VIEW ALL CATEGORIES không điều hướng trang.")


    