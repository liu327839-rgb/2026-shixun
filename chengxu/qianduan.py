import os
import sqlite3
from datetime import datetime
from tkinter import Tk, StringVar, END, filedialog, messagebox
from tkinter import ttk

from PIL import Image as PillowImage
from PIL import ImageTk

from im import image_process
from onnx_infer import OnnxInferEngine
from queue_image import ImageQueue


# ==================== 全局状态 ====================
current_image_path = None
image_queue = ImageQueue()
DB_PATH = "recognition_history.db"

batch_total = 0
batch_done = 0
batch_running = False

try:
    engine = OnnxInferEngine()
    engine_error = None
except Exception as exc:
    engine = None
    engine_error = str(exc)


# ==================== 数据库 ====================
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recognition_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_result(image_path, class_name, confidence):
    file_name = os.path.basename(image_path)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO recognition_history
            (image_path, file_name, class_name, confidence, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (image_path, file_name, class_name, confidence, created_at),
        )
        conn.commit()


def search_history(keyword=""):
    keyword = keyword.strip()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if keyword:
            like_keyword = f"%{keyword}%"
            cursor.execute(
                """
                SELECT id, created_at, file_name, class_name, confidence, image_path
                FROM recognition_history
                WHERE file_name LIKE ? OR class_name LIKE ?
                ORDER BY id DESC
                """,
                (like_keyword, like_keyword),
            )
        else:
            cursor.execute(
                """
                SELECT id, created_at, file_name, class_name, confidence, image_path
                FROM recognition_history
                ORDER BY id DESC
                """
            )
        return cursor.fetchall()


# ==================== 图片与识别 ====================
def show_image_preview(image_path):
    try:
        image = PillowImage.open(image_path)
        image.thumbnail((500, 360), PillowImage.Resampling.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)

        image_preview.configure(image=image_tk, text="")
        image_preview.image = image_tk
        file_name_var.set(os.path.basename(image_path))
    except Exception as exc:
        image_preview.configure(image="", text="图片预览失败")
        image_preview.image = None
        messagebox.showerror("图片读取失败", str(exc))


def select_file():
    global current_image_path

    file_path = filedialog.askopenfilename(
        title="选择需要识别的图片",
        filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")],
    )
    if not file_path:
        return

    current_image_path = file_path
    show_image_preview(file_path)
    current_task_var.set(os.path.basename(file_path))
    status_var.set("图片已选择，等待识别")


def select_batch_files():
    global batch_total, batch_done, batch_running

    file_paths = filedialog.askopenfilenames(
        title="批量选择图片",
        filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")],
    )
    if not file_paths:
        return

    image_queue.clear()
    for file_path in file_paths:
        image_queue.enqueue(file_path)

    batch_total = len(file_paths)
    batch_done = 0
    batch_running = False

    progress_bar.configure(maximum=max(batch_total, 1), value=0)
    remaining_var.set(str(batch_total))
    current_task_var.set(os.path.basename(file_paths[0]))
    status_var.set(f"已导入 {batch_total} 张图片，等待批量识别")
    show_image_preview(file_paths[0])


def recognize_image(image_path):
    if engine is None:
        raise RuntimeError(f"模型未成功加载：{engine_error}")

    image_tensor = image_process(image_path)
    result = engine.predict(image_tensor)
    return result["class_name"], result["confidence"]


def show_recognition_result(label, confidence):
    result_var.set(label)
    confidence_var.set(f"{confidence * 100:.2f}%")


def start_recognize():
    if current_image_path is None:
        messagebox.showwarning("提示", "请先选择一张图片")
        return

    status_var.set("正在识别，请稍候……")
    root.update_idletasks()

    try:
        label, confidence = recognize_image(current_image_path)
        show_recognition_result(label, confidence)
        save_result(current_image_path, label, confidence)
        refresh_history_table()
        status_var.set("单张图片识别完成")
    except Exception as exc:
        status_var.set("识别失败")
        result_var.set("识别失败")
        confidence_var.set("--")
        messagebox.showerror("识别失败", str(exc))


def start_batch_recognize():
    global batch_running

    if image_queue.is_empty():
        messagebox.showwarning("提示", "请先批量导入图片")
        return

    if batch_running:
        return

    batch_running = True
    batch_recognize_button.state(["disabled"])
    select_batch_button.state(["disabled"])
    process_next_image()


def process_next_image():
    global batch_done, batch_running

    if image_queue.is_empty():
        batch_running = False
        batch_recognize_button.state(["!disabled"])
        select_batch_button.state(["!disabled"])
        current_task_var.set("无")
        remaining_var.set("0")
        status_var.set(f"批量识别完成，共处理 {batch_done} 张图片")
        return

    image_path = image_queue.dequeue()
    file_name = os.path.basename(image_path)

    current_task_var.set(file_name)
    remaining_var.set(str(len(image_queue.items)))
    status_var.set(f"正在识别：{file_name}")
    show_image_preview(image_path)
    root.update_idletasks()

    try:
        label, confidence = recognize_image(image_path)
        show_recognition_result(label, confidence)
        save_result(image_path, label, confidence)
    except Exception as exc:
        result_var.set("识别失败")
        confidence_var.set("--")
        print(f"批量识别失败：{file_name}，原因：{exc}")

    batch_done += 1
    progress_bar.configure(value=batch_done)
    refresh_history_table()

    # 适当留出时间给界面刷新，答辩演示时更加直观
    root.after(500, process_next_image)


# ==================== 历史记录 ====================
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
                image_path,
            ),
        )

    history_count_var.set(f"共 {len(rows)} 条记录")


def search_from_entry():
    refresh_history_table(search_var.get())


# ==================== 界面布局 ====================
init_db()

root = Tk()
root.title("AI 图片识别工具")
root.geometry("1180x820+120+40")
root.minsize(980, 700)

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

style = ttk.Style(root)
try:
    style.theme_use("clam")
except Exception:
    pass

style.configure("Title.TLabel", font=("微软雅黑", 22, "bold"))
style.configure("SubTitle.TLabel", font=("微软雅黑", 10), foreground="#5B6472")
style.configure("Section.TLabel", font=("微软雅黑", 12, "bold"))
style.configure("InfoName.TLabel", font=("微软雅黑", 10), foreground="#667085")
style.configure("InfoValue.TLabel", font=("微软雅黑", 12, "bold"))
style.configure("Result.TLabel", font=("微软雅黑", 18, "bold"), foreground="#175CD3")
style.configure("Primary.TButton", font=("微软雅黑", 11, "bold"), padding=(18, 9))
style.configure("Normal.TButton", font=("微软雅黑", 11), padding=(18, 9))
style.configure("Treeview", font=("微软雅黑", 9), rowheight=27)
style.configure("Treeview.Heading", font=("微软雅黑", 9, "bold"))

# 变量
status_var = StringVar(value="等待操作")
current_task_var = StringVar(value="无")
remaining_var = StringVar(value="0")
result_var = StringVar(value="等待识别")
confidence_var = StringVar(value="--")
file_name_var = StringVar(value="尚未选择图片")
search_var = StringVar()
history_count_var = StringVar(value="共 0 条记录")

# 顶部标题区
header_frame = ttk.Frame(root, padding=(24, 18, 24, 10))
header_frame.grid(row=0, column=0, sticky="ew")
header_frame.columnconfigure(0, weight=1)

ttk.Label(header_frame, text="AI 图片识别工具", style="Title.TLabel").grid(
    row=0, column=0, sticky="w"
)
ttk.Label(
    header_frame,
    text="本地图像分类 · 单图识别 · 批量队列 · 历史记录",
    style="SubTitle.TLabel",
).grid(row=1, column=0, sticky="w", pady=(4, 0))

# 主体容器
main_frame = ttk.Frame(root, padding=(24, 8, 24, 20))
main_frame.grid(row=1, column=0, sticky="nsew")
main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=2)
main_frame.rowconfigure(1, weight=1)
main_frame.rowconfigure(2, weight=1)

# 操作按钮区：四个按钮横向排列，左右分组
operation_frame = ttk.LabelFrame(main_frame, text="操作区", padding=12)
operation_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
for index in range(4):
    operation_frame.columnconfigure(index, weight=1)

select_button = ttk.Button(
    operation_frame,
    text="选择单张图片",
    command=select_file,
    style="Normal.TButton",
)
select_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

start_button = ttk.Button(
    operation_frame,
    text="开始单图识别",
    command=start_recognize,
    style="Primary.TButton",
)
start_button.grid(row=0, column=1, sticky="ew", padx=6)

select_batch_button = ttk.Button(
    operation_frame,
    text="批量导入图片",
    command=select_batch_files,
    style="Normal.TButton",
)
select_batch_button.grid(row=0, column=2, sticky="ew", padx=6)

batch_recognize_button = ttk.Button(
    operation_frame,
    text="开始批量识别",
    command=start_batch_recognize,
    style="Primary.TButton",
)
batch_recognize_button.grid(row=0, column=3, sticky="ew", padx=(6, 0))

# 左侧图片预览区
preview_frame = ttk.LabelFrame(main_frame, text="图片预览", padding=12)
preview_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 12))
preview_frame.columnconfigure(0, weight=1)
preview_frame.rowconfigure(0, weight=1)

image_preview = ttk.Label(
    preview_frame,
    text="请点击上方按钮选择图片",
    anchor="center",
    justify="center",
)
image_preview.grid(row=0, column=0, sticky="nsew")

ttk.Separator(preview_frame, orient="horizontal").grid(
    row=1, column=0, sticky="ew", pady=10
)
ttk.Label(preview_frame, textvariable=file_name_var, anchor="center").grid(
    row=2, column=0, sticky="ew"
)

# 右侧状态与结果区
info_frame = ttk.LabelFrame(main_frame, text="识别信息", padding=16)
info_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 12))
info_frame.columnconfigure(1, weight=1)

info_items = [
    ("运行状态", status_var),
    ("当前任务", current_task_var),
    ("剩余数量", remaining_var),
]

for row_index, (name, variable) in enumerate(info_items):
    ttk.Label(info_frame, text=name, style="InfoName.TLabel").grid(
        row=row_index, column=0, sticky="w", pady=8
    )
    ttk.Label(info_frame, textvariable=variable, style="InfoValue.TLabel").grid(
        row=row_index, column=1, sticky="e", pady=8
    )

progress_bar = ttk.Progressbar(info_frame, mode="determinate", maximum=1, value=0)
progress_bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 16))

ttk.Separator(info_frame, orient="horizontal").grid(
    row=4, column=0, columnspan=2, sticky="ew", pady=8
)

ttk.Label(info_frame, text="识别结果", style="InfoName.TLabel").grid(
    row=5, column=0, columnspan=2, pady=(14, 4)
)
ttk.Label(info_frame, textvariable=result_var, style="Result.TLabel").grid(
    row=6, column=0, columnspan=2, pady=6
)
ttk.Label(info_frame, text="置信度", style="InfoName.TLabel").grid(
    row=7, column=0, columnspan=2, pady=(18, 4)
)
ttk.Label(info_frame, textvariable=confidence_var, style="Result.TLabel").grid(
    row=8, column=0, columnspan=2, pady=6
)

# 下方历史记录区
history_frame = ttk.LabelFrame(main_frame, text="历史识别记录", padding=12)
history_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
history_frame.columnconfigure(0, weight=1)
history_frame.rowconfigure(1, weight=1)

search_frame = ttk.Frame(history_frame)
search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
search_frame.columnconfigure(0, weight=1)

search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("微软雅黑", 10))
search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
search_entry.bind("<Return>", lambda event: search_from_entry())

search_button = ttk.Button(search_frame, text="查找", command=search_from_entry)
search_button.grid(row=0, column=1, padx=4)

show_all_button = ttk.Button(
    search_frame,
    text="显示全部",
    command=lambda: (search_var.set(""), refresh_history_table()),
)
show_all_button.grid(row=0, column=2, padx=4)

ttk.Label(search_frame, textvariable=history_count_var).grid(
    row=0, column=3, padx=(14, 0)
)

# Treeview及滚动条
tree_container = ttk.Frame(history_frame)
tree_container.grid(row=1, column=0, sticky="nsew")
tree_container.columnconfigure(0, weight=1)
tree_container.rowconfigure(0, weight=1)

history_tree = ttk.Treeview(
    tree_container,
    columns=("id", "time", "file", "class", "confidence", "path"),
    show="headings",
    height=8,
)

columns = {
    "id": ("编号", 60, "center"),
    "time": ("识别时间", 150, "center"),
    "file": ("图片名", 170, "w"),
    "class": ("识别结果", 150, "center"),
    "confidence": ("置信度", 90, "center"),
    "path": ("图片路径", 380, "w"),
}

for column_name, (title, width, anchor) in columns.items():
    history_tree.heading(column_name, text=title)
    history_tree.column(column_name, width=width, anchor=anchor)

vertical_scrollbar = ttk.Scrollbar(
    tree_container, orient="vertical", command=history_tree.yview
)
horizontal_scrollbar = ttk.Scrollbar(
    tree_container, orient="horizontal", command=history_tree.xview
)
history_tree.configure(
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set,
)

history_tree.grid(row=0, column=0, sticky="nsew")
vertical_scrollbar.grid(row=0, column=1, sticky="ns")
horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

refresh_history_table()

if engine_error:
    status_var.set("模型加载失败，请检查模型路径")

root.mainloop()