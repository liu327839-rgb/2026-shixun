import os
from tkinter import *
from tkinter import filedialog, ttk
from PIL import ImageTk, Image as pillow
current_image_path = None
def select_file():
    global current_image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if file_path:
        current_image_path = file_path
        img = pillow.open(file_path)
        img.thumbnail((400, 400))
        img_tk = ImageTk.PhotoImage(img)
        image_preview.image = img_tk
        image_preview.config(image=img_tk)
def recognize_image(image_path):
    label = "假的例子：猫"
    confidence = 0.95
    return label, confidence
def start_recognize():
    if current_image_path is None:
        result_label.config(text="请先选择图片")
        confidence_label.config(text="置信度：--")
        return
    
    label, confidence = recognize_image(current_image_path)
    result_label.config(text="识别结果：" + label)
    confidence_label.config(text=f"置信度：{confidence * 100:.2f}%")
        
root = Tk()
root.title("ai图片识别工具")
root.geometry("1200x900+300+50")
yongtu = Label(root, text="ai图片识别工具",font=("微软雅黑", 20), fg="black")
yongtu.pack()
renwu = Label(root, text="请在下方放入你所需要识别的图片",font=("微软雅黑", 15), fg="red")
renwu.pack()
xuanze = Button(root, text="选择图片", font=("微软雅黑", 15), fg="black", command=select_file)
xuanze.pack()
image_preview = Label(root)
image_preview.pack()
shibie = Button(root, text="开始识别", font=("微软雅黑", 15), fg="black", command=start_recognize)
shibie.pack()
result_label = Label(root, text="识别结果：等待中", font=("微软雅黑", 15), fg="black")
result_label.pack()
confidence_label = Label(root, text="置信度：--", font=("微软雅黑", 15), fg="black")
confidence_label.pack()
root.mainloop()

