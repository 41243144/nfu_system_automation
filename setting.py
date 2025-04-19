import json
import subprocess
import base64
import logging
import os
import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from typing import Dict

# 常數定義
DEBUG = False
CONST_VERSION = "1.0.1"
CONST_AUTHOR = "wenwen"
CONST_TITLE = "Tron Class自動登入系統"
CONST_MAXBOT_CONFIG_FILE = "TronClassBot.json"
CONST_WINDOW_SIZE = "400x300"
CONST_FONT = ("Arial", 12)
ENCODING = "utf-8"

# 支援的大學清單
UNIVERSITY: Dict[str, str] = {
    "虎尾科大(NFU)": "nfu",
    "雲林科技大學(YunTech)": "yuntech",
}

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
    log_file = os.path.join(log_dir, 'setting.log')

    logging.basicConfig(
        level=logging.ERROR,
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding=ENCODING,
    )
    return log_file

class TronClassApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{CONST_TITLE} - v{CONST_VERSION}")
        self.root.geometry(CONST_WINDOW_SIZE)
        self.root.resizable(False, False)

        # 設定樣式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=CONST_FONT, foreground="#333333")
        self.style.configure("TButton", font=CONST_FONT, background="#4CAF50", foreground="white", padding=5)
        self.style.map("TButton", background=[("active", "#45A049")])
        self.style.configure("TCombobox", font=CONST_FONT, padding=5)
        self.style.configure("TEntry", font=CONST_FONT, padding=5)

        # 介面元件
        self.create_widgets()

    def create_widgets(self):
        # 標籤
        ttk.Label(self.root, text="請選擇學校:", style="TLabel").pack(pady=10)

        # 下拉選單
        self.school_var = StringVar(value="請選擇學校")
        self.school_dropdown = ttk.Combobox(
            self.root, textvariable=self.school_var, values=list(UNIVERSITY.keys()), state="readonly", style="TCombobox"
        )
        self.school_dropdown.pack(pady=10)

        # 帳號輸入
        ttk.Label(self.root, text="帳號:", style="TLabel").pack(pady=5)
        self.username_var = StringVar()
        ttk.Entry(self.root, textvariable=self.username_var, style="TEntry").pack(pady=5)

        # 密碼輸入
        ttk.Label(self.root, text="密碼:", style="TLabel").pack(pady=5)
        self.password_var = StringVar()
        ttk.Entry(self.root, textvariable=self.password_var, show="*", style="TEntry").pack(pady=5)

        # 儲存按鈕
        ttk.Button(self.root, text="儲存設定", command=self.save_config, style="TButton").pack(pady=20)

    def save_config(self):
        selected_school = self.school_var.get()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # 驗證輸入
        if selected_school not in UNIVERSITY:
            messagebox.showerror("錯誤", "請選擇一間學校")
            return
        if not username or not password:
            messagebox.showerror("錯誤", "請輸入帳號和密碼")
            return

        # 儲存設定
        encrypted_password = base64.b64encode(password.encode(ENCODING)).decode(ENCODING)

        config_data = {
            "university": UNIVERSITY[selected_school],
            "username": username,
            "password": encrypted_password,
        }

        try:
            with open(CONST_MAXBOT_CONFIG_FILE, "w", encoding=ENCODING) as config_file:
                json.dump(config_data, config_file, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", "設定已成功儲存")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法儲存設定: {e}")

        # 儲存成功後執行 gui.py
        self.run_gui()

    def run_gui(self):
        """執行 gui.py"""
        try:
            # Debug
            if DEBUG:
                subprocess.Popen(["python", "gui.py"], shell=True)
            else:
                gui_path = os.path.join(os.path.dirname(sys.executable), "gui.exe")
                subprocess.Popen([gui_path], shell=True)
            self.root.destroy()  # 關閉當前視窗
        except Exception as e:
            messagebox.showerror("錯誤", f"無法執行: {e}")

if __name__ == "__main__":
    # 設定日誌紀錄
    log_file = logging_setup()
    root = Tk()
    app = TronClassApp(root)
    root.mainloop()