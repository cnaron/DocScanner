# app/main.py
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from runner import run_batch

APP_TITLE = "DocScanner 批量去畸变（双击即用）"
DEFAULT_OUTPUT = "output"

def choose_input_dir(var):
    path = filedialog.askdirectory(title="选择输入文件夹（包含多张书页图片）")
    if path:
        var.set(path)

def choose_output_dir(var):
    path = filedialog.askdirectory(title="选择输出文件夹（将写入处理结果）")
    if path:
        var.set(path)

def start_process(btn, in_var, out_var, log_box):
    in_dir = in_var.get().strip()
    out_dir = out_var.get().strip() or DEFAULT_OUTPUT
    if not in_dir or not os.path.isdir(in_dir):
        messagebox.showwarning("提示", "请先选择有效的输入文件夹")
        return
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    btn.config(state=tk.DISABLED)
    log_box.delete(1.0, tk.END)
    log_box.insert(tk.END, f"开始处理...\n输入：{in_dir}\n输出：{out_dir}\n\n")

    def task():
        try:
            ok, fail = run_batch(in_dir, out_dir, log_fn=lambda s: log_box.insert(tk.END, s))
            log_box.insert(tk.END, f"\n=== 完成 ===\n成功：{ok}，失败：{fail}\n")
            messagebox.showinfo("完成", f"处理完成：成功 {ok}，失败 {fail}")
        except Exception as e:
            messagebox.showerror("错误", f"运行失败：{e}")
        finally:
            btn.config(state=tk.NORMAL)

    threading.Thread(target=task, daemon=True).start()

def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("680x420")

    in_var = tk.StringVar()
    out_var = tk.StringVar(value=DEFAULT_OUTPUT)

    frm = tk.Frame(root, padx=12, pady=12)
    frm.pack(fill=tk.BOTH, expand=True)

    tk.Label(frm, text="输入文件夹（含书页图片）").grid(row=0, column=0, sticky="w")
    tk.Entry(frm, textvariable=in_var, width=60).grid(row=0, column=1, padx=6)
    tk.Button(frm, text="浏览...", command=lambda: choose_input_dir(in_var)).grid(row=0, column=2)

    tk.Label(frm, text="输出文件夹").grid(row=1, column=0, sticky="w", pady=(8,0))
    tk.Entry(frm, textvariable=out_var, width=60).grid(row=1, column=1, padx=6, pady=(8,0))
    tk.Button(frm, text="浏览...", command=lambda: choose_output_dir(out_var)).grid(row=1, column=2, pady=(8,0))

    log_box = tk.Text(frm, height=15)
    log_box.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(12,0))
    frm.grid_rowconfigure(2, weight=1)
    frm.grid_columnconfigure(1, weight=1)

    start_btn = tk.Button(frm, text="开始处理", command=lambda: start_process(start_btn, in_var, out_var, log_box))
    start_btn.grid(row=3, column=0, columnspan=3, pady=12)

    tk.Label(frm, text="说明：将多张 JPG/PNG/TIFF 放在一个文件夹中，输出会按原文件名生成校正后的图像。").grid(row=4, column=0, columnspan=3, sticky="w")
    root.mainloop()

if __name__ == "__main__":
    main()
