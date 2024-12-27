import socket
import json
import time
from PyQt6.QtWidgets import QApplication, QToolBar, QFileDialog, QMessageBox, QTableWidgetItem, QTextBrowser
from PyQt6 import uic
import sys

# 1、损坏帧和丢失帧不回复ACK
# 2、窗口内标记接受到的帧
# 3、向上层传递有效帧
# 4、发送ACK

# 帧结构：使用字典 {"frame_number": x, "data": "..."}

def receiver(server_ip, server_port, text_browser):
    # TCP建立连接
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.bind((server_ip, server_port))
    receiver_socket.listen(1)
    text_browser.append("接收方已启动，等待连接...")
    print("接收方已启动，等待连接...")

    conn, addr = receiver_socket.accept()
    text_browser.append(f"已连接到发送方: {addr}")
    print(f"已连接到发送方: {addr}")

    expected_frame = 0  # 期望的帧编号
    buffer = ""  # 用于存储未处理的数据

    while True:
        try:
            # 从连接中接收数据
            data = conn.recv(1024).decode()
            if not data:  # 连接断开
                break

            buffer += data  # 将新接收的数据追加到缓冲区

            # 持续解析缓冲区中的完整帧
            while "\n" in buffer:  # 假设帧以 '\n' 分隔
                frame_data, buffer = buffer.split("\n", 1)  # 分离出一帧数据
                frame = json.loads(frame_data)
                print(frame)
                frame_info = f"\n接收 <--- 帧{frame['frame_number']}: {frame['data']}"
                text_browser.append(frame_info)
                print(frame_info)

                # 1、损失帧 丢失帧不是期待的帧直接丢弃
                if frame['frame_number'] == expected_frame:
                    # 通过QMessageBox提示用户选择如何处理帧
                    msg = QMessageBox()
                    msg.setWindowTitle("接收者：处理帧操作")
                    msg.setText(f"处理帧{frame['frame_number']} (j-接收, d-丢失, s-损坏)?")
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

                    # 修改按钮文本为中文
                    yes_button = msg.button(QMessageBox.StandardButton.Yes)
                    yes_button.setText("确认接收")

                    no_button = msg.button(QMessageBox.StandardButton.No)
                    no_button.setText("确认丢失")

                    cancel_button = msg.button(QMessageBox.StandardButton.Cancel)
                    cancel_button.setText("确认损坏")

                    # 设置弹窗位置跟随UI
                    msg.move(ui.pos())  # 将弹窗移动到UI界面的位置

                    response = msg.exec()

                    if response == QMessageBox.StandardButton.No:
                        log_msg = f"  [丢失] 忽略帧{frame['frame_number']}"
                        text_browser.append(log_msg)
                        print(log_msg)
                        continue
                    elif response == QMessageBox.StandardButton.Cancel:
                        log_msg = f"  [损坏] 忽略帧{frame['frame_number']}"
                        text_browser.append(log_msg)
                        print(log_msg)

                        # 休眠处理损坏帧
                        sleep_time = 2  # 设置休眠时间（2秒）
                        log_msg = f"  [休眠] 帧{frame['frame_number']} 被标记为损坏，休眠 {sleep_time} 秒等待重新发送"
                        text_browser.append(log_msg)
                        print(log_msg)
                        time.sleep(sleep_time)
                        continue

                    # 2、接收者窗口标记接收帧成功 并窗口移动到下一位（窗口只有一个）
                    log_msg = f"  [接受] 帧{frame['frame_number']} 正确接收"
                    text_browser.append(log_msg)
                    print(log_msg)
                    expected_frame += 1
                    #  3、前端展示加一个向上层发送的例子 比如往右边一摆
                    log_msg = f"  [上层发送] 帧{frame['frame_number']} 已经发送到上层"
                    text_browser.append(log_msg)
                    print(log_msg)

                    # 4、自动发送ACK
                    ack = {"ack_number": expected_frame, "ack_data": "yes"}
                    conn.sendall(json.dumps(ack).encode())
                    log_msg = f"发送 ---> ACK{ack['ack_number']}"
                    text_browser.append(log_msg)
                    print(log_msg)
                else:
                    # 不是期望的帧就重新发送ack
                    log_msg = f"  [错误] 未预期的帧，期望帧{expected_frame}"
                    text_browser.append(log_msg)
                    print(log_msg)

                    # 4、自动发送ACK
                    ack = {"ack_number": expected_frame, "ack_data":"yes"}
                    conn.sendall(json.dumps(ack).encode())
                    log_msg = f"发送 ---> ACK{ack['ack_number']}"
                    text_browser.append(log_msg)
                    print(log_msg)

                time.sleep(5)  # 模拟延迟

        except json.JSONDecodeError:
            continue

    print("接收方结束通信！")
    text_browser.append("接收方结束通信！")
    conn.close()
    receiver_socket.close()


def begin(ui):
    server_ip = "127.0.0.1"
    server_port = 999
    # 将QTextBrowser传递给receiver函数，用于显示接收到的帧信息
    text_browser = ui.textBrowser
    receiver(server_ip, server_port, text_browser)


if __name__ == "__main__":
    app = QApplication(sys.argv)  # 创建应用实例
    ui = uic.loadUi("./receiverUI.ui")  # 加载UI文件
    ui.show()  # 显示UI界面

    # 连接按钮的事件
    ui.pushButton.clicked.connect(lambda: begin(ui))

    sys.exit(app.exec())  # 运行事件循环，阻塞直到退出