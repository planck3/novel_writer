# 在文件开头导入 ttkbootstrap
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # 导入常量
import datetime
import os
import sys
import tkinter.font as tkfont
from fontTools.ttLib import TTFont
from PIL import Image, ImageTk

class NovelWriter:
    def __init__(self, root):
        self.root = root
        # 设置主题样式
        self.style = ttk.Style(theme="cosmo")
        self.root.title("简易小说txt写作工具")
        # 先设置一个临时大小
        temp_width = 700
        temp_height = 600
        self.root.geometry(f"{temp_width}x{temp_height}")

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # 计算窗口在屏幕偏右上的位置
        x = (screen_width - temp_width) // 2 + 85  # 增加 x 坐标使窗口右移
        y = max(0, (screen_height - temp_height) // 2 - 40)  # 减小 y 坐标使窗口上移
        # 设置窗口位置
        self.root.geometry(f"{temp_width}x{temp_height}+{x}+{y}")

        # 使用动态路径设置图标
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "static", "novel.ico")
        self.root.iconbitmap(icon_path)

        # 创建垂直滚动条
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 初始化文本内容
        self.font_size = 18
        try:
            # 尝试加载自定义字体
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(base_path, "static", "simsunb.ttf")
            font = TTFont(font_path)
            # 这里假设字体名称为 SimSun-Bold
            self.font = tkfont.Font(family="SimSun-Bold", size=self.font_size)
        except Exception as e:
            print(f"加载自定义字体失败: {e}")
            # 若加载失败，使用默认字体
            self.font = tkfont.Font(family="Arial", size=self.font_size)

        # 设置字体大小
        # 计算两个中文字体的宽度，假设中文字体宽度是英文字体两倍
        tab_width = self.font.measure('　' * 2) 
        self.text_content = tk.Text(self.root, wrap=tk.WORD, undo=True, yscrollcommand=scrollbar.set, font=self.font, tabs=tab_width)
        self.text_content.pack(expand=True, fill='both')

        # 将焦点设置到文本编辑区域
        self.text_content.focus_set()

        # 将滚动条与文本框关联
        scrollbar.config(command=self.text_content.yview)

        # 绑定文本修改事件，滚动到文本末尾并更新预览
        self.text_content.bind("<<Modified>>", self.on_text_modified)
        
        # 预览窗口相关变量
        self.preview_window = None
        self.preview_text = None
        self.chars_per_page = 200  # 每页显示的字符数
        self.current_page = 0
        self.preview_visible = False
        self.preview_button = None

        # 创建菜单栏
        self.create_menu()

        # 添加状态栏
        self.status_bar = ttk.Label(root, text="就绪", anchor=tk.W, bootstyle="secondary")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定快捷键
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-f>", self.open_find_replace)
        self.root.bind("<Control-p>", self.toggle_preview)

        # 初始化背景颜色
        self.text_content.config(bg="white")
        
        # 创建预览按钮
        self.create_preview_button()

    def create_preview_button(self):
        """创建预览按钮"""
        self.preview_button = ttk.Button(
            self.root, 
            text="显示预览", 
            command=self.toggle_preview,
            bootstyle="info-outline"
        )
        self.preview_button.place(x=10, y=10)

    def toggle_preview(self, event=None):
        """切换预览窗口的显示状态"""
        if self.preview_visible:
            self.hide_preview()
        else:
            self.show_preview()

    def show_preview(self):
        """显示预览窗口"""
        if self.preview_window is None or not self.preview_window.winfo_exists():
            # 创建新的预览窗口
            self.preview_window = tk.Toplevel(self.root)
            self.preview_window.title("小说预览")
            self.preview_window.geometry("250x400")
            
            # 设置窗口位置在主窗口左侧
            main_x = self.root.winfo_rootx()
            main_y = self.root.winfo_rooty()
            self.preview_window.geometry(f"+{main_x-260}+{main_y}")
            
            # 设置窗口样式
            self.preview_window.transient(self.root)  # 设置为主窗口的临时窗口
            self.preview_window.resizable(False, False)  # 禁止调整大小
            
            # 创建预览框架
            preview_frame = ttk.Frame(self.preview_window, padding=10)
            preview_frame.pack(fill='both', expand=True)
            
            # 创建书本样式的预览区域
            book_frame = ttk.Frame(preview_frame, bootstyle="danger")
            book_frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            # 创建预览文本区域
            preview_font = tkfont.Font(family=self.font.cget("family"), size=12)
            self.preview_text = tk.Text(
                book_frame, 
                wrap=tk.WORD, 
                font=preview_font,
                width=20,
                height=15,
                bg="#FFE4E1",
                relief="flat",
                padx=10,
                pady=10
            )
            self.preview_text.pack(fill='both', expand=True, padx=5, pady=5)
            self.preview_text.config(state=tk.DISABLED)  # 设置为只读
            
            # 创建翻页按钮
            btn_frame = ttk.Frame(preview_frame)
            btn_frame.pack(fill='x', pady=5)
            
            ttk.Button(
                btn_frame, 
                text="上一页", 
                command=self.prev_page,
                bootstyle="secondary-outline"
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                btn_frame, 
                text="下一页", 
                command=self.next_page,
                bootstyle="secondary-outline"
            ).pack(side=tk.RIGHT, padx=5)
            
            # 绑定关闭事件
            self.preview_window.protocol("WM_DELETE_WINDOW", self.hide_preview)
            
            # 更新预览内容
            self.update_preview()
        
        self.preview_visible = True
        self.preview_button.config(text="隐藏预览")

    def hide_preview(self):
        """隐藏预览窗口"""
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.withdraw()  # 隐藏窗口而不是销毁
        self.preview_visible = False
        self.preview_button.config(text="显示预览")

    def update_preview(self):
        """更新预览内容"""
        if not self.preview_window or not self.preview_window.winfo_exists():
            return
            
        # 获取当前文本内容
        content = self.text_content.get("1.0", "end-1c")
        
        # 计算总页数
        total_chars = len(content)
        total_pages = max(1, (total_chars + self.chars_per_page - 1) // self.chars_per_page)
        
        # 确保当前页在有效范围内
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
        
        # 计算当前页的内容范围
        start_char = self.current_page * self.chars_per_page
        end_char = min(start_char + self.chars_per_page, total_chars)
        
        # 更新预览文本
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        
        if total_chars > 0:
            page_content = content[start_char:end_char]
            self.preview_text.insert("1.0", page_content)
            
            # 添加页码信息
            page_info = f"\n\n--- 第 {self.current_page + 1} 页 / 共 {total_pages} 页 ---"
            self.preview_text.insert(tk.END, page_info)
        else:
            self.preview_text.insert("1.0", "开始创作您的小说...")
            
        self.preview_text.config(state=tk.DISABLED)

    def prev_page(self):
        """显示上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_preview()

    def next_page(self):
        """显示下一页"""
        content = self.text_content.get("1.0", "end-1c")
        total_chars = len(content)
        total_pages = max(1, (total_chars + self.chars_per_page - 1) // self.chars_per_page)
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_preview()

    def on_text_modified(self, event):
        """文本修改事件处理"""
        # 滚动到文本末尾
        self.text_content.see(tk.END)
        
        # 更新预览
        self.update_preview()
        
        # 自动翻页到最新内容
        content = self.text_content.get("1.0", "end-1c")
        total_chars = len(content)
        current_page_for_latest = total_chars // self.chars_per_page
        
        if current_page_for_latest != self.current_page and self.preview_visible:
            self.current_page = current_page_for_latest
            self.update_preview()
        
        # 重置修改标记
        self.text_content.edit_modified(False)

    def create_menu(self):
        # 主菜单栏
        menu_bar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        menu_bar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="查找/替换", command=self.open_find_replace, accelerator="Ctrl+F")
        edit_menu.add_command(label="显示/隐藏预览", command=self.toggle_preview, accelerator="Ctrl+P")
        menu_bar.add_cascade(label="编辑", menu=edit_menu)

        # 新增格式菜单
        format_menu = tk.Menu(menu_bar, tearoff=0)
        
        # 添加主题样式子菜单
        theme_menu = tk.Menu(format_menu, tearoff=0)
        themes = ['cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone', 
                 'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly', 
                 'superhero', 'solar', 'cyborg', 'vapor', 'simplex', 'cerculean']
        for theme in themes:
            theme_menu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))
        format_menu.add_cascade(label="主题样式", menu=theme_menu)

        font_size_menu = tk.Menu(format_menu, tearoff=0)
        for size in [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]:
            font_size_menu.add_command(label=f"{size} 号字体", command=lambda s=size: self.set_font_size(s))
        format_menu.add_cascade(label="字体大小", menu=font_size_menu)

        # 新增选择字体文件子菜单
        font_file_menu = tk.Menu(format_menu, tearoff=0)
        font_file_menu.add_command(label="选择字体文件", command=self.select_font_file)
        format_menu.add_cascade(label="选择字体", menu=font_file_menu)

        # 新增背景颜色子菜单
        bg_color_menu = tk.Menu(format_menu, tearoff=0)
        color_codes = [
            "#FFFFFF", "#F9DB91", "#F4CAE0", "#FFB6C1",
            "#A8E7DF", "#A3CFB3", "#92CBFC", "#BDA5E7",
            "#9370DB", "#8C92CF", "#72A9A5", "#EB99A7",
            "#EB96BD", "#FFAE8B", "#FF7F50", "#CA6174"
        ]

        # 为每个颜色创建一个小的图像
        for color in color_codes:
            img = Image.new('RGB', (85, 16), color)  # 调整尺寸
            photo = ImageTk.PhotoImage(img)
            bg_color_menu.add_command(image=photo, command=lambda c=color: self.set_bg_color(c))
            # 配置菜单项
            bg_color_menu.entryconfigure('end', compound='center',
                                       activebackground=color, background=color)
            setattr(bg_color_menu, f"img_{color}", photo)

        bg_color_menu.add_command(label="自定义颜色", command=self.custom_bg_color)
        format_menu.add_cascade(label="背景颜色", menu=bg_color_menu)

        # 预览设置子菜单
        preview_menu = tk.Menu(format_menu, tearoff=0)
        preview_menu.add_command(label="每页字数设置", command=self.set_chars_per_page)
        format_menu.add_cascade(label="预览设置", menu=preview_menu)

        menu_bar.add_cascade(label="格式", menu=format_menu)
        self.root.config(menu=menu_bar)

    def set_chars_per_page(self):
        """设置每页显示的字符数"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置每页字数")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        
        ttk.Label(
            dialog, 
            text="请输入每页显示的字符数:",
            bootstyle="secondary"
        ).pack(pady=(20, 10))
        
        entry = ttk.Entry(dialog, width=10, bootstyle="secondary")
        entry.insert(0, str(self.chars_per_page))
        entry.pack(pady=5)
        entry.select_range(0, tk.END)
        entry.focus_set()
        
        def on_ok():
            try:
                value = int(entry.get())
                if value > 0:
                    self.chars_per_page = value
                    self.current_page = 0  # 重置当前页
                    self.update_preview()
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "请输入大于0的数字")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
        
        ttk.Button(
            dialog, 
            text="确定", 
            command=on_ok,
            bootstyle="success-outline"
        ).pack(pady=10)
        
        # 绑定回车键
        dialog.bind("<Return>", lambda e: on_ok())

    def set_bg_color(self, color):
        self.text_content.config(bg=color)

    def custom_bg_color(self):
        try:
            # 弹出颜色选择对话框
            result = colorchooser.askcolor()
            # 检查用户是否选择了颜色
            if result and result[1]:
                # 获取所选颜色的十六进制表示
                color = result[1]
                # 设置文本编辑区域的背景颜色
                self.text_content.config(bg=color)
            else:
                print("用户未选择颜色")
        except Exception as e:
            # 打印异常信息
            print(f"选择颜色时出现错误: {e}")

    def change_theme(self, theme_name):
        """切换应用主题"""
        try:
            self.style.theme_use(theme_name)
            # 更新状态栏提示
            self.status_bar.config(text=f"已切换主题：{theme_name}")
        except Exception as e:
            messagebox.showerror("错误", f"切换主题失败：{str(e)}")

    def set_font_size(self, size):
        self.font_size = size
        self.font.configure(size=self.font_size)
        # 如果预览窗口存在，也更新预览字体
        if self.preview_text:
            preview_font = tkfont.Font(family=self.font.cget("family"), size=max(10, size-6))
            self.preview_text.configure(font=preview_font)

    def select_font_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("TrueType Fonts", "*.ttf"), ("OpenType Fonts", "*.otf")]
        )
        if file_path:
            try:
                # 这里需要额外的库来加载字体文件，比如 fontTools
                # 目前 tkinter 没有直接加载字体文件的方法
                # 这里只是简单提示
                messagebox.showinfo("提示", f"选择的字体文件: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", str(e))

    def save_file(self, event=None):
        # 获取当前日期
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文档", "*.txt"), ("All Files", "*.*")],
            initialfile=f"{current_date}.txt"  # 设置默认文件名
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                text = self.text_content.get(1.0, tk.END)
                f.write(text)
            self.status_bar.config(text=f"文件已保存：{file_path}")
        except Exception as e:
            messagebox.showerror("保存错误", str(e))

    def open_find_replace(self, event=None):
        FindReplaceWindow(self.root, self.text_content)

class FindReplaceWindow(tk.Toplevel):
    def __init__(self, parent, text_widget):
        super().__init__(parent)
        self.text = text_widget
        self.title("查找与替换")
        self.geometry("400x200")
        self.search_start = "1.0"  # 初始化搜索起始位置

        # 使用 ttkbootstrap 的样式
        ttk.Label(self, text="查找内容:", bootstyle="secondary").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.find_entry = ttk.Entry(self, width=30, bootstyle="secondary")
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="替换为:", bootstyle="secondary").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.replace_entry = ttk.Entry(self, width=30, bootstyle="secondary")
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)

        # 按钮框架
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # 使用 ttkbootstrap 的按钮样式
        ttk.Button(btn_frame, text="查找下一个", command=self.find_next, bootstyle="info-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="替换", command=self.replace, bootstyle="warning-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全部替换", command=self.replace_all, bootstyle="danger-outline").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=self.destroy, bootstyle="secondary-outline").pack(side=tk.RIGHT, padx=5)

        self.find_entry.focus_set()

    def find_next(self):
        target = self.find_entry.get()
        if not target:
            return

        start_pos = self.text.search(
            target, 
            self.search_start, 
            stopindex=tk.END,
            nocase=True
        )

        if start_pos:
            end_pos = f"{start_pos}+{len(target)}c"
            self.text.tag_remove("highlight", 1.0, tk.END)
            self.text.tag_add("highlight", start_pos, end_pos)
            self.text.tag_config("highlight", background="yellow")
            self.search_start = end_pos
            self.text.mark_set(tk.INSERT, start_pos)
            self.text.see(start_pos)
        else:
            messagebox.showinfo("提示", "已到达文档末尾")
            self.search_start = "1.0"

    def replace(self):
        target = self.find_entry.get()
        replace_text = self.replace_entry.get()

        if self.text.tag_ranges("highlight"):
            current_pos = self.text.index(tk.INSERT)
            self.text.delete(current_pos, f"{current_pos}+{len(target)}c")
            self.text.insert(current_pos, replace_text)
            self.find_next()

    def replace_all(self):
        target = self.find_entry.get()
        replace_text = self.replace_entry.get()

        content = self.text.get(1.0, tk.END)
        new_content = content.replace(target, replace_text)
        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, new_content)

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriter(root)
    root.mainloop()