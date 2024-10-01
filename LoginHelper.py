from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from PIL import Image
import ddddocr
import base64
import io
import requests

class LoginHelper():
    def __init__(self, username, password, current):
        # 初始化 Chrome 瀏覽器
        self.driver = None
        self.url = {
            "ulearn" : r"https://identity.nfu.edu.tw/auth/realms/nfu/protocol/cas/login?ui_locales=zh-TW&service=https%3A//ulearn.nfu.edu.tw/login%3Fnext%3D/user/index&locale=zh_TW&ts=1727781519.447133",
            "ecare" : r"https://ecare.nfu.edu.tw/",
            "mail2000" : "https://mail.nfu.edu.tw/cgi-bin/login?index=1",
            "工讀平台" : "https://sw.nfu.edu.tw/"
            }
        self.username = username
        self.password = password
        self.current = current
        self.start_browser()
        # 避免瀏覽器自動關閉
        input()
        self.close_browser()

    def start_browser(self):
        """
        啟動 Chrome driver，並根據current的值執行該系統腳本
        """
        # 使用 WebDriver Manager 自動安裝或更新 ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

        # 自動最大化瀏覽器窗大小
        self.driver.maximize_window()

        # 打開目標網站
        self.driver.get(self.url[self.current])

        # 根據current決定執行腳本
        if self.current == "ulearn":
            self.ulearn()
        elif self.current == "ecare":
            self.ecare()
        elif self.current == "mail2000":
            self.mail2000()
        elif self.current == "工讀平台":
            self.study_work()

    def ulearn(self):
        """
        登錄到ulearn系統
        """

        # 使用者帳號輸入
        username_input = self.driver.find_element(By.ID, "username")
        username_input.send_keys(self.username)

        # 密碼輸入
        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(self.password)

        # 辨識驗證碼，找到含有驗證碼圖片的元素，轉換為圖片檔並執行辨識函式
        captcha_input = self.driver.find_element(By.ID, "captchaCode")
        captcha_img = self.driver.find_element(By.CLASS_NAME, "captcha-image")
        img_base64 = captcha_img.get_attribute("src").split(",")[1]
        img_data = base64.b64decode(img_base64)
        captcha_text = self.get_captcha_text(img_data)
        captcha_input.send_keys(captcha_text)

        # 按下Enter鍵登入
        password_input.send_keys(Keys.RETURN)

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "info_group"))
            )
            # 如果出現 class="info_group"，則認為驗證碼錯誤，需要重新輸入
            self.ulearn()
        except:
            return

    def ecare(self):
        """
        登錄到ecare系統
        """
        # 使用者帳號輸入
        username_input = self.driver.find_element(By.ID, "login_acc")
        username_input.send_keys(self.username)

        # 密碼輸入
        password_input = self.driver.find_element(By.ID, "login_pwd")
        password_input.send_keys(self.password)

        # 驗證碼處理
        captcha_input = self.driver.find_element(By.ID, "login_chksum")
        img_data = self.get_captcha_img()
        captcha_text = self.get_captcha_text(img_data)
        captcha_input.send_keys(captcha_text)
        password_input.send_keys(Keys.RETURN)

        try:
            # 使用 xpath 查找包含「回首頁」的元素
            alert = self.driver.switch_to.alert
            alert.accept()
            username_input.clear()
            password_input.clear()
            captcha_input.clear()
            self.ecare()
        except NoAlertPresentException:
            WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '回首頁')]"))
                )
            self.driver.get(self.url["ecare"])
            self.ecare()
        finally:
            return

    def mail2000(self):
        """
        mail2000信箱登入
        """
        # 先定位出輸入框表單
        form = self.driver.find_element(By.ID, "stdLogin")

        # 使用者帳號輸入
        username_input = form.find_element(By.NAME, "USERID")
        username_input.send_keys(self.username)

        # 使用者密碼輸入
        password_input = form.find_element(By.NAME, "PASSWD")
        password_input.send_keys(self.password)

        # 驗證碼處理
        captcha_input = form.find_element(By.NAME, "CaptAns")
        captcha_img = form.find_element(By.ID, "CaptQuiz")
        img_src = captcha_img.get_attribute("src")
        response = requests.get(img_src)
        img_data = response.content  # 圖片的二進制數據
        captcha_text = self.get_captcha_text(img_data)
        captcha_input.send_keys(captcha_text)
        # 模擬按下Enter
        captcha_input.send_keys(Keys.RETURN)

    def study_work(self):
        """
        工讀平台登入
        """
        # 使用者帳號宣布
        username_input = self.driver.find_element(By.ID, "acc")
        username_input.send_keys(self.username)

        # 密碼輸入
        password_input = self.driver.find_element(By.ID, "pass")
        password_input.send_keys(self.password)

        # 驗證碼處理
        captcha_input = self.driver.find_element(By.ID, "caword")
        img_data = self.get_captcha_img()
        captcha_text = self.get_captcha_text(img_data)
        if captcha_text.isdigit() and len(captcha_text) == 6:
            captcha_input.send_keys(captcha_text)
        else:
            captcha_img = self.driver.find_element(By.ID, "authimg")
            captcha_img.click()
            username_input.clear()
            password_input.clear()
            self.study_work()
        # 模擬Enter
        password_input.send_keys(Keys.RETURN)
        try:
            # 等待提示訊息出現
            warning_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='div_content']//p[contains(text(), '這個登入請求，被系統判斷為可能是機器人攻擊行為')]"))
            )
            
            # 如果找到元素，表示提示已出現
            self.driver.get(self.url[self.current])
            self.study_work()
        except:
            return


    def get_captcha_img(self):
        """
        擷取驗證碼圖片
        """
        captcha_img = self.driver.find_element(By.ID, "authimg")
        location = captcha_img.location                         # 元素的 x, y 座標
        size = captcha_img.size                                 # 元素的寬度和高度
        screenshot = self.driver.get_screenshot_as_png()        # 獲取整個畫面的截圖
        screenshot_image = Image.open(io.BytesIO(screenshot))   # 使用 PIL 來讀取整個畫面的截圖

        # 計算驗證碼圖片的區域 (左, 上, 右, 下)
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        captcha_image = screenshot_image.crop((left, top, right, bottom))        # 從整個畫面截圖中裁剪出驗證碼圖片
        img_byte_arr = io.BytesIO()
        captcha_image.save(img_byte_arr, format='PNG')
        img_data = img_byte_arr.getvalue()
        return img_data
    
    def get_captcha_text(self, img_data):
        """
        抓取驗證碼圖像並進行識別
        """

        ocr = ddddocr.DdddOcr()

        # 使用 ddddocr 進行驗證碼識別
        captcha_text = ocr.classification(img_data)

        return captcha_text

    def close_browser(self):
        """
        關閉瀏覽器
        """
        if self.driver:
            self.driver.quit()

# 測試使用
if __name__ == "__main__":
    ulearn = LoginHelper("TEST", "TEST", "ecare")
    input()