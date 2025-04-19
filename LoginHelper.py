import io
import os
import sys
import base64
import logging
import tempfile
import chromedriver_autoinstaller_max
import ddddocr
import json

from filelock import FileLock
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchWindowException,
    WebDriverException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ENCODING = "utf-8"
SEARCH_PARAM = {
    "id" : By.ID,
    "name" : By.NAME,
    "class_name" : By.CLASS_NAME,
    "xpath" : By.XPATH,
    "css_selector" : By.CSS_SELECTOR,
    "link_text" : By.LINK_TEXT,
}

MAX_ATTEMPTS = 3

def logging_setup():
    """設定日誌紀錄"""
    if getattr(sys, 'frozen', False):
        # 如果是打包後的執行檔，使用執行檔所在目錄
        base_dir = os.path.dirname(sys.executable)
    else:
        # 如果是原始碼執行，使用檔案所在目錄
        base_dir = os.path.dirname(__file__)

    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'selenium.log')

    logging.basicConfig(
        level=logging.ERROR,
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding=ENCODING,
    )
    return log_file

def load_config_file():
    """從外部 JSON 檔案讀取配置"""
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("config.json not found!")
        return {}
    except json.JSONDecodeError:
        logging.error("Failed to parse config.json!")
        return {}

def load_setting():
    """讀取 TronClassBot.json 配置檔案"""
    try:
        with open('TronClassBot.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("TronClassBot.json not found!")
        return {}
    except json.JSONDecodeError:
        logging.error("Failed to parse TronClassBot.json!")
        return {}

def filter_config(config, setting, name):
    """過濾配置檔案，僅保留指定學校的配置"""
    if not config or not setting:
        print("無法載入配置檔案，請檢查日誌檔")
        logging.error("無法載入配置檔案")
        return {}
        
    university = setting.get("university", {})

    if not university:
        print("無法找到學校名稱，請重新設置設定檔")
        logging.error("無法找到學校名稱，請重新設置設定檔")
        return {}
    
    config = config.get(university, {})

    config = config.get(name, {})
    print(f"當前學校: {university}，當前系統: {name}")
    if not config:
        print("無法找到登入系統")
        logging.error("無法找到登入系統")
        return {}
    
    return config

def install_chromedriver():
    """安裝或更新 ChromeDriver 到暫存資料夾，若已安裝過但版本過舊，則重新安裝"""
    import subprocess
    try:
        temp_root = os.path.join(tempfile.gettempdir(), "webdriver")
        os.makedirs(temp_root, exist_ok=True)

        # 取得當前 Chrome 的主版本號
        current_version = chromedriver_autoinstaller_max.get_chrome_version().split('.')[0]
        chromedriver_path = os.path.join(temp_root, current_version, "chromedriver.exe")

        # 檢查是否已經安裝過對應版本的 ChromeDriver
        if os.path.exists(chromedriver_path):
            print("ChromeDriver 已存在，檢查更新...")
            try:
                # 使用 subprocess 執行 chromedriver 並取得版本資訊
                result = subprocess.run(
                    [chromedriver_path, '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                installed_version = result.stdout.split(' ')[1].split('.')[0]
                if installed_version == current_version:
                    print("已安裝最新版本的 ChromeDriver，跳過更新。")
                    return chromedriver_path
                else:
                    print("版本過舊，重新安裝最新版本的 ChromeDriver。")
            except Exception as e:
                print(f"無法檢查已安裝的 ChromeDriver 版本: {e}")

        # 安裝最新的 ChromeDriver
        lock_path = os.path.join(temp_root, "webdriver.lock")
        with FileLock(lock_path):
            chromedriver_autoinstaller_max.install(path=temp_root)
            if not os.path.exists(chromedriver_path):
                raise FileNotFoundError("安裝後仍找不到 chromedriver.exe")
        
        return chromedriver_path
    
    except Exception as e:
        logging.error(f"安裝 ChromeDriver 時發生錯誤: {e}")
        return None

def get_chrome_options():
    """設定 Chrome 選項"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-animations")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-print-preview")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--disable-smooth-scrolling")
    options.add_argument("--disable-sync")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-web-security')
    options.add_argument('--lang=zh-TW')
    # options.add_argument("--window-size=600,400")
    options.add_argument("--start-maximized")

    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "translate": {"enabled": False}
    })

    options.add_experimental_option("detach", True)
    options.page_load_strategy = 'eager'
    options.unhandled_prompt_behavior = "accept"

    return options

def get_args():
    """取得命令列參數"""
    if len(sys.argv) < 1:
        print("發生錯誤，請檢查日誌檔")
        logging.error("命令列參數不足")
        sys.exit(1)

    return sys.argv[1]

def decode_password(encoded_password):
    """解碼 Base64 編碼的密碼"""
    try:
        return base64.b64decode(encoded_password).decode("utf-8") if encoded_password else ""
    except Exception as e:
        logging.error(f"Failed to decode password: {e}")
        return ""

def get_user_credentials(**kwargs):
    """從配置中獲取使用者憑證"""
    config = kwargs.get("config")
    if not config:
        logging.error("No configuration provided to get_user_credentials.")
        return "", ""
    
    username = config.get("username", "")
    password = decode_password(config.get("password", ""))
    return username, password

class LoginHelper:
    """登入輔助類別"""
    def __init__(self, **kwargs):
        """初始化登入類別"""
        self.driver = kwargs.get("driver")
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.config = kwargs.get("config")


    def get_url(self):
        """獲取登入網址"""

        url = self.config.get("url", "")
        if not url:
            logging.error("沒有提供登入網址")
            return None
        
        return url
    
    def get_redirect_url(self):
        """獲取重定向網址"""
        redirect_url = self.config.get("redirect_url", "")
        if not redirect_url:
            logging.error("沒有提供重定向網址")
            return None
        
        return redirect_url

    def redirect(self, url):
        """重定向到登入頁面"""
        print("重定向到登入頁面...")
        try:
            self.driver.get(url)
        except Exception as e:
            logging.error(f"無法重導向: {e}")
            print("發生錯誤，請檢查日誌檔")
            return False

    def get_captcha_text(self, captcha_image, encoding):
        """辨識驗證碼"""
        try:
            if encoding == "base64":
                ddddocr_client = ddddocr.DdddOcr()
                captcha_image_base64 = captcha_image.get_attribute("src").split(",")[1]
                captcha_image_data = base64.b64decode(captcha_image_base64)
                captcha_text = ddddocr_client.classification(captcha_image_data)
            elif encoding == "image":
                ddddocr_client = ddddocr.DdddOcr()
                captcha_image_data = captcha_image.screenshot_as_png
                captcha_text = ddddocr_client.classification(captcha_image_data)

        except Exception as e:
            logging.error(f"驗證碼辨識失敗: {e}")
            print("驗證碼辨識失敗，請檢查日誌檔")
            captcha_text = ""
        return captcha_text
    
    def process_captcha(self, captcha_config: dict) -> bool:
        """處理驗證碼並填入"""
        try:
            captcha_length = captcha_config.get("length", "")
            captcha_field = self.get_field("captcha_field", config=captcha_config)
            captcha_image = self.get_field("captcha_image", config=captcha_config)
            image_encoding = captcha_config.get("captcha_image", {}).get("encoding", "base64")

            for attempt in range(MAX_ATTEMPTS):
                print(f"驗證碼辨識嘗試 {attempt + 1}/{MAX_ATTEMPTS}...")
                captcha_text = self.get_captcha_text(captcha_image, encoding=image_encoding)
                print(f"辨識的驗證碼: {captcha_text}")

                if captcha_length and captcha_length != len(captcha_text):
                    print("圖形驗證碼長度不符，重新嘗試...")
                    logging.debug("圖形驗證碼長度不符，重新嘗試...")
                    captcha_image.click()  # 重新載入驗證碼
                    continue

                self.send_keys(captcha_field, captcha_text)
                return True

            print("驗證碼辨識失敗，請檢查日誌檔")
            logging.error("驗證碼辨識失敗")
            return False
        except Exception as e:
            logging.error(f"處理驗證碼時發生錯誤: {e}")
            return False
    
    def find_element(self, by, value):
        """尋找元素"""
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, value))
            )
        except (NoSuchWindowException, WebDriverException) as e:
            logging.error(f"無法找到元素: {e}")
            print("發生錯誤，請檢查日誌檔")
            return None
        
    def get_field(self, field, config = None):
        """獲取輸入欄位"""
        try:
            if config is None:
                field = self.config.get(field, {})
                element = self.find_element(SEARCH_PARAM.get(field.get("by"), By.ID), field.get("value"))
                if element is None:
                    raise ValueError(f"無法找到元素: {field}")
                return element
            else:
                field = config.get(field, {})
                element = self.find_element(SEARCH_PARAM.get(field.get("by"), By.ID), field.get("value"))
                if element is None:
                    raise ValueError(f"無法找到元素: {field}")
                return element
        except (NoSuchWindowException, WebDriverException) as e:
            logging.error(f"無法獲取輸入欄位: {e}")
            print("發生錯誤，請檢查日誌檔")
            return None
    
    def send_keys(self, element, keys):
        """發送鍵入事件"""
        try:
            if element is not None:
                element.clear()
            element.send_keys(keys)
        except (NoSuchWindowException, WebDriverException) as e:
            logging.error(f"無法發送鍵入事件: {e}")
            print("發生錯誤，請檢查日誌檔")
            return False
        
    def vaildate_login(self):
        """驗證登入是否成功"""
        vaild = self.config.get("vaild", {})
        mode = vaild.get("mode", "")

        if mode == "find_element":
            if "error" in vaild:
                error = vaild.get("error", {})
                text = error.get("text", "")
                try:
                    element = WebDriverWait(self.driver, 0.2).until(
                        EC.presence_of_element_located((SEARCH_PARAM.get(vaild.get("by"), By.ID), vaild.get("value", "")))
                    )

                    print(f"尋找元素: {element.text}")

                    if text in element.text:
                        return False
                except TimeoutException:
                    element = None
                    return True
                
        elif mode == "not_find_element":
            try:
                element = WebDriverWait(self.driver, 0.2).until(
                    EC.presence_of_element_located((SEARCH_PARAM.get(vaild.get("by"), By.ID), vaild.get("value", "")))
                )
                
                return True
            except TimeoutException:
                element = None
                return False
        return False
    
    def login(self) -> bool:
        """執行登入操作"""
        try:
            self.redirect(url=self.get_url())

            username_field = self.get_field("username_field")
            password_field = self.get_field("password_field")
            login_button = self.get_field("login_button")

            captcha_config = self.config.get("captcha", {})
            if captcha_config.get("vaildate", False):
                if not self.process_captcha(captcha_config):
                    return False

            self.send_keys(username_field, self.username)
            self.send_keys(password_field, self.password)
            print("正在登入...")

            login_delay = self.config.get("login_delay", 0)
            if login_delay > 0:
                print(f"登入延遲: {login_delay} 秒")
                logging.debug(f"登入延遲: {login_delay} 秒")
                self.driver.implicitly_wait(login_delay)

            login_button.click()
            return True
        except Exception as e:
            logging.error(f"登入過程中發生錯誤: {e}")
            print("發生錯誤，請檢查日誌檔")
            return False

def main():
    """主程式"""
    logging_setup()
    try:
        if not getattr(sys, 'frozen', False):  # 檢查是否為打包環境
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=ENCODING)
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=ENCODING)
        else:
            logging.error("無法重新包裝 sys.stdout 或 sys.stderr")
    except Exception as e:
        logging.error(f"無法重新包裝 sys.stdout 或 sys.stderr: {e}")
    try:
        name = get_args()
        config = load_config_file()
        setting = load_setting()

        config = filter_config(config, setting, name)
        if not config:
            return

        username, password = get_user_credentials(config=setting)
        chromedriver_path = install_chromedriver()
        options = get_chrome_options()

        driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
        login_helper = LoginHelper(driver=driver, username=username, password=password, config=config)

        for attempt in range(MAX_ATTEMPTS):
            print(f"登入嘗試 {attempt + 1}/{MAX_ATTEMPTS}...")
            if login_helper.login() and login_helper.vaildate_login():
                print("登入成功")
                redirect_url = login_helper.get_redirect_url()
                if redirect_url:
                    login_helper.redirect(url=redirect_url)
                else:
                    print("不須重新導向")
                break
            else:
                print("登入失敗")
        else:
            print("多次登入嘗試失敗，請檢查日誌檔")
    except Exception as e:
        logging.error(f"主程式執行時發生錯誤: {e}")
        print("發生錯誤，請檢查日誌檔")

if __name__ == "__main__":
    main()
