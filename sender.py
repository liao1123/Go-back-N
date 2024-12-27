import socket
import json
import time
from PyQt6.QtWidgets import QApplication, QToolBar, QFileDialog, QMessageBox, QTableWidgetItem, QTextBrowser
from PyQt6 import uic
import sys

# 1、成帧
# 2、发送帧启动定时并缓存
# 3、接收损坏帧休眠
# 4、累计确认
# 5、响应ACK：删除帧、停止计时、移动窗口
# 6、超时重发

# UI更新函数
def add_row(data, flag1, flag2):
    global ui
    row_position = ui.table1.rowCount()  # 获取当前行数
    ui.table1.insertRow(row_position)  # 插入新行

    # 添加数据到新行
    ui.table1.setItem(row_position, 0, QTableWidgetItem(data))
    ui.table1.setItem(row_position, 1, QTableWidgetItem(flag1))
    ui.table1.setItem(row_position, 2, QTableWidgetItem(flag2))


# 更新ACK状态为确认
def update_ack_status(ack_number, status):
    global ui
    row_count = ui.table1.rowCount()

    # 查找ACK对应的行并更新状态
    for row in range(row_count):
        if ui.table1.item(row, 0).text() == f"ACK{ack_number}":
            ui.table1.setItem(row, 2, QTableWidgetItem(status))
            break


# 添加选项到comboBox
def add_ack_to_comboBox(ack_number, round_trip_time, ack_data):
    global ui
    ack_item = f"ACK{ack_number}确认"
    ui.comboBox.addItem(ack_item)  # 向comboBox添加选项

    # 获取名为textBrowser的QTextBrowser框
    text_browser = ui.textBrowser
    text_browser.append(f"ACK{ack_number}确认:")
    text_browser.append(f"ACK信息：{json.dumps(ack_data, indent=4)}")  # 将ACK内容打印到textBrowser
    text_browser.append(f"往返时间: {round_trip_time:.4f} 秒")
    text_browser.append("------------------------------------------------------")


# 发送函数
def sender(server_ip, server_port, send_frames, window_size):
    # TCP建立连接
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender_socket.settimeout(10)  # 设置套接字的超时时间
    sender_socket.connect((server_ip, server_port))
    print("已连接到接收方...")
    time.sleep(3)  # 模拟延迟

    # 成帧处理
    frames = [{"frame_number": i, "data": f"{send_frames[i]}"} for i in range(len(send_frames))]
    print(f"成帧结果：{frames}")
    frame_length = len(frames)

    ack_to_receive = 0  # 等待ACK的位置
    frame_to_send = 0  # 当前发送帧的位置

    timer_start_time = None
    timer_running = False
    sent_frames = {}  # 缓存已发送的帧（用于重传）

    while ack_to_receive < frame_length:
        # 发送窗口内全部的帧
        while frame_to_send < ack_to_receive + window_size and frame_to_send < frame_length:
            frame = frames[frame_to_send]
            add_row(f"帧{frame['frame_number']}:{frame['data']}", "发送", "未确认")

            # 更新文本框，显示当前的ack_to_receive和frame_to_send的值
            ui.lineEdit.setText(f"{ack_to_receive}")
            ui.lineEdit_2.setText(f"{frame_to_send}")

            # 发送帧 缓存 启动定时
            print(f"第一次发送 ---> 帧{frame['frame_number']}: {frame['data']}")
            sender_socket.sendall((json.dumps(frame) + "\n").encode())
            frame_to_send += 1

            sent_frames[frame["frame_number"]] = frame  # 缓存发送的帧

        # 启动计时器
        if not timer_running:
            timer_start_time = time.time()
            timer_running = True
            print(f"启动定时器 ---> 帧{ack_to_receive}")

        # 接收ACK
        try:
            ack_data = sender_socket.recv(1024).decode()
            ack = json.loads(ack_data)

            # 处理ACK
            reply = QMessageBox.question(ui, '处理ACK', f"发送者：收到ACK{ack['ack_number']}，是否认为该ACK损坏？",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                print(f"发送者接收到的ACK{ack['ack_number']}  [损坏] 休眠")
                # 更新ACK状态为损坏
                update_ack_status(ack['ack_number'], "损坏")
                continue  # 跳过此ACK的处理

            print(f"接收 <--- ACK{ack['ack_number']}")
            add_row(f"ACK{ack['ack_number']}", "接收", "未确认")  # 添加ACK接收信息到UI

            # 更新ACK状态为确认
            update_ack_status(ack['ack_number'], "确认")
            # 向comboBox添加ACK确认项
            round_trip_time = time.time() - timer_start_time
            add_ack_to_comboBox(ack['ack_number'], round_trip_time, ack)  # 添加到comboBox并打印到textBrowser

            # 更新文本框，显示当前的ack_to_receive和frame_to_send的值
            ui.lineEdit.setText(f"{ack_to_receive}")
            ui.lineEdit_2.setText(f"{frame_to_send}")

            # 累计确认
            if ack['ack_number'] > ack_to_receive:
                print(f"累计确认 ---> 帧{ack_to_receive}到帧{ack['ack_number'] - 1}")
                # 停止已累积确认帧的定时器，并从缓存中删除
                for i in range(ack_to_receive, ack['ack_number']):
                    if i in sent_frames:
                        del sent_frames[i]
                ack_to_receive = ack['ack_number']  # 移动窗口
                timer_running = False  # 停止定时器
            else:
                print("收到重复ACK，忽略...")

        except socket.timeout:
            print(" ")
        # 超时重发
        if timer_running and time.time() - timer_start_time > 10:
            print(f"超时！重发 ---> 帧{ack_to_receive}--帧{frame_to_send - 1}")
            for unacked_frame in sent_frames.values():
                sender_socket.sendall((json.dumps(unacked_frame) + "\n").encode())
                print(f"重新发送 ---> 帧{unacked_frame['frame_number']}: {unacked_frame['data']}")
                add_row(f"重发 ---> 帧{unacked_frame['frame_number']}: {unacked_frame['data']}", "发送",
                        "未确认")
            timer_start_time = time.time()
    print("所有帧已发送成功！")
    sender_socket.close()


# 连接按钮回调函数
def right():
    global ui
    server_ip = "127.0.0.1"
    server_port = 999

    # 获取数据帧和窗口大小
    frames = ui.plainTextEdit.toPlainText().splitlines()  # 获取并转换为帧列表
    window_size = int(ui.plainTextEdit_2.toPlainText())  # 获取窗口大小

    sender(server_ip, server_port, frames, window_size)


if __name__ == "__main__":
    app = QApplication(sys.argv)  # 创建应用实例
    ui = uic.loadUi("./senderUI.ui")  # 加载UI文件
    ui.show()  # 显示UI界面

    # 连接按钮的事件
    ui.pushButton_2.clicked.connect(right)

    sys.exit(app.exec())  # 运行事件循环，阻塞直到退出
