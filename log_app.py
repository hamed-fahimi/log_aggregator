import tkinter as tk
from tkinter import ttk, scrolledtext
import logging

# ---------- رنگ‌ها برای لاگ ----------
LOG_COLORS = {
    "DEBUG": "#6c757d",
    "INFO": "#198754",
    "WARNING": "#ffc107",
    "ERROR": "#dc3545",
    "CRITICAL": "#d63384"
}


# ---------- اپلیکیشن ----------
class LogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم لاگ‌گیری")
        self.root.geometry("700x500")
        self.root.configure(bg="#1e1e2f")

        # استایل کلی
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e2f", foreground="white", font=("IRANSans", 12))
        style.configure("TRadiobutton", background="#1e1e2f", foreground="white", font=("IRANSans", 11))
        style.configure("TButton", font=("IRANSans", 11, "bold"))

        # ---- Frame انتخاب روش لاگ‌گیری ----
        frame_top = ttk.Frame(root)
        frame_top.pack(fill="x", pady=10)

        ttk.Label(frame_top, text="روش لاگ‌گیری:").pack(side="left", padx=10)

        self.method_var = tk.StringVar(value="console")
        options = [("Console", "console"), ("Database", "db"), ("Grafana Loki", "loki")]

        for text, value in options:
            ttk.Radiobutton(frame_top, text=text, variable=self.method_var, value=value).pack(side="left", padx=5)

        # ---- ناحیه نمایش لاگ ----
        frame_log = ttk.LabelFrame(root, text="Log Output")
        frame_log.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_display = scrolledtext.ScrolledText(frame_log, width=80, height=20, bg="#2d2d3d", fg="white",
                                                     font=("Consolas", 10))
        self.log_display.pack(fill="both", expand=True, padx=5, pady=5)

        # ---- دکمه‌ها ----
        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(pady=10)

        ttk.Button(frame_buttons, text="تولید لاگ تست", command=self.test_logs).pack(side="left", padx=10)
        ttk.Button(frame_buttons, text="پاک کردن لاگ‌ها", command=self.clear_logs).pack(side="left", padx=10)

        # ---- Status Bar ----
        self.status_var = tk.StringVar(value="روش انتخاب‌شده: Console")
        status_bar = ttk.Label(root, textvariable=self.status_var, anchor="w", relief="sunken")
        status_bar.pack(fill="x", side="bottom")

        # ---- Logger ----
        self.logger = logging.getLogger("MyLogger")
        self.logger.setLevel(logging.DEBUG)
        self.setup_logger()

    def setup_logger(self):
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # هندلر GUI
        gui_handler = logging.StreamHandler(self)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        gui_handler.setFormatter(formatter)
        self.logger.addHandler(gui_handler)

        # به‌روزرسانی استاتوس
        method = self.method_var.get()
        names = {"console": "Console", "db": "Database", "loki": "Grafana Loki"}
        self.status_var.set(f"روش انتخاب‌شده: {names.get(method, 'Console')}")

    def write(self, message):
        # پیدا کردن سطح لاگ و اعمال رنگ
        for level, color in LOG_COLORS.items():
            if level in message:
                self.log_display.insert(tk.END, message, level)
                self.log_display.tag_config(level, foreground=color)
                break
        else:
            self.log_display.insert(tk.END, message)

        self.log_display.see(tk.END)

    def flush(self):
        pass

    def test_logs(self):
        self.setup_logger()
        self.logger.debug("پیام دیباگ")
        self.logger.info("پیام اطلاعاتی")
        self.logger.warning("پیام هشدار")
        self.logger.error("پیام خطا")
        self.logger.critical("پیام بحرانی")

    def clear_logs(self):
        self.log_display.delete(1.0, tk.END)


# ---------- اجرا ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = LogApp(root)
    root.mainloop()

