# -*- coding : utf-8-*-
import signal
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import json
import cv2
import os
from shutil import rmtree
from PIL import Image, ImageTk
import math
import time
import _thread
import threading
import ctypes
# from mpl_toolkits import mplot3d
# import  matplotlib.pyplot as plt
# import keyboard


class LabelTool:
    def __init__(self, master):
        self.parent = master
        self.parent.title('掩码标注工具软件')
        self.parent.geometry('880x820')
        self.frame = tk.Frame(self.parent, takefocus=True)
        self.frame.pack(fill='both', expand=True)

        # entry定义
        self.entry_list = [tk.Entry(self.frame) for i in range(16)]  # 显示mask点
        self.entry_content = [tk.StringVar() for i in range(16)]
        for i in range(16):
            self.entry_list[i].config(textvariable=self.entry_content[i])


        # 参数定义
        self.annot_frame_index = [tk.IntVar() for i in range(21)]
        self.annot_frame_entry = [tk.Entry(self.frame, state=tk.DISABLED) for i in range(21)]
        for i in range(21):
            self.annot_frame_index[i].set(-1)
            self.annot_frame_entry[i].config(textvariable=self.annot_frame_index[i])

        self.videoPath = ''  # 选中的视频的路径
        self.current = 0  # 当前帧（当前帧current与显示的帧序号i的关系是：i = current + 1）
        self.start = False  # 是否开始处理视频
        self.rad = 3.0  # 标注点的半径
        self.image_height = 680
        self.image_width = 360
        self.original_height = 0
        self.original_width = 0
        self.frame_count = 0
        self.frame_rate = 0.0
        self.filename = ''
        self.first = 0  # 起始帧位置，初始为0

        self.img = []  # 缓存每一帧图片
        self.show = True  # true时显示当前关键点，false时不显示

        # radiobutton定义


        # checkbutton定义



        # button定义
        # self.bt = tk.Button(self.frame, text="更改json输出路径", command=self.change_output_path)
        self.bt0 = tk.Button(self.frame, text="选择视频", command=self.select_path)
        self.bt2 = tk.Button(self.frame, text="重置当前帧", command=self.reset_coordinate, takefocus=False)
        self.bt3 = tk.Button(self.frame, text="上一帧图像", command=self.previous_image, takefocus=False)
        self.bt4 = tk.Button(self.frame, text="下一帧图像", command=self.next_image, takefocus=False)
        self.bt5 = tk.Button(self.frame, text="保存输出文件", command=self.save_file)
        # self.bt6 = tk.Button(self.frame, text="使用说明", command=self.info)
        # self.bt7 = tk.Button(self.frame, text="更改默认输入路径", command=self.change_input_path)
        # self.bt8 = tk.Button(self.frame, text='更改视频输出路径', command=self.change_video_path)
        self.bt9 = tk.Button(self.frame, text='更改软件配置', command=self.config_software, takefocus=False)
        self.bt_list = [tk.Button(self.frame, text='clear') for i in range(8)]

        # label定义
        self.label1 = tk.Label(self.frame, font=200, text="帧序号：" + "0/0")
        self.label2 = tk.Label(self.frame, font=200, text="视频编号：")
        # self.label3 = tk.Label(self.frame, font=200)  # 输出路径。已弃用
        # self.label8 = tk.Label(self.frame, font=150, text="", background="red")
        self.label9 = tk.Label(self.frame, font=200, text="帧率：")
        self.label10 = tk.Label(self.frame, font=200, text="")
        self.label11 = tk.Label(self.frame, font=300, text="手掌点（两个以上）")
        self.label12 = tk.Label(self.frame, font=300, text="背景点（三个以上）")

        # 两个画布定义
        self.panel0 = tk.Canvas(self.frame, bg="lightgrey", height=740, width=420)
        self.panel = tk.Canvas(self.frame, bg="lightgrey", height=680, width=360)

        # 创建scrollbar，有bug
        # self.sb = tk.Scrollbar(self.frame)
        # self.sb.pack(side='right', fill='y')
        # self.sb.config(command=self.parent_canvas.yview)
        # self.parent_canvas.config(yscrollcommand=self.sb.set)
        # self.parent_canvas.create_window(0, 0, window=self.frame)

        # 输入输出路径等的定义、创建默认文件夹和config.json
        self.output_path = tk.StringVar()
        self.input_path = tk.StringVar()
        self.multi_thread = tk.BooleanVar()
        self.into_memory = tk.BooleanVar()  # 帧缓存是否写入内存
        self.into_memory_ = True  # 保证状态一致
        self.read_config_file()

        # 组件绑定函数
        self.panel.bind("<Button-1>", self.on_click)
        self.panel.bind("<Button-3>", self.on_click_r)
        self.panel.bind("<MouseWheel>", self.on_mousewheel)
        self.panel0.bind("<MouseWheel>", self.on_mousewheel)
        self.frame.bind("<MouseWheel>", self.on_mousewheel)
        self.frame.bind("<KeyPress>", self.on_keyboard)
        self.frame.bind("<Button-1>", self.focus_on_frame)
        self.frame.bind("<Destroy>", self.when_frame_destroy)
        for i in range(16):
            self.entry_list[i].bind("<KeyPress>", self.on_keyboard_entry)
            if i % 2 == 0:
                self.bt_list[i // 2].bind("<Button-1>", lambda event, i=i: self.on_clear_bt(event, i//2))

        # 变量绑定回调函数
        for i in range(16):
            self.entry_content[i].trace_variable("w", self.callback_entry)
        self.multi_thread.trace('w', self.callback_multi_thread)
        self.into_memory.trace('w', self.callback_into_memory)


        self.layout()
        self.frame.focus_set()


    def layout(self):
        # entry_list（关键点坐标）、rb（关键点index）、label（关键点说明label）
        # 第一部分
        j = 0
        for i in range(0, 8):
            self.entry_list[i].place(x=620 + 80 * (i % 2), y=100 + 20 * (i - (i % 2)), width=60, height=16)
            if (i % 2) == 0:
                j += 1
                la = tk.Label(self.frame, text=str(j), bg="green")
                la.place(x=595, y=100 + 20 * i)
                self.bt_list[i // 2].place(x=540, y=95 + 20 * i, width=50, height=31)
        # 第二部分
        # j = 4
        for i in range(8, 16):
            self.entry_list[i].place(x=620 + 80 * (i % 2), y=150 + 20 * (i - (i % 2)), width=60, height=16)
            if (i % 2) == 0:
                j += 1
                la = tk.Label(self.frame, text=str(j - 4), bg="red")
                la.place(x=595, y=150 + 20 * i)
                self.bt_list[i // 2].place(x=540, y=145 + 20 * i, width=50, height=31)

        for i in range(3):
            text = ['第一组(连续)', '第二组(连续)', '第三组(连续)']
            la = tk.Label(self.frame, text=text[i], font=300)
            la.place(x=540, y=510 + i * 100)
            for j in range(7):
                self.annot_frame_entry[i * 7 + j].place(x=460 + j * 30, y=540 + i * 100, width=30, height=30)


        # checkbutton布局
        # self.cb.place(x=470, y=770)  # 辅助网格线
        # self.cb1.place(x=750, y=35)  # 复杂场景
        # self.cb3.place(x=20, y=30)  # 十秒视频起始帧

        # button布局
        self.bt0.place(x=700, y=530, width=140, height=31)  # 选择视频
        self.bt2.place(x=700, y=570, width=140, height=31)  # 重置当前帧坐标
        self.bt3.place(x=700, y=610, width=140, height=31)  # 上一帧图像
        self.bt4.place(x=700, y=650, width=140, height=31)  # 下一帧图像
        # self.bt1.place(x=700, y=690, width=140, height=31)  # test
        self.bt5.place(x=700, y=730, width=140, height=31)  # 保存输出文件和视频
        # self.bt.place(x=710, y=730, width=140, height=31)  # 更改json输出路径
        # self.bt8.place(x=710, y=690, width=140, height=31)  # 更改视频输出路径
        # self.bt7.place(x=710, y=770, width=140, height=31)  # 更改默认输入路径
        self.bt9.place(x=700, y=770, width=140, height=31)  # 修改软件配置

        # label布局
        self.label1.place(x=240, y=5)  # 帧序号
        self.label2.place(x=20, y=5)  # 视频编号
        self.label11.place(x=660, y=70)
        self.label12.place(x=660, y=280)


        # 画布布局
        self.panel0.place(x=20, y=60, anchor="nw")  # 底层画布
        self.panel.place(x=50, y=90, anchor="nw")  # 顶层画布

    def read_config_file(self):
        if not os.path.exists('./mask_output'):  # 初始输出文件夹
            os.mkdir('./mask_output')
        if not os.path.exists('./temp'):
            os.mkdir('./temp')
        if os.path.exists('./path.json'):
            os.remove('./path.json')
        if os.path.exists('./video2image'):
            rmtree('./video2img')
        if os.path.exists('./img2video'):
            rmtree('./img2video')
        if not os.path.exists('./mask_config.json'):
            with open('./mask_config.json', 'w') as file:
                path = os.getcwd()
                path = path.replace('\\', '/')
                json_file = dict(input_path="../../Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/45c0ed021465dec99511cf89c0ce52ab/Message/MessageTemp/2fb61c95cbe0c3499ebd7eb44b7bfa58/File", output_path=path + '/mask_output',
                                 multi_thread=True, into_memory=True, running_instance=[])
                json.dump(json_file, file)
        with open('./mask_config.json', 'r') as file:
            json_file = json.load(file)
            self.output_path.set(json_file['output_path'])
            self.input_path.set(json_file['input_path'])
            try:
                self.multi_thread.set(json_file['multi_thread'])
            except KeyError:
                self.multi_thread.set(True)
            try:
                self.into_memory.set(json_file['into_memory'])
            except KeyError:
                self.into_memory.set(True)


    def set_into_memory_(self):
        if not self.start:
            self.into_memory_ = self.into_memory.get()

    def when_frame_destroy(self, event):
        self.config_running_instance('remove')
        self.free_temp()

    def free_temp(self):
        with open('config.json', 'r') as file:
            data = json.load(file)
            try:
                instances = data['running_instance']
            except KeyError:
                instances = []
            for instance in os.listdir('./temp'):
                if not instance[9:] in instances:
                    rmtree('./temp/' + instance)
                    # print('rmtree ./temp/{}'.format(instance))


    def focus_on_frame(self, event):
        self.frame.focus_set()

    def config_software(self):
        top = tk.Toplevel()
        top.title('修改配置')
        top.geometry('640x640')
        top.wm_attributes('-topmost', 1)
        tk.Button(top, text='更改默认视频输入路径', command=self.change_input_path).place(x=20, y=8, width=140, height=31)
        tk.Entry(top, textvariable=self.input_path, state=tk.DISABLED).place(x=180, y=8, width=420, height=31)
        tk.Button(top, text='更改默认json输出路径', command=self.change_output_path).place(x=20, y=58, width=140, height=31)
        tk.Entry(top, textvariable=self.output_path, state=tk.DISABLED).place(x=180, y=58, width=420, height=31)

        tk.Label(top, text='工作模式：', font=1).place(x=102, y=213, anchor='center')
        tk.Checkbutton(top, text='多线程处理视频', onvalue=True, offvalue=False, variable=self.multi_thread, font=1).place(x=180, y=198)


        tk.Label(top, text='如何缓存图像帧：', font=1).place(x=102, y=297, anchor='center')
        text = ['内存', '磁盘']
        value = [True, False]
        rb3 = [tk.Radiobutton(top, text=text[i], value=value[i], variable=self.into_memory, font=1) for i in range(2)]
        for i in range(2):
            rb3[i].place(x=180 + 75 * i, y=284)


    def set_invisible(self, index_):
        temp = []
        if self.entry_content[2 * index_].get() != '':
            temp.append(int(self.entry_content[2 * index_].get()))
        else:
            return
        if self.entry_content[2 * index_ + 1].get() != '':
            temp.append(int(self.entry_content[2 * index_ + 1].get()))
        else:
            return
        if (not 0 <= temp[0] <= self.image_width) or (not 0 <= temp[1] <= self.image_height):
            return
        k = [temp[0], self.image_width - temp[0], temp[1], self.image_height - temp[1]]  # 左，右，上，下
        i = k.index(min(k))
        if i == 0:
            self.entry_content[2 * index_].set(str(-10))
        elif i == 1:
            self.entry_content[2 * index_].set(str(self.image_width + 10))
        elif i == 2:
            self.entry_content[2 * index_ + 1].set(str(-10))
        elif i == 3:
            self.entry_content[2 * index_ + 1].set(str(self.image_height + 10))


    def on_keyboard_entry(self, event):
        if self.start:
            temp = str(self.parent.focus_get())
            i = temp.split('y')[1]
            if i == '':
                i = 0
            else:
                i = int(i) - 1
            if event.keysym == 'Return':
                self.focus_on_frame('')
            elif i % 2 == 0 and (event.char == 'a' or event.char == 'A'):  # 向左
                self.entry_content[i].set(str(int(self.entry_content[i].get()) - 1))
            elif i % 2 == 1 and (event.char == 'w' or event.char == 'W'):  # 向上
                self.entry_content[i].set(str(int(self.entry_content[i].get()) - 1))
            elif i % 2 == 1 and (event.char == 's' or event.char == 'S'):  # 向下
                self.entry_content[i].set(str(int(self.entry_content[i].get()) + 1))
            elif i % 2 == 0 and (event.char == 'd' or event.char == 'D'):  # 向右
                self.entry_content[i].set(str(int(self.entry_content[i].get()) + 1))

    def on_keyboard(self, event):
        if self.start:
            # print(event, event.keycode, event.keysym, event.char)  # 根据这行代码来确定自己的按键信息
            if event.keysym == 'Return':
                self.next_image()
                return
            elif event.char == '0' or event.char == 'k' or event.char == 'K':
                self.previous_image()
                return
            elif event.char == '6' or event.char == ']':
                self.reset_coordinate()
                return

    # 响应鼠标点击
    def on_click(self, event):
        if self.start:
            has_value = [False, False, False, False]
            for i in range(0, 4, 1):
                if self.entry_content[i * 2].get() != '-1':
                    has_value[i] = True
            index = -1
            for j, value in enumerate(has_value):
                if not value:
                    index = j
                    break
            if index != -1:
                self.entry_content[index * 2].set(event.x)
                self.entry_content[index * 2 + 1].set(event.y)

    def on_click_r(self, event):
        if self.start:
            has_value = [False, False, False, False]
            for i in range(4, 8, 1):
                if self.entry_content[i * 2].get() != '-1':
                    has_value[i - 4] = True
            index = -1
            for j, value in enumerate(has_value):
                if not value:
                    index = j + 4
                    break
            if index != -1:
                self.entry_content[index * 2].set(event.x)
                self.entry_content[index * 2 + 1].set(event.y)

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.previous_image()
        elif event.delta < 0:
            self.next_image()

    def on_clear_bt(self, event, i):
        self.entry_content[i * 2].set(str(-1))
        self.entry_content[i * 2 + 1].set(str(-1))

    def write_config_file(self):
        with open('./config.json', 'r') as file:
            data = json.load(file)
        with open('./config.json',  'w') as file:
            instance = data['running_instance']
            json_file = dict(input_path=self.input_path.get(), output_path=self.output_path.get(),
                             multi_thread=self.multi_thread.get(),
                             into_memory=self.into_memory.get(),
                             running_instance=instance)
            json.dump(json_file, file)

    def change_output_path(self):
        path = tk.filedialog.askdirectory(initialdir=self.output_path.get())
        if path != '':
            self.output_path.set(path)
            self.write_config_file()

    def change_input_path(self):
        path = tk.filedialog.askdirectory(initialdir=self.input_path.get())
        if path != '':
            self.input_path.set(path)
            self.write_config_file()

    def select_path(self):
        path_ = tk.filedialog.askopenfilename(initialdir=self.input_path.get())
        if path_ != "":
            self.reset()
            self.videoPath = path_
            self.set_filename()
            if self.multi_thread.get():
                try:
                    _thread.start_new_thread(self.process_by_mediapipe, ())
                except:
                    tk.messagebox.showerror('错误', '无法启动线程')
            else:
                self.process_by_mediapipe()
        else:
            return

        self.config_running_instance('append')

    def config_running_instance(self, command):
        with open('./config.json', 'r') as file:
            data = json.load(file)
        with open('./config.json', 'w') as file:
            try:
                instance = data['running_instance']
                if command == 'append':
                    instance.append(self.filename)
                elif command == 'remove':
                    try:
                        instance.remove(self.filename)
                    except ValueError:
                        pass
                elif command == 'clear':
                    instance = []
            except KeyError:
                if command == 'append':
                    instance = [self.filename]
                else:
                    instance = []
            data['running_instance'] = instance
            json.dump(data, file)

    def set_filename(self):
        path, name = os.path.split(self.videoPath)
        self.filename, suffix = os.path.splitext(name)
        self.label2.config(text="视频编号：" + self.filename)

    def reset_coordinate(self):
        if self.start:
            for i in range(16):
                self.entry_content[i].set(str(-1))
        else:
            tk.messagebox.showwarning("提示", "先点击选择视频~")
        self.frame.focus_set()

    # 保存每一帧的关键点坐标、过渡or张开or握紧
    def save_coordinate(self):
        if self.start:
            for i in range(16):
                point_index = i // 2
                content = float(self.entry_content[i].get())
                coord_index = (i % 2) + 1  # x or y

                if content == -1.0:
                    self.label_point[self.current][point_index][0] = -1
                    self.label_point[self.current][point_index][coord_index] = -1
                else:
                    self.label_point[self.current][point_index][0] = self.current + 1
                    temp = self.image_width if coord_index == 1 else self.image_height
                    self.label_point[self.current][point_index][coord_index] = content / temp
                    foreground = 1 if i < 8 else 0
                    self.label_point[self.current][point_index][3] = foreground

            self.updata_annot_frame_entry()
            return True

    def updata_annot_frame_entry(self):  # 前景点大于等于2，背景点大于等于3
        foreground = 0
        background = 0
        for i in range(4):
            if self.entry_content[2 * i].get() != '-1':
                foreground += 1
        for i in range(4, 8):
            if self.entry_content[2 * i].get() != '-1':
                background += 1
        if foreground >= 2 and background >= 3:
            temp = []
            for i in range(21):
                if self.annot_frame_index[i].get() != -1:
                    temp.append(self.annot_frame_index[i].get())
            if (self.current + 1) not in temp:
                temp.append(self.current + 1)
                temp.sort()
                for i in range(21):
                    if i < len(temp):
                        self.annot_frame_index[i].set(temp[i])
                    else:
                        self.annot_frame_index[i].set(-1)
        else:
            temp = []
            for i in range(21):
                if self.annot_frame_index[i].get() != -1:
                    temp.append(self.annot_frame_index[i].get())
            if (self.current + 1) in temp:
                temp.remove(self.current + 1)
                temp.sort()
                for i in range(21):
                    if i < len(temp):
                        self.annot_frame_index[i].set(temp[i])
                    else:
                        self.annot_frame_index[i].set(-1)

    def load_image(self):
        if self.into_memory_:  # 写入内存
            pil_image = Image.fromarray(self.img[self.current])  # bgr转rgb的第一种方法：需要调用opencv2接口
            # pil_image = Image.fromarray(self.img[self.current][..., ::-1])  # bgr转rgb的第二种方法，不调用opencv接口
        else:
            imagePath = './temp/video2img' + self.filename + '/' + str(self.current + 1) + '.jpg'
            pil_image = Image.open(imagePath)
        self.tkimg = ImageTk.PhotoImage(pil_image)
        self.panel.create_image(2, 2, image=self.tkimg, anchor="nw")
        self.set_entry_content()
        # self.clear_rb()
        self.frame.focus_set()
        self.label1.config(text="帧序号：" + str(self.current + 1) + "/" + str(self.frame_count))

    # 设置entry的值
    def set_entry_content(self):
        for i in range(8):  # 前四个为前景，后四个为背景
            if self.label_point[self.current][i][0] != -1:
                self.entry_content[i * 2].set(str(int(self.label_point[self.current][i][1] * self.image_width)))
                self.entry_content[i * 2 + 1].set(str(int(self.label_point[self.current][i][2] * self.image_height)))
            else:
                self.entry_content[i * 2].set(str(-1))
                self.entry_content[i * 2 + 1].set(str(-1))


    def callback_multi_thread(self, *args):
        self.write_config_file()

    def callback_into_memory(self, *args):
        self.write_config_file()
        self.set_into_memory_()

    def callback_index(self, *args):
        if self.start:
            for i in range(21):
                self.new_show_coordinate(i)

    def callback_entry(self, var, index, mode):
        if self.start:
            temp_str = "".join(list(filter(str.isdigit, var)))
            i = int(temp_str)
            index_ = i // 2
            # print("var = " + str(var), " i = " + str(i))
            temp_cont = self.entry_content[i - 0].get()  # entry_content前面有0个tk变量
            prefix = ''
            if temp_cont.startswith('-'):
                prefix = '-'
            temp_cont = prefix + "".join(list(filter(str.isdigit, temp_cont)))
            self.entry_content[i].set(temp_cont)
            # print("entry_content[" + str(i - 0) + "] = " + temp_cont)
            if temp_cont.replace("-", "").isdigit() and temp_cont != "":
                # print(temp_cont)
                # self.show_coordinate()
                self.new_show_coordinate(index_)

    def new_show_coordinate(self, index_):
        self.panel.delete('a' + str(index_))  # tag为纯数字识别不了- -
        temp = []
        if self.entry_content[2 * index_].get() != '':
            temp.append(float(self.entry_content[2 * index_].get()))
        else:
            return
        if self.entry_content[2 * index_ + 1].get() != '':
            temp.append(float(self.entry_content[2 * index_ + 1].get()))
        else:
            return
        color = ['green', 'red', 'yellow', 'cyan', 'pink', '']
        offset = [1, -3]
        if index_ < 4:
            foreground = 0
        else:
            foreground = 1
        self.panel.create_oval(temp[0] - self.rad, temp[1] - self.rad, temp[0] + self.rad, temp[1] + self.rad,
                               fill=color[foreground], tags='a' + str(index_))
        self.panel.create_text(temp[0] + self.rad + 3.0, temp[1], text=str(index_ + offset[foreground]),
                               tags='a' + str(index_))


    def reset(self):
        self.panel.delete("all")
        self.start = False
        self.set_into_memory_()
        self.current = 0
        for i in range(16):
            self.entry_list[i].delete(0, tk.END)
        self.label2.config(text="视频编号：")
        self.label1.config(text="帧序号：0/0")
        self.label10.config(text="")
        self.detect = 'all'
        self.config_running_instance('remove')
        self.filename = ''
        # self.cb2.deselect()
        # self.last_gr_label = 0
        self.bt5.config(text='保存输出文件')
        self.img = []
        for i in range(21):
            self.annot_frame_index[i].set(-1)

    def next_image(self):
        if self.start:
            if not self.save_coordinate():
                return
            # print("cur = " + str(self.current))
            # print("count = " + str(self.frame_count))
            if (self.current + 1) < self.frame_count:
                self.current = self.current + 1
                self.load_image()
            else:
                tk.messagebox.showinfo("提示", "该视频已处理完成，请点击’保存输出文件‘按钮")
            # print(self.current + 1, self.process[self.current])
        else:
            tk.messagebox.showwarning("提示", "先点击选择视频~")

    def check(self):
        temp = []
        for i in range(21):
            temp.append(self.annot_frame_index[i].get())
        if -1 in temp:
            tk.messagebox.showwarning("错误", "未标够21帧")
            return False
        for i in range(3):
            for j in range(6):
                if temp[i * 7 + j] + 1 != temp[i * 7 + j + 1]:
                    tk.messagebox.showwarning("错误", "组内不连续")
                    return False
        if temp[7] - temp[6] <= 2 or temp[14] - temp[13] <= 2:
            tk.messagebox.showwarning("错误", "组间间隔需大于2")
            return False

        return True

    def get_json_filename(self):
        return 'mask_' + self.filename

    def write_json(self):
        json_name = self.get_json_filename()
        name = tk.filedialog.asksaveasfilename(title=u"保存文件", initialdir=self.output_path.get(),
                                               initialfile=json_name, filetypes=[("json", ".json")])
        if name == '':
            tk.messagebox.showwarning("提示", "未保存成功，请点击保存输出文件按钮")
            return False

        mlabel = [[] for _ in range(21)]
        for i in range(21):
            frame_index = self.annot_frame_index[i].get()
            mlabel[i].append(frame_index)
            for j in range(8):
                if self.label_point[frame_index - 1][j][0] != -1:
                    x = self.label_point[frame_index - 1][j][1]
                    y = self.label_point[frame_index - 1][j][2]
                    foreground = self.label_point[frame_index - 1][j][3]
                    mlabel[i].append((x, y, foreground))

        json_file = dict(name=self.filename,
                         width=self.original_width, height=self.original_height,
                         label=mlabel)
        with open(name + ".json", "w") as file:
            json.dump(json_file, file)
        print("write json file successfully!")
        return True

    def save_file(self):
        if self.start:
            if not self.save_coordinate():
                return
            if not self.check():
                return

            if not self.write_json():
                return

            self.reset()
        else:
            tk.messagebox.showwarning("提示", "先点击选择视频")

    def previous_image(self):
        if self.current > 0:
            if not self.save_coordinate():
                return
            self.current = self.current - 1
            self.load_image()
            # print(self.current + 1, self.process[self.current])
        else:
            tk.messagebox.showwarning("提示", "前面真的没有图像帧了~")

    def get_frame_rate(self, fps):
        temp = round(fps, 2)
        temp = str(int(100 * temp))
        while len(temp) < 4:
            temp = list(temp)
            temp.append('0')
            temp = ''.join(temp)
            # print(temp)
        if int(temp[3]) > 4:
            temp = int(temp) // 10
            result = (temp + 1) * 10
        else:
            result = temp
        result = float(result)
        # print('before processed: ' + str(self.frame_rate))
        # print('after processed: ' + str(round(result / 100, 1)))
        return round(result / 100, 1)


    def process_by_mediapipe(self):
        cap = cv2.VideoCapture(self.videoPath)
        # print(type(path), path)
        self.frame_count = int(cap.get(7))  # 视频总帧数. opencv似乎会丢掉重复的帧，因此该值不一定准确
        self.frame_rate = cap.get(5)
        self.frame_rate = self.get_frame_rate(self.frame_rate)
        self.label9.config(text="帧率：" + str(self.frame_rate))
        self.label_point = [[[-1, -1, -1, -1] for _ in range(8)] for _ in range(self.frame_count)]
        i = 0

        # 创建video2img文件夹
        if not self.into_memory_:
            if not os.path.exists('./temp/video2img' + self.filename):
                os.mkdir('./temp/video2img' + self.filename)
            else:
                rmtree('./temp/video2img' + self.filename)
                os.mkdir('./temp/video2img' + self.filename)

        # 创建img2video文件夹
        if not os.path.exists('./temp/img2video' + self.filename):
            os.mkdir('./temp/img2video' + self.filename)
        else:
            rmtree('./temp/img2video' + self.filename)
            os.mkdir('./temp/img2video' + self.filename)

        while True:
            # if i != 0:
            #     keyboard.wait('d')
            success, image = cap.read()
            if not success:
                # print("Ignoring empty camera frame.")
                break

            # 尺寸调整为360*680
            dim = (self.image_width, self.image_height)
            if image.shape[0] != self.image_height or image.shape[1] != self.image_width:
                resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
                if not self.into_memory_:
                    cv2.imwrite('./temp/video2img' + self.filename + '/' + str(i + 1) + '.jpg', resized)
                else:
                    self.img.append(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
            else:
                if not self.into_memory_:
                    cv2.imwrite('./temp/video2img' + self.filename + '/' + str(i + 1) + '.jpg', image)
                else:
                    self.img.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            cv2.imwrite('./temp/img2video' + self.filename + '/' + str(i + 1) + '.jpg', image)

            image1 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # image2 = image.copy()


            i = i + 1
            if i == 1:  # 只赋值一次
                self.original_height, self.original_width, c = image.shape  # get image shape

            cv2.namedWindow('Processing', 0)
            cv2.resizeWindow('Processing', 360, 680)
            cv2.imshow('Processing', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        if self.into_memory_:
            if len(self.img) != self.frame_count:  # 读取视频丢帧时
                self.frame_count = len(self.img)
        else:
            if len(os.listdir('./temp/video2img' + self.filename)) != self.frame_count:
                self.frame_count = len(os.listdir('./temp/video2img' + self.filename))

        cv2.destroyAllWindows()
        cap.release()
        self.start = True
        self.load_image()
        # print("mediapipe")


if __name__ == '__main__':
    root = tk.Tk()
    tool = LabelTool(root)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()

