import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime

class NovelWriter:
    def __init__(self, root):
        self.root = root
        self.root.title("简易小说写作工具")
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
        print(f"屏幕宽度: {screen_width}, 屏幕高度: {screen_height}")
        print(f"计算得到的 x 坐标: {x}, y 坐标: {y}")
        # 设置窗口位置
        self.root.geometry(f"{temp_width}x{temp_height}+{x}+{y}")

        # 多次调用 update_idletasks 确保布局稳定
        for _ in range(3):
            self.root.update_idletasks()

        # 创建垂直滚动条
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 初始化文本内容
        self.text_content = tk.Text(self.root, wrap=tk.WORD, undo=True, yscrollcommand=scrollbar.set)
        self.text_content.pack(expand=True, fill='both')

        # 将滚动条与文本框关联
        scrollbar.config(command=self.text_content.yview)

        # 创建菜单栏
        self.create_menu()

        # 添加状态栏
        self.status_bar = ttk.Label(root, text="就绪", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定快捷键
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-f>", self.open_find_replace)

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
        menu_bar.add_cascade(label="编辑", menu=edit_menu)

        self.root.config(menu=menu_bar)

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

        # 当前搜索位置
        self.search_start = "1.0"

        # 创建界面元素
        ttk.Label(self, text="查找内容:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.find_entry = ttk.Entry(self, width=30)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="替换为:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.replace_entry = ttk.Entry(self, width=30)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)

        # 按钮框架
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="查找下一个", command=self.find_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="替换", command=self.replace).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全部替换", command=self.replace_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=self.destroy).pack(side=tk.RIGHT, padx=5)

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