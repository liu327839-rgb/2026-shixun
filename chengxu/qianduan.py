import os
import queue
from tkinter import *
from tkinter import filedialog, ttk
from PIL import ImageTk, Image as pillow
from queue_image import ImageQueue
current_image_path = None
image_queue = ImageQueue()

def  select_batch_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if not file_paths:
        return
    image_queue.clear()
    for file_path in file_paths:
        image_queue.enqueue(file_path)
    status_label.config(text="状态：批量图片导入成功")
    current_task_label.config(text=f"当前任务:{current_image_path if current_image_path else '无'}")
    remaining_label.config(text=f"剩余图片数量：{len(image_queue.items)}")

def process_next_image():
    if image_queue.is_empty():
        status_label.config(text="状态：没有更多图片需要识别")
        current_task_label.config(text="当前任务:无")
        remaining_label.config(text="剩余图片数量：0")
        return
    image_path = image_queue.dequeue()
    file_name = os.path.basename(image_path)
    current_task_label.config(text=f"当前任务:{file_name}")
    remaining_label.config(text=f"剩余图片数量：{len(image_queue.items)}")
    status_label.config(text=f"状态：正在识别 {file_name}...")
    show_image_preview(image_path)
    root.update_idletasks()
    label, confidence = recognize_image(image_path)
    result_label.config(text="识别结果：" + label)
    confidence_label.config(text=f"置信度：{confidence * 100:.2f}%")
    root.after(2000, process_next_image)

def show_image_preview(image_path):
    img = pillow.open(image_path)
    img.thumbnail((400, 400))
    img_tk = ImageTk.PhotoImage(img)
    image_preview.image = img_tk
    image_preview.config(image=img_tk)

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
batch_button = Button(root, text="批量导入图片", font=("微软雅黑", 15), fg="black", command=select_batch_files)
batch_button.pack()
image_preview = Label(root)
image_preview.pack()
shibie = Button(root, text="开始识别", font=("微软雅黑", 15), fg="black", command=start_recognize)
shibie.pack()
batch_shibie = Button(root, text="批量识别", font=("微软雅黑", 15), fg="black", command=process_next_image)
batch_shibie.pack()
status_label = Label(root,text="状态：等待中", font=("微软雅黑", 15), fg="black")
status_label.pack()
current_task_label = Label(root,text="当前任务:无", font=("微软雅黑", 15), fg="black")
current_task_label.pack()
remaining_label = Label(root,text="剩余图片数量：0", font=("微软雅黑", 15), fg="black")
remaining_label.pack()
result_label = Label(root, text="识别结果：等待中", font=("微软雅黑", 15), fg="black")
result_label.pack()
confidence_label = Label(root, text="置信度：--", font=("微软雅黑", 15), fg="black")
confidence_label.pack()
root.mainloop()

