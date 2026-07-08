import os
import queue
import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import filedialog, ttk
from PIL import ImageTk, Image as pillow
from queue_image import ImageQueue

current_image_path = None
image_queue = ImageQueue()
DB_path = "recognition_history.db"

def init_db():
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recognition_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        class_name TEXT NOT NULL,
        confidence REAL NOT NULL,
        created_at TEXT NOT NULL
    )
""")
    conn.commit()
    conn.close()

def save_result(image_path, class_name, confidence):
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    file_name = os.path.basename(image_path)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO recognition_history 
        (image_path, file_name, class_name, confidence, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (image_path, file_name, class_name, confidence, created_at))

    conn.commit()
    conn.close()

def search_history(keyword=""):
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    keyword = keyword.strip()
    if keyword:
        like_keyword = f"%{keyword}%"
        cursor.execute("""
            SELECT id, created_at, file_name, class_name, confidence, image_path
            FROM recognition_history
            WHERE file_name LIKE ? OR class_name LIKE ?
            ORDER BY id DESC
        """, (like_keyword, like_keyword))
    else:
        cursor.execute("""
            SELECT id, created_at, file_name, class_name, confidence, image_path
            FROM recognition_history
            ORDER BY id DESC
        """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def select_batch_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if not file_paths:
        return
    image_queue.clear()
    for file_path in file_paths:
        image_queue.enqueue(file_path)
    status_label.config(text="状态：批量图片导入成功")
    current_task_label.config(text=f"当前任务:{current_image_path if current_image_path else '无'}")
    remaining_label.config(text=f"剩余图片数量：{len(image_queue.items)}")
    show_image_preview(file_paths[0])

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

    save_result(image_path, label, confidence)
    refresh_history_table()
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
        show_image_preview(file_path)
        current_task_label.config(text=f"当前任务:{os.path.basename(file_path)}")

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

    save_result(current_image_path, label, confidence)
    refresh_history_table()

def refresh_history_table(keyword=""):
    rows = search_history(keyword)

    for item in history_tree.get_children():
        history_tree.delete(item)

    for row in rows:
        id_, created_at, file_name, class_name, confidence, image_path = row
        history_tree.insert(
            "",
            END,
            values=(
                id_,
                created_at,
                file_name,
                class_name,
                f"{confidence * 100:.2f}%",
                image_path
            )
        )
        
init_db()

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

history_title = Label(root, text="历史识别结果", font=("微软雅黑", 16), fg="black")
history_title.pack(pady=5)

search_frame = Frame(root)
search_frame.pack()

search_entry = Entry(search_frame, font=("微软雅黑", 12), width=30)
search_entry.pack(side=LEFT, padx=5)

search_button = Button(
    search_frame,
    text="查找",
    font=("微软雅黑", 12),
    command=lambda: refresh_history_table(search_entry.get())
)
search_button.pack(side=LEFT, padx=5)

show_all_button = Button(
    search_frame,
    text="显示全部",
    font=("微软雅黑", 12),
    command=lambda: refresh_history_table()
)
show_all_button.pack(side=LEFT, padx=5)

history_tree = ttk.Treeview(
    root,
    columns=("id", "time", "file", "class", "confidence", "path"),
    show="headings",
    height=8
)

history_tree.heading("id", text="编号")
history_tree.heading("time", text="识别时间")
history_tree.heading("file", text="图片名")
history_tree.heading("class", text="识别结果")
history_tree.heading("confidence", text="置信度")
history_tree.heading("path", text="图片路径")

history_tree.column("id", width=50)
history_tree.column("time", width=150)
history_tree.column("file", width=180)
history_tree.column("class", width=120)
history_tree.column("confidence", width=100)
history_tree.column("path", width=350)

history_tree.pack(pady=10)

refresh_history_table()

root.mainloop()