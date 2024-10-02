"""
project name: 虎科大自動登入
project author: wenwen
project description: 
    這是一個使用 PyQt6 建立的自動登入應用程式，利用 Selenium 驅動 Chrome 瀏覽器，自動登入不同系統，包括ulearn、ecare、mail2000以及工讀平台，並提供使用者介面讓使用者輸入帳號密碼並進行自動登入。
project function: 
    - 自動登入ulearn、ecare、mail2000和工讀平台。
    - 儲存及更新使用者的帳號和密碼。
    - 使用驗證碼辨識技術自動處理登入過程中的驗證碼。
    - 提供圖形化使用者介面 (GUI) 進行操作。
latest change date: 2024-10-02

"""
from gui import MyWidget
from PyQt6 import QtWidgets
import sys
import traceback

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        Form = MyWidget()
        Form.show()
        sys.exit(app.exec())
    except Exception as e:
        # 將錯誤信息寫入到 log.txt
        with open("error_log.txt", "w") as f:
            f.write("An error occurred:\n")
            f.write(str(e) + "\n")
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()
