# ye_replacer.py
import os
import re
import sys
import glob
import platform
import urllib.request
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font

OS_NAME = platform.system()  # 'Windows', 'Darwin', 'Linux'

# ── تنظیمات High-DPI ویندوز ───────────────────────────────────────────────────
if OS_NAME == "Windows":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ── دانلود و بارگذاری خودکار فونت Vazirmatn ───────────────────────────────────
VAZIR_URL = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf"


def get_base_dir() -> str:
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def ensure_vazirmatn_font() -> str:
    base_dir = get_base_dir()
    # بررسی وجود هرگونه فایل فونت وزیرمتن در پوشه برنامه
    candidates = [
        os.path.join(base_dir, "Vazirmatn-Regular.ttf"),
        os.path.join(base_dir, "Vazirmatn.ttf"),
    ] + glob.glob(os.path.join(base_dir, "*Vazir*.ttf"))

    font_path = next((p for p in candidates if os.path.exists(p)), None)

    # اگر فایل فونت کنار برنامه نبود، خودکار دانلودش کن
    if not font_path:
        target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Vazirmatn-Regular.ttf")
        if not os.path.exists(target):
            try:
                urllib.request.urlretrieve(VAZIR_URL, target)
                font_path = target
            except Exception:
                font_path = None
        else:
            font_path = target

    if OS_NAME == "Windows" and font_path and os.path.exists(font_path):
        try:
            import ctypes
            ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
            return "Vazirmatn"
        except Exception:
            pass

    if OS_NAME == "Darwin":
        return "Vazirmatn" if font_path else "Geeza Pro"
    elif OS_NAME == "Linux":
        return "Vazirmatn" if font_path else "Noto Sans Arabic"
    return "Vazirmatn"


FONT_NAME = ensure_vazirmatn_font()
MOD_KEY = "Command" if OS_NAME == "Darwin" else "Control"
MOD_LABEL = "Cmd" if OS_NAME == "Darwin" else "Ctrl"

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
def to_fa_num(val) -> str:
    return str(val).translate(FA_DIGITS)


# ── کپی‌رایت ──────────────────────────────────────────────────────────────────
COPYRIGHT_FA = (
    "حق نشر © ۲۰۲۶  Mr.M.M95612\n"
    "تمامی حقوق محفوظ است.\n\n"
    "هرگونه کپی‌برداری، توزیع، تغییر، یا استفادهٔ غیرمجاز\n"
    "از این نرم‌افزار ممنوع است."
)
COPYRIGHT_EN = (
    "Copyright © 2026  Mr.M.M95612\n"
    "All rights reserved.\n\n"
    "Unauthorized copying, distribution, modification,\n"
    "or use of this software is strictly prohibited."
)


# ── پالت‌های رنگی ─────────────────────────────────────────────────────────────
DARK = {
    "bg":            "#12121F",
    "surface":       "#1B1B2F",
    "surface2":      "#162447",
    "primary":       "#E94560",
    "primary_dark":  "#C73652",
    "secondary":     "#3D2C8D",
    "success":       "#2ECC71",
    "success_dark":  "#27AE60",
    "warning":       "#F39C12",
    "border":        "#2A2A4A",
    "text":          "#F0F0F5",
    "subtext":       "#9A9AB0",
    "header_bg":     "#0D0D17",
    "status_bg":     "#0D0D17",
    "title_text":    "#E94560",
    "input_bg":      "#151525",
    "error_bg":      "#2D0A0A",
    "error_text":    "#FF6B6B",
}

LIGHT = {
    "bg":            "#F4F6F9",
    "surface":       "#FFFFFF",
    "surface2":      "#E8EAF6",
    "primary":       "#3F51B5",
    "primary_dark":  "#303F9F",
    "secondary":     "#5C6BC0",
    "success":       "#43A047",
    "success_dark":  "#388E3C",
    "warning":       "#FB8C00",
    "border":        "#D0D5DD",
    "text":          "#1A1A2E",
    "subtext":       "#667085",
    "header_bg":     "#3F51B5",
    "status_bg":     "#E4E7EC",
    "title_text":    "#FFFFFF",
    "input_bg":      "#F9FAFB",
    "error_bg":      "#FFF0F0",
    "error_text":    "#D92D20",
}


# ── منطق پردازش متن ──────────────────────────────────────────────────────────
# کاراکترهای هدف: ی فارسی (06CC)، ى مقصوره (0649)، ی باریک (FBFD/FBFC)
YE_VARIANTS = ('\u06cc', '\u0649', '\ufbfc', '\ufbfd', '\ufbfe', '\ufbff')
ARABIC_YE = '\u064a'  # ي عربی (دو نقطه)
PERSIAN_KAF = '\u06a9'
ARABIC_KAF = '\u0643'


def analyze_and_replace(text: str, replace_kaf: bool = False) -> tuple[str, int, int]:
    """
    خروجی: (متن تبدیل‌شده، تعداد تبدیل‌های جدید، تعداد ي عربی که از قبل در متن بود)
    """
    already_arabic_ye = text.count(ARABIC_YE)
    replaced_count = sum(text.count(ch) for ch in YE_VARIANTS)

    result = text
    for ch in YE_VARIANTS:
        result = result.replace(ch, ARABIC_YE)

    if replace_kaf:
        kaf_cnt = result.count(PERSIAN_KAF)
        replaced_count += kaf_cnt
        result = result.replace(PERSIAN_KAF, ARABIC_KAF)

    return result, replaced_count, already_arabic_ye


def has_latin_letters(text: str) -> bool:
    return bool(re.search(r'[A-Za-z]', text))


def strip_latin_letters(text: str) -> str:
    return re.sub(r'[A-Za-z]+', '', text)


# ── پنجره اصلی برنامه ─────────────────────────────────────────────────────────
class YeReplacerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.dark = True
        self.c = DARK
        self.title("YeReplacer  |  ی ← ي")
        self.geometry("960x720")
        self.minsize(780, 580)

        # باز شدن به صورت Maximized (تمام‌صفحه)
        self.after(50, self._maximize_window)

        self.var_live = tk.BooleanVar(value=True)
        self.var_kaf = tk.BooleanVar(value=False)
        self.var_block_latin = tk.BooleanVar(value=True)
        self.var_auto_copy = tk.BooleanVar(value=False)

        self.f_title  = Font(family=FONT_NAME, size=14, weight="bold")
        self.f_btn    = Font(family=FONT_NAME, size=11, weight="bold")
        self.f_text   = Font(family=FONT_NAME, size=13)
        self.f_status = Font(family=FONT_NAME, size=10)
        self.f_small  = Font(family=FONT_NAME, size=10)

        self._build_ui()
        self._setup_shortcuts()
        self._apply_theme()

    def _maximize_window(self):
        try:
            if OS_NAME == "Windows":
                self.state("zoomed")
            elif OS_NAME == "Linux":
                self.attributes("-zoomed", True)
            else:
                w, h = self.winfo_screenwidth(), self.winfo_screenheight()
                self.geometry(f"{w}x{h}+0+0")
        except Exception:
            pass

    def _build_ui(self):
        cursor_style = "pointinghand" if OS_NAME == "Darwin" else "hand2"

        # ۱. هدر
        self.frm_header = tk.Frame(self, height=54)
        self.frm_header.pack(fill="x", side="top")
        self.frm_header.pack_propagate(False)

        self.btn_theme = tk.Button(
            self.frm_header, text="☀", font=self.f_btn,
            relief="flat", bd=0, cursor=cursor_style,
            command=self._toggle_theme, width=3
        )
        self.btn_theme.pack(side="left", padx=(14, 6), pady=10)

        self.btn_about = tk.Button(
            self.frm_header, text="ℹ درباره", font=self.f_small,
            relief="flat", bd=0, cursor=cursor_style,
            command=self._show_about, padx=12, pady=4
        )
        self.btn_about.pack(side="left", padx=4, pady=10)

        self.lbl_title = tk.Label(
            self.frm_header,
            text="YeReplacer  |  اصلاح «ی» برای نرم‌افزارهای ادوبی",
            font=self.f_title, anchor="e"
        )
        self.lbl_title.pack(side="right", padx=(0, 18), pady=10)

        # ۲. نوار تنظیمات (چیدمان شبکه‌ای تا هیچ گزینه‌ای از کادر بیرون نزند)
        self.frm_opts = tk.Frame(self, pady=6)
        self.frm_opts.pack(fill="x", padx=18, pady=(8, 2))
        for col in range(4):
            self.frm_opts.columnconfigure(col, weight=1)

        chk_cfg = dict(font=self.f_small, relief="flat", bd=0, cursor=cursor_style)

        self.chk_autocopy = tk.Checkbutton(
            self.frm_opts, text="کپی خودکار پس از تبدیل دستی",
            variable=self.var_auto_copy, **chk_cfg
        )
        self.chk_autocopy.grid(row=0, column=0, sticky="e", padx=6)

        self.chk_latin = tk.Checkbutton(
            self.frm_opts, text="جلوگیری از حروف انگلیسی",
            variable=self.var_block_latin, command=self._on_option_change, **chk_cfg
        )
        self.chk_latin.grid(row=0, column=1, sticky="e", padx=6)

        self.chk_kaf = tk.Checkbutton(
            self.frm_opts, text="تبدیل «ک» به «ك»",
            variable=self.var_kaf, command=self._on_option_change, **chk_cfg
        )
        self.chk_kaf.grid(row=0, column=2, sticky="e", padx=6)

        self.chk_live = tk.Checkbutton(
            self.frm_opts, text="تبدیل خودکار (لحظه‌ای)",
            variable=self.var_live, command=self._on_option_change, **chk_cfg
        )
        self.chk_live.grid(row=0, column=3, sticky="e", padx=6)

        # ۳. بدنه اصلی
        self.frm_body = tk.Frame(self)
        self.frm_body.pack(fill="both", expand=True, padx=18, pady=6)

        # --- کارت ورودی ---
        self.frm_in = tk.LabelFrame(
            self.frm_body, text="  متن ورودی (فارسی)  ",
            font=self.f_small, bd=1, relief="solid", labelanchor="ne"
        )
        self.frm_in.pack(fill="both", expand=True, pady=(0, 10))

        frm_in_editor = tk.Frame(self.frm_in)
        frm_in_editor.pack(fill="both", expand=True, padx=8, pady=(8, 2))

        self.scroll_in = ttk.Scrollbar(frm_in_editor)
        self.scroll_in.pack(side="left", fill="y")

        # نکته کلیدی: عدم استفاده از tag_configure(justify='right') برای جلوگیری از باگ پرش کاراکتر آخر در ویندوز
        self.txt_in = tk.Text(
            frm_in_editor, font=self.f_text, wrap="word",
            relief="flat", bd=0, undo=True, height=6,
            yscrollcommand=self.scroll_in.set, padx=10, pady=8
        )
        self.txt_in.pack(side="right", fill="both", expand=True)
        self.scroll_in.config(command=self.txt_in.yview)

        self.txt_in.bind("<KeyRelease>", self._on_input_change)
        self._add_context_menu(self.txt_in, is_readonly=False)

        self.lbl_chars = tk.Label(
            self.frm_in, text="کاراکترها: ۰  |  قابل تبدیل («ی» فارسی): ۰  |  «ي» عربی موجود: ۰",
            font=self.f_small, anchor="w"
        )
        self.lbl_chars.pack(side="bottom", fill="x", padx=12, pady=(0, 6))

        # --- کارت خروجی ---
        self.frm_out = tk.LabelFrame(
            self.frm_body, text="  متن خروجی (اصلاح‌شده برای ادوبی)  ",
            font=self.f_small, bd=1, relief="solid", labelanchor="ne"
        )
        self.frm_out.pack(fill="both", expand=True, pady=(0, 10))

        frm_out_editor = tk.Frame(self.frm_out)
        frm_out_editor.pack(fill="both", expand=True, padx=8, pady=(8, 2))

        self.scroll_out = ttk.Scrollbar(frm_out_editor)
        self.scroll_out.pack(side="left", fill="y")

        self.txt_out = tk.Text(
            frm_out_editor, font=self.f_text, wrap="word",
            relief="flat", bd=0, state="disabled", height=6,
            yscrollcommand=self.scroll_out.set, padx=10, pady=8
        )
        self.txt_out.pack(side="right", fill="both", expand=True)
        self.scroll_out.config(command=self.txt_out.yview)
        self._add_context_menu(self.txt_out, is_readonly=True)

        self.lbl_count = tk.Label(
            self.frm_out, text="جایگزینی انجام‌شده: ۰",
            font=self.f_small, anchor="w"
        )
        self.lbl_count.pack(side="bottom", fill="x", padx=12, pady=(0, 6))

        # ۴. دکمه‌ها (چیدمان Grid هم‌اندازه که هرگز از صفحه بیرون نمی‌زند)
        self.frm_btns = tk.Frame(self.frm_body)
        self.frm_btns.pack(fill="x", pady=(2, 6))
        for col in range(6):
            self.frm_btns.columnconfigure(col, weight=1)

        btn_cfg = dict(font=self.f_btn, relief="flat", bd=0, cursor=cursor_style, pady=9)

        self.btn_load = tk.Button(self.frm_btns, text="📂 باز کردن فایل", command=self._load_file, **btn_cfg)
        self.btn_load.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_save = tk.Button(self.frm_btns, text="💾 ذخیره فایل", command=self._save_file, **btn_cfg)
        self.btn_save.grid(row=0, column=1, sticky="ew", padx=4)

        self.btn_clear = tk.Button(self.frm_btns, text="🗑 پاک‌کردن", command=self._clear, **btn_cfg)
        self.btn_clear.grid(row=0, column=2, sticky="ew", padx=4)

        self.btn_paste = tk.Button(self.frm_btns, text="📥 جای‌گذاری و تبدیل", command=self._paste_and_convert, **btn_cfg)
        self.btn_paste.grid(row=0, column=3, sticky="ew", padx=4)

        self.btn_copy = tk.Button(self.frm_btns, text="📋 کپی خروجی", command=self._copy_output, **btn_cfg)
        self.btn_copy.grid(row=0, column=4, sticky="ew", padx=4)

        self.btn_convert = tk.Button(self.frm_btns, text="🔄 تبدیل متن", command=lambda: self._convert(manual=True), **btn_cfg)
        self.btn_convert.grid(row=0, column=5, sticky="ew", padx=(4, 0))

        # ۵. نوار وضعیت
        self.frm_status = tk.Frame(self, height=32)
        self.frm_status.pack(fill="x", side="bottom")
        self.frm_status.pack_propagate(False)

        self.lbl_stat_left = tk.Label(
            self.frm_status,
            text=f"YeReplacer v2.1  |  فونت: {FONT_NAME}  |  {MOD_LABEL}+Enter: تبدیل  |  {MOD_LABEL}+Shift+C: کپی",
            font=self.f_status, anchor="w"
        )
        self.lbl_stat_left.pack(side="left", padx=14)

        self.lbl_status = tk.Label(
            self.frm_status, text="● آماده",
            font=self.f_status, anchor="e"
        )
        self.lbl_status.pack(side="right", padx=14)

    def _setup_shortcuts(self):
        self.bind(f"<{MOD_KEY}-Return>", lambda _: self._convert(manual=True))
        self.bind(f"<{MOD_KEY}-Shift-C>", lambda _: self._copy_output())
        self.bind(f"<{MOD_KEY}-Shift-c>", lambda _: self._copy_output())
        self.bind(f"<{MOD_KEY}-l>", lambda _: self._clear())
        self.bind(f"<{MOD_KEY}-L>", lambda _: self._clear())

    def _add_context_menu(self, widget: tk.Text, is_readonly: bool):
        menu = tk.Menu(widget, tearoff=0, font=self.f_small)
        if not is_readonly:
            menu.add_command(label="برش (Cut)", command=lambda: widget.event_generate("<<Cut>>"))
            menu.add_command(label="کپی (Copy)", command=lambda: widget.event_generate("<<Copy>>"))
            menu.add_command(label="جای‌گذاری (Paste)", command=lambda: self._paste_to_widget(widget))
            menu.add_separator()
        else:
            menu.add_command(label="کپی کل خروجی", command=self._copy_output)
            menu.add_command(label="کپی بخش انتخاب‌شده", command=lambda: widget.event_generate("<<Copy>>"))
            menu.add_separator()

        menu.add_command(label="انتخاب همه (Select All)", command=lambda: widget.tag_add("sel", "1.0", "end"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)
        if OS_NAME == "Darwin":
            widget.bind("<Button-2>", show_menu)
            widget.bind("<Control-Button-1>", show_menu)

    def _paste_to_widget(self, widget: tk.Text):
        try:
            clip = self.clipboard_get()
            widget.insert("insert", clip)
            self._on_input_change()
        except tk.TclError:
            pass

    def _apply_theme(self):
        c = self.c
        self.configure(bg=c["bg"])

        self.frm_header.configure(bg=c["header_bg"])
        self.lbl_title.configure(bg=c["header_bg"], fg=c["title_text"])
        self.btn_theme.configure(bg=c["secondary"], fg="#FFFFFF", activebackground=c["primary"], activeforeground="#FFFFFF")
        self.btn_about.configure(bg=c["surface2"], fg=c["text"] if not self.dark else "#FFFFFF", activebackground=c["primary"], activeforeground="#FFFFFF")

        self.frm_opts.configure(bg=c["bg"])
        for chk in (self.chk_live, self.chk_kaf, self.chk_latin, self.chk_autocopy):
            chk.configure(bg=c["bg"], fg=c["text"], activebackground=c["bg"], activeforeground=c["primary"], selectcolor=c["surface"])

        self.frm_body.configure(bg=c["bg"])
        for frm in (self.frm_in, self.frm_out):
            frm.configure(bg=c["surface"], fg=c["subtext"], highlightbackground=c["border"])

        for txt in (self.txt_in, self.txt_out):
            txt.master.configure(bg=c["surface"])
            txt.configure(bg=c["input_bg"], fg=c["text"], insertbackground=c["primary"], selectbackground=c["primary"], selectforeground="#FFFFFF")

        self.lbl_chars.configure(bg=c["surface"], fg=c["subtext"])
        self.lbl_count.configure(bg=c["surface"], fg=c["success"])

        self.frm_btns.configure(bg=c["bg"])
        self.btn_convert.configure(bg=c["primary"], fg="#FFFFFF", activebackground=c["primary_dark"], activeforeground="#FFFFFF")
        self.btn_copy.configure(bg=c["secondary"], fg="#FFFFFF", activebackground=c["primary"], activeforeground="#FFFFFF")
        self.btn_paste.configure(bg=c["surface2"], fg="#FFFFFF" if self.dark else c["text"], activebackground=c["primary"], activeforeground="#FFFFFF")
        self.btn_clear.configure(bg=c["warning"], fg="#FFFFFF", activebackground="#d68910", activeforeground="#FFFFFF")
        self.btn_save.configure(bg=c["success"], fg="#FFFFFF", activebackground=c["success_dark"], activeforeground="#FFFFFF")
        self.btn_load.configure(bg=c["secondary"], fg="#FFFFFF", activebackground=c["primary"], activeforeground="#FFFFFF")

        self.frm_status.configure(bg=c["status_bg"])
        self.lbl_status.configure(bg=c["status_bg"], fg=c["subtext"])
        self.lbl_stat_left.configure(bg=c["status_bg"], fg=c["subtext"])

    def _toggle_theme(self):
        self.dark = not self.dark
        self.c = DARK if self.dark else LIGHT
        self.btn_theme.configure(text="☀" if self.dark else "🌙")
        self._apply_theme()

    def _status(self, msg: str, role: str = "subtext"):
        color_map = {
            "success": self.c["success"],
            "warning": self.c["warning"],
            "error":   self.c["error_text"],
            "subtext": self.c["subtext"],
        }
        self.lbl_status.configure(text=msg, fg=color_map.get(role, self.c["subtext"]))

    def _on_option_change(self):
        self._on_input_change()

    def _on_input_change(self, _=None):
        text = self.txt_in.get("1.0", "end-1c")

        n_chars = len(text)
        result, replaced_cnt, arabic_ye_cnt = analyze_and_replace(text, self.var_kaf.get())

        self.lbl_chars.configure(
            text=(
                f"کاراکترها: {to_fa_num(n_chars)}  |  "
                f"قابل تبدیل («ی» فارسی): {to_fa_num(replaced_cnt)}  |  "
                f"«ي» عربی موجود در متن: {to_fa_num(arabic_ye_cnt)}"
            )
        )

        if self.var_live.get():
            if not text.strip():
                self._set_output("")
                self.lbl_count.configure(text="جایگزینی انجام‌شده: ۰")
                return

            if self.var_block_latin.get() and has_latin_letters(text):
                self._status("⚠ متن حاوی حروف انگلیسی است! (برای جزئیات روی تبدیل کلیک کنید)", "error")
                return

            self._set_output(result)
            total_ready = replaced_cnt + arabic_ye_cnt
            self.lbl_count.configure(
                text=f"جایگزینی جدید: {to_fa_num(replaced_cnt)}  |  مجموع «ي» آماده برای ادوبی: {to_fa_num(total_ready)}"
            )
            self._status("● تبدیل خودکار انجام شد", "success")

    def _set_output(self, text: str):
        self.txt_out.configure(state="normal")
        self.txt_out.delete("1.0", "end")
        self.txt_out.insert("1.0", text)
        self.txt_out.configure(state="disabled")

    def _convert(self, manual: bool = False):
        text = self.txt_in.get("1.0", "end-1c")
        if not text.strip():
            self._status("⚠ ورودی خالی است!", "warning")
            return

        if self.var_block_latin.get() and has_latin_letters(text):
            self._show_latin_error()
            return

        result, replaced_cnt, arabic_ye_cnt = analyze_and_replace(text, self.var_kaf.get())
        self._set_output(result)
        total_ready = replaced_cnt + arabic_ye_cnt
        self.lbl_count.configure(
            text=f"جایگزینی جدید: {to_fa_num(replaced_cnt)}  |  مجموع «ي» آماده برای ادوبی: {to_fa_num(total_ready)}"
        )

        if manual and self.var_auto_copy.get():
            self.clipboard_clear()
            self.clipboard_append(result)
            self._status(f"✅ {to_fa_num(replaced_cnt)} مورد جایگزین شد ({to_fa_num(total_ready)} آماده) و کپی شد", "success")
        else:
            self._status(f"✅ {to_fa_num(replaced_cnt)} جایگزین شد (مجموع «ي» استاندارد: {to_fa_num(total_ready)})", "success")

    def _paste_and_convert(self):
        try:
            clip = self.clipboard_get()
        except tk.TclError:
            self._status("⚠ کلیپ‌بورد خالی است!", "warning")
            return

        self.txt_in.delete("1.0", "end")
        self.txt_in.insert("1.0", clip)
        self._on_input_change()
        self._convert(manual=True)

    def _clear(self):
        self.txt_in.delete("1.0", "end")
        self._set_output("")
        self.lbl_count.configure(text="جایگزینی انجام‌شده: ۰")
        self.lbl_chars.configure(text="کاراکترها: ۰  |  قابل تبدیل («ی» فارسی): ۰  |  «ي» عربی موجود: ۰")
        self._status("🗑 پاک شد", "subtext")

    def _copy_output(self):
        text = self.txt_out.get("1.0", "end-1c")
        if not text.strip():
            self._status("⚠ خروجی خالی است!", "warning")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self._status("✅ خروجی در کلیپ‌بورد کپی شد", "success")

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="انتخاب فایل متنی",
            filetypes=[("Text files", "*.txt"), ("Subtitle files", "*.srt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.txt_in.delete("1.0", "end")
            self.txt_in.insert("1.0", content)
            self._on_input_change()
            if not self.var_live.get():
                self._convert(manual=False)
            self._status(f"✅ بارگذاری شد: {os.path.basename(path)}", "success")
        except Exception as e:
            self._status(f"❌ خطا در بارگذاری: {e}", "error")

    def _save_file(self):
        text = self.txt_out.get("1.0", "end-1c")
        if not text.strip():
            self._status("⚠ خروجی برای ذخیره وجود ندارد!", "warning")
            return
        path = filedialog.asksaveasfilename(
            title="ذخیره فایل خروجی",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Subtitle files", "*.srt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self._status(f"✅ ذخیره شد: {os.path.basename(path)}", "success")
        except Exception as e:
            self._status(f"❌ خطا در ذخیره: {e}", "error")

    def _show_latin_error(self):
        win = tk.Toplevel(self)
        win.title("هشدار کاراکتر لاتین")
        win.geometry("460x300")
        win.resizable(False, False)
        win.configure(bg=self.c["error_bg"])
        win.transient(self)
        win.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 460) // 2
        y = self.winfo_y() + (self.winfo_height() - 300) // 2
        win.geometry(f"+{x}+{y}")

        tk.Label(
            win, text="⚠", font=Font(family=FONT_NAME, size=34),
            bg=self.c["error_bg"], fg=self.c["error_text"]
        ).pack(pady=(16, 4))

        tk.Label(
            win,
            text=(
                "متن حاوی حروف انگلیسی (لاتین) است!\n\n"
                "به دلیل باگ موتور متنی ادوبی، ترکیب همزمان\n"
                "فارسی و انگلیسی ممکن است باعث به‌هم‌ریختگی شود."
            ),
            font=Font(family=FONT_NAME, size=10),
            bg=self.c["error_bg"], fg=self.c["text"], justify="center"
        ).pack(pady=(0, 16))

        btn_frame = tk.Frame(win, bg=self.c["error_bg"])
        btn_frame.pack(pady=4)

        def remove_latin_and_convert():
            raw = self.txt_in.get("1.0", "end-1c")
            cleaned = strip_latin_letters(raw)
            self.txt_in.delete("1.0", "end")
            self.txt_in.insert("1.0", cleaned)
            win.destroy()
            self._on_input_change()
            self._convert(manual=True)

        def ignore_and_convert():
            self.var_block_latin.set(False)
            win.destroy()
            self._convert(manual=True)

        tk.Button(
            btn_frame, text="حذف انگلیسی و تبدیل",
            font=self.f_btn, bg=self.c["error_text"], fg="#FFFFFF",
            relief="flat", bd=0, padx=14, pady=7, command=remove_latin_and_convert
        ).pack(side="right", padx=6)

        tk.Button(
            btn_frame, text="تبدیل با حفظ انگلیسی",
            font=self.f_btn, bg=self.c["secondary"], fg="#FFFFFF",
            relief="flat", bd=0, padx=14, pady=7, command=ignore_and_convert
        ).pack(side="right", padx=6)

        tk.Button(
            win, text="انصراف",
            font=self.f_small, bg=self.c["surface"], fg=self.c["subtext"],
            relief="flat", bd=0, padx=22, pady=5, command=win.destroy
        ).pack(pady=(14, 0))

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title("درباره نرم‌افزار")
        win.geometry("440x400")
        win.resizable(False, False)
        win.configure(bg=self.c["bg"])
        win.transient(self)
        win.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 440) // 2
        y = self.winfo_y() + (self.winfo_height() - 400) // 2
        win.geometry(f"+{x}+{y}")

        hdr = tk.Frame(win, bg=self.c["header_bg"], height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="ℹ  درباره YeReplacer", font=self.f_title,
            bg=self.c["header_bg"], fg=self.c["title_text"], anchor="e"
        ).pack(side="right", padx=14, pady=10)

        body = tk.Frame(
            win, bg=self.c["surface"], bd=1, relief="solid",
            highlightthickness=1, highlightbackground=self.c["border"]
        )
        body.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(
            body, text="YeReplacer",
            font=Font(family=FONT_NAME, size=18, weight="bold"),
            bg=self.c["surface"], fg=self.c["primary"]
        ).pack(pady=(16, 2))

        tk.Label(
            body, text="نسخه ۲.۱  |  ابزار اصلاح متون فارسی برای ادوبی",
            font=self.f_small, bg=self.c["surface"], fg=self.c["subtext"]
        ).pack(pady=(0, 12))

        tk.Frame(body, bg=self.c["border"], height=1).pack(fill="x", padx=20, pady=(0, 12))

        tk.Label(
            body, text=COPYRIGHT_FA, font=self.f_small,
            bg=self.c["surface"], fg=self.c["text"], justify="center"
        ).pack(pady=(0, 8))

        tk.Label(
            body, text=COPYRIGHT_EN, font=Font(family=FONT_NAME, size=9),
            bg=self.c["surface"], fg=self.c["subtext"], justify="center"
        ).pack(pady=(0, 10))

        tk.Button(
            win, text="بستن", font=self.f_btn,
            bg=self.c["primary"], fg="#FFFFFF",
            relief="flat", bd=0, padx=28, pady=6,
            activebackground=self.c["primary_dark"], activeforeground="#FFFFFF",
            command=win.destroy
        ).pack(pady=(0, 12))


if __name__ == "__main__":
    app = YeReplacerApp()
    app.mainloop()
