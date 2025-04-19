import json
import os
import sys
import logging
import subprocess
import threading
from tkinter import Tk, Button, ttk, messagebox
from tkinter import Label, Frame
from PIL import Image, ImageTk

# 常數定義
DEBUG = False
CONST_VERSION = "1.0.1"
CONST_AUTHOR = "wenwen"
CONST_TITLE = "Tron Class自動登入系統"
ENCODING = "utf-8"
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
CONFIG_FILE_PATH = 'config.json'
SETTING_FILE_PATH = 'TronClassBot.json'
IMAGE_SIZE = (400, 80)
WINDOW_TITLE = f"{CONST_TITLE} - v{CONST_VERSION}"
WINDOW_BG_COLOR = "#2b2b2b"
BUTTON_BG_COLOR = "#444444"
BUTTON_TEXT_COLOR = "white"
TITLE_FONT = ("Arial", 24, "bold")
BUTTON_FONT = ("Arial", 14)

# 設定日誌
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
    log_file = os.path.join(log_dir, 'gui.log')

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
        with open(CONFIG_FILE_PATH, 'r', encoding=ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", "設定檔遺失")
        logging.error(f"{CONFIG_FILE_PATH} not found!")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Error", "無法解析設定檔")
        logging.error(f"Failed to parse {CONFIG_FILE_PATH}!")
        return {}

def load_setting():
    """讀取 TronClassBot.json 配置檔案"""
    try:
        with open(SETTING_FILE_PATH, 'r', encoding=ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", "沒有找到歷史資料檔案，請先完成資料設定！")
        logging.error(f"{SETTING_FILE_PATH} not found!")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Error", "無法解析歷史資料檔案！")
        logging.error(f"Failed to parse {SETTING_FILE_PATH}!")
        return {}

def on_image_click(args):
    """處理圖片按鈕點擊事件"""
    def run_second_program():
        try:

            if DEBUG:
                subprocess.Popen(
                    ["python", "LoginHelper.py", args['name']]
                )
            else:
                # 正式執行
                login_helper_path = os.path.join(os.path.dirname(sys.executable), "LoginHelper.exe")
                subprocess.Popen(
                    [login_helper_path, args['name']],
                    shell=True
                )
        except Exception as e:
            logging.error(f"Failed to execute login_helper.py: {e}")
            messagebox.showerror("Error", "出現錯誤，請檢查設定檔")

    threading.Thread(target=run_second_program).start()

def open_settings_and_exit():
    """執行 setting.py 並關閉當前程式"""
    try:
        if DEBUG:
            subprocess.Popen(["python", "setting.py"], shell=True)
        else:
            setting_path = os.path.join(os.path.dirname(sys.executable), "setting.exe")
            subprocess.Popen([setting_path], shell=True)

        logging.info("Opening setting.py and exiting current program.")
        sys.exit()
    except Exception as e:
        messagebox.showerror("Error", "出現錯誤，請檢查設定檔")
        logging.error(f"Failed to open setting.py: {e}")

def create_image_buttons(root, school_key, **kwargs):
    """根據學校的圖片配置按鈕"""
    config_file = kwargs.get("config_file")
    if not config_file:
        logging.error("No config_file provided to create_image_buttons.")
        return

    if school_key not in config_file:
        messagebox.showerror("Error", f"No images found for school: {school_key}")
        logging.error(f"No images found for school: {school_key}")
        return

    title_label = Label(root, text="選擇系統登入", font=TITLE_FONT, bg=WINDOW_BG_COLOR, fg="white")
    title_label.pack(pady=20)

    images = config_file[school_key]

    button_frame = Frame(root, bg=WINDOW_BG_COLOR)
    button_frame.pack(pady=10)

    for idx, (name, details) in enumerate(images.items()):
        path = details.get("image", "")
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize(IMAGE_SIZE, Image.LANCZOS)  # 調整圖片大小
                photo = ImageTk.PhotoImage(img)

                if idx == 0:
                    root.iconphoto(False, photo)
                    continue

                btn = Button(
                    button_frame,
                    image=photo,
                    command=lambda details=details, name=name: on_image_click({
                        'name': name,
                    }),
                    bg=WINDOW_BG_COLOR,
                    relief="flat",
                    highlightthickness=2,
                    highlightbackground="#444444",
                )
                btn.image = photo
                btn.grid(row=(idx-1) // 2, column=idx % 2, padx=10, pady=10)
            except Exception as e:
                messagebox.showwarning("Warning", f"出現錯誤，請檢查設定檔")
                logging.warning(f"Failed to load image {path}: {e}")
        else:
            messagebox.showwarning("Warning", "出現錯誤，請檢查設定檔")
            logging.warning(f"Image not found: {path}")

    change_password_btn = Button(
        root,
        text="更改設定",
        font=BUTTON_FONT,
        bg=BUTTON_BG_COLOR,
        fg=BUTTON_TEXT_COLOR,
        relief="flat",
        command=open_settings_and_exit,
    )
    change_password_btn.pack(pady=20)

def main():
    """主程式"""
    log_file = logging_setup()
    config_file = load_config_file()
    if not config_file:
        messagebox.showerror("Error", "出現錯誤，請檢查設定檔")
        logging.error("Failed to load config.json!")
        return

    setting = load_setting()
    if not setting:
        open_settings_and_exit()

    university_key = setting.get("university", "")
    if not university_key:
        messagebox.showerror("Error", "出現錯誤，請檢查設定檔")
        logging.error("university key not found in TronClassBot.json!")
        return
    
    root = Tk()
    root.title(WINDOW_TITLE)
    root.configure(bg=WINDOW_BG_COLOR)
    style = ttk.Style()
    style.configure("TButton", padding=5, relief="flat", background="#f0f0f0")
    create_image_buttons(root, university_key, config_file=config_file)
    root.mainloop()

if __name__ == "__main__":
    main()
