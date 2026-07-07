from tkinter import *
root = Tk()
root.title("ai图片识别工具")
root.geometry("1200x900+300+50")
yongtu = Label(root, text="ai图片识别工具",font=("微软雅黑", 20), fg="black")
yongtu.pack()
renwu = Label(root, text="请在下方放入你所需要识别的图片",font=("微软雅黑", 15), fg="red")
renwu.pack()
root.mainloop()

