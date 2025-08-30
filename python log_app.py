import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import sqlite3
import requests
import datetime

# =========================
#  هندلر لاگ برای دیتابیس
# =========================
class DatabaseHandler(logging.Handler):
    def __init__(self, db_file="logs.db"):
        super().__init__()
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                time TEXT
            )
        """)
        self.conn.commit()

    def emit(self, record):
        log_entry = self.format(record)
        self.cursor.execute("INSERT INTO logs (level, message, time) VALUES (?, ?, ?)",
                            (record.levelname, record.getMessage(),
                             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()


# =========================
#  هندلر لاگ برای Loki
# =========================
class LokiHandler(logging.Handler):
    def __init__(self, url="http://localhost:3100/loki/api/v1/push"):
        super().__init__()
        self.url = url

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "streams": [
                {
                    "stream": {"job": "my_python_app"},
                    "values": [[
                        str(int(datetime.datetime.now().timestamp() * 1e9)),
                        f"{record.levelname}: {record.getMessage()}"
                    ]]
                }
            ]
        }
        try:
            requests.post(self.url, json=payload)
        except Exception as e:
            print("Error sending log to Loki:", e)


# =========================
#  برنامه Tkinter
# =========================
class LogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم لاگ‌گیری")

        # ناحیه انتخاب
        self.method_var = tk.StringVar(value="console")
        ttk.Label(root, text="روش لاگ‌گیری:").pack(pady=5)

        options = [("Console", "console"),
                   ("Database (SQLite)", "db"),
                   ("Grafana Loki", "loki")]
        for text, value in options:
            ttk.Radiobutton(root, text=text, variable=self.method_var, value=value,
                            command=self.setup_logger).pack(anchor="w")

        # ناحیه نمایش لاگ‌ها
        self.log_display = scrolledtext.ScrolledText(root, width=60, height=15)
        self.log_display.pack(pady=10)

        # دکمه تست
        ttk.Button(root, text="تولید لاگ تست", command=self.test_logs).pack(pady=5)

        # لاگر پیش‌فرض
        self.logger = logging.getLogger("MyLogger")
        self.logger.setLevel(logging.DEBUG)
        self.setup_logger()

    def setup_logger(self):
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        choice = self.method_var.get()

        if choice == "console":
            handler = logging.StreamHandler()
        elif choice == "db":
            handler = DatabaseHandler()
        elif choice == "loki":
            handler = LokiHandler()
        else:
            handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        # هندلر دوم برای نمایش در Tkinter
        gui_handler = logging.StreamHandler(self)
        gui_handler.setFormatter(formatter)
        self.logger.addHandler(gui_handler)

    def write(self, message):
        self.log_display.insert(tk.END, message)
        self.log_display.see(tk.END)

    def flush(self):
        pass

    def test_logs(self):
        self.logger.debug("پیام دیباگ")
        self.logger.info("پیام اطلاعاتی")
        self.logger.warning("پیام هشدار")
        self.logger.error("پیام خطا")
        self.logger.critical("پیام بحرانی")


# =========================
#  اجرای برنامه
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = LogApp(root)
    root.mainloop()
