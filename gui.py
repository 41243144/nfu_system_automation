import sys
import os
import functools
from PyQt6 import QtWidgets, QtGui, QtCore
from LoginHelper import LoginHelper

class LoginThread(QtCore.QThread):
    login_finished = QtCore.pyqtSignal(str)  # 登入完成時發射的信號

    def __init__(self, account, password, system_name):
        super().__init__()
        self.account = account
        self.password = password
        self.system_name = system_name

    def run(self):
        """
        將登入流程移交多線程
        """
        try:
            # 啟動 LoginHelper，進行登入操作
            helper = LoginHelper(self.account, self.password, self.system_name)
            self.login_finished.emit(f"{self.system_name} 登入成功！")  # 成功時發射信號
        except Exception as e:
            self.login_finished.emit(f"{self.system_name} 登入失敗: {str(e)}")  # 失敗時發射信號

class AccountDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('請輸入校務系統帳號密碼')
        self.setFixedSize(300, 150)

        # 設置佈局
        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("請輸入校務系統帳號密碼")
        self.label.setStyleSheet("""
                font-size: 15px;
                font-width: bold;
                text-align: center;
            """)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter) # align: top center
        self.label.setGeometry(0, 20, 300, 150)
        layout.addWidget(self.label)

        # 帳號輸入
        self.account_label = QtWidgets.QLabel("帳號:")
        self.account_input = QtWidgets.QLineEdit(self)
        layout.addWidget(self.account_label)
        layout.addWidget(self.account_input)

        # 密碼輸入
        self.password_label = QtWidgets.QLabel("密碼:")
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # 確定與取消按鈕
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        # 設置對話框佈局
        self.setLayout(layout)

    def get_account_info(self):
        """
        回傳帳號與密碼
        """
        return self.account_input.text(), self.password_input.text()

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # button_initial (ulean, ecare, mail2000, 工讀平台)
        self.button_name = ['ulearn', 'ecare', 'mail2000', '工讀平台']
        self.window_size = (400, 400)               # 視窗大小
        WIDTH, HEIGHT = self.window_size
        self.account_file = "account.txt"  # 存儲帳號密碼的文件
        self.button = list()
        self.check_account()               # 檢查帳號密碼紀錄
        self.setWindowTitle('自動登入使用者介面')     # 設置視窗標題
        self.resize(WIDTH, HEIGHT)                  # 設置視窗大小
        self.setUpdatesEnabled(True)                # 允許視窗自動更新
        self.main()

    def main(self):
        if self.check_account():
            self.ui()
        else:
            exit(1)

    def check_account(self):
        if self.load_account():
            return True
        else:
            if self.create_account():
                return True
            else:
                return False

    def load_account(self):
        try:
            with open(self.account_file, "r", encoding="utf-8") as file:
                self.account, self.password = file.read().split()
            return True
        except FileNotFoundError:
            self.show_message("錯誤", "帳號文件未找到，請創建新帳號。")
            return False
        except ValueError:
            self.show_message("錯誤", "帳號文件格式不正確，無法加載帳號與密碼。")
            return False
        except Exception as e:
            self.show_message("未知錯誤", f"發生未知錯誤: {e}")
            return False

    def create_account(self):
        """
        創建帳號與密碼，並將其保存到 account.txt
        """
        dialog = AccountDialog()  # 打開帳號密碼輸入對話框
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            account, password = dialog.get_account_info()

            if account and password:  # 檢查是否輸入帳號與密碼
                try:
                    with open(self.account_file, "w", encoding="utf-8") as file:
                        file.write(f"{account} {password}")
                    self.show_message("成功", "帳號與密碼已成功儲存。")
                    return True
                except Exception as e:
                    self.show_message("錯誤", f"無法儲存帳號: {e}")
                    return False
            else:
                self.show_message("錯誤", "帳號或密碼不得為空。")
                return False
        return False

    def show_message(self, title, message):
        """
        使用 QMessageBox 來顯示錯誤或提示信息
        """
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Warning if "錯誤" in title else QtWidgets.QMessageBox.Icon.Information)
        msg_box.exec()

    def ui(self):
        """
        創建ui介面
        """
        WIDTH, HEIGHT = self.window_size
        BUTTON_LEN = len(self.button_name)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 獲取當前目錄

        # Label
        self.label = QtWidgets.QLabel(self)
        self.label.setText('選擇系統登入')
        self.label.setStyleSheet("font-size:20px;")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter) # align: top center
        self.label.setGeometry(0, 20, WIDTH, HEIGHT)  # (margin, margin, setWidth, setHeight)

        # set button
        for i in range(BUTTON_LEN):
            icon_path = os.path.join(BASE_DIR, 'icon', f"{self.button_name[i]}.png")  # 構建圖片的路徑

            # 創建一個新按鈕
            button = QtWidgets.QPushButton(self)
            button.setFixedWidth(200)
            button.setText(self.button_name[i])
            button.setStyleSheet("""
                font-size: 15px;
                padding-left: 20px;
                text-align: left;
            """)

            # 動態設定按鈕位置，讓每個按鈕都不重疊
            button.move(50, 50 + i * 80)

            # 檢查圖片是否存在並設置圖標
            if os.path.exists(icon_path):
                icon = QtGui.QIcon(icon_path)   # 使用圖片建立 QIcon
                button.setIcon(icon)
                button.setIconSize(QtCore.QSize(64, 64))  # 設置圖標的大小
            else:
                self.show_message("錯誤", f"未找到圖標文件: {icon_path}")
            button.clicked.connect(functools.partial(self.on_button_click, button))
            self.button.append(button)
        # 更改帳號密碼按鈕
        self.change_button = QtWidgets.QPushButton('更改帳號密碼', self)
        self.change_button.setGeometry(50, 350, 200, 40)  # 設定按鈕位置和大小
        self.change_button.setStyleSheet("font-size: 15px;")
        self.change_button.clicked.connect(self.on_change_account_click)
    def on_button_click(self, button):
        print(button.text())
        self.login_thread = LoginThread(self.account, self.password, button.text())
        self.login_thread.login_finished.connect(self.on_login_finished)
        self.login_thread.start()
    def on_change_account_click(self):
        """
        處理更改帳號密碼的邏輯
        """
        dialog = AccountDialog()  # 打開更改帳號密碼對話框
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            account, password = dialog.get_account_info()

            if account and password:  # 檢查是否輸入帳號與密碼
                try:
                    with open(self.account_file, "w", encoding="utf-8") as file:
                        file.write(f"{account} {password}")
                    self.show_message("成功", "帳號與密碼已成功更改。")
                    self.account, self.password = account, password  # 更新內存中的帳號密碼
                except Exception as e:
                    self.show_message("錯誤", f"無法儲存帳號: {e}")
            else:
                self.show_message("錯誤", "帳號或密碼不得為空。")
        
    def on_login_finished(self, message):
        print("登入結果", message)

# if __name__ == '__main__':
#     # 創建app
#     app = QtWidgets.QApplication(sys.argv)
    
#     Form = MyWidget()
#     Form.show()
    
#     sys.exit(app.exec())
