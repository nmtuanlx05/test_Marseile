import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="function")
def driver():
    # Cài đặt tùy chọn cho Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # Khởi tạo WebDriver tự động tải Chrome bản mới nhất
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5) # Chờ ngầm định 5s cho các element
    
    # Trả driver cho các file test sử dụng
    yield driver 
    
    # Đóng trình duyệt sau khi test xong 1 case
    driver.quit()