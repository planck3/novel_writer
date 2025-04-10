import tkinter as tk
from tkinter import filedialog, messagebox

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                text = text_area.get("1.0", tk.END)
                file.write(text)
            messagebox.showinfo("保存成功", "文件已成功保存。")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存文件时出错: {e}")

def find_and_replace():
    find_dialog = tk.Toplevel(root)
    find_dialog.title("查找替换")

    tk.Label(find_dialog, text="查找:").grid(row=0, column=0)
    find_entry = tk.Entry(find_dialog)
    find_entry.grid(row=0, column=1)

    tk.Label(find_dialog, text="替换为:").grid(row=1, column=0)
    replace_entry = tk.Entry(find_dialog)
    replace_entry.grid(row=1, column=1)

    def perform_replace():
        find_text = find_entry.get()
        replace_text = replace_entry.get()
        content = text_area.get("1.0", tk.END)
        new_content = content.replace(find_text, replace_text)
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", new_content)
        find_dialog.destroy()

    tk.Button(find_dialog, text="替换", command=perform_replace).grid(row=2, column=0, columnspan=2)

root = tk.Tk()
root.title("简易小说写作工具")

# 创建菜单栏
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="保存", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="退出", command=root.quit)
menu_bar.add_cascade(label="文件", menu=file_menu)

edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="查找替换", command=find_and_replace)
menu_bar.add_cascade(label="编辑", menu=edit_menu)

root.config(menu=menu_bar)

# 创建文本编辑区域
text_area = tk.Text(root, wrap=tk.WORD)
text_area.pack(fill=tk.BOTH, expand=True)

root.mainloop()
