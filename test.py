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
    print("接收方已启动，等待连接...")

    conn, addr = receiver_socket.accept()
    print(f"已连接到发送方: {addr}")

    expected_frame = 0  # 期望的帧编号

    while True:
        try:
            # 接收到的帧
            frame_data = conn.recv(1024).decode()
            if not frame_data:
                break

            frame = json.loads(frame_data)
            frame_info = f"\n接收 <--- 帧{frame['frame_number']}: {frame['data']}"
            print(frame_info)

            # 更新文本浏览器显示接收到的帧信息
            text_browser.append(frame_info)

            # 1、损失帧 丢失帧不是期待的帧直接丢弃
            if frame['frame_number'] == expected_frame:
                # 通过QMessageBox提示用户选择如何处理帧
                msg = QMessageBox()
                msg.setWindowTitle("选择操作")
                msg.setText(f"处理帧{frame['frame_number']} (j-接收, d-丢失, s-损坏)?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                response = msg.exec()

                if response == QMessageBox.StandardButton.No:
                    print(f"  [丢失] 忽略帧{frame['frame_number']}")
                    continue
                elif response == QMessageBox.StandardButton.Cancel:
                    print(f"  [损坏] 忽略帧{frame['frame_number']}")
                    continue

                # 2、接收者窗口标记接收帧成功 并窗口移动到下一位（窗口只有一个）
                print(f"  [接受] 帧{frame['frame_number']} 正确接收")
                expected_frame += 1
                #  3、前端展示加一个向上层发送的例子 比如往右边一摆
                print(f"  [上层发送] 帧{frame['frame_number']} 已经发送到上层")
            else:
                print(f"  [错误] 未预期的帧，期望帧{expected_frame}")
                ack = {"ack_number": expected_frame}

            # 4、人为控制是否发送ACK
            ack = {"ack_number": expected_frame, "ack_data":"yes"}

            # 通过QMessageBox提示是否发送ACK
            msg = QMessageBox()
            msg.setWindowTitle("发送ACK")
            msg.setText(f"发送ACK{ack['ack_number']}?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            send_ack_response = msg.exec()

            if send_ack_response == QMessageBox.StandardButton.Yes:
                conn.sendall(json.dumps(ack).encode())
                print(f"发送 ---> ACK{ack['ack_number']}")
            else:
                print(f"  [丢失] 未发送ACK{ack['ack_number']}")

            time.sleep(1)  # 模拟延迟

        except json.JSONDecodeError:
            continue

    print("接收方结束通信！")
    conn.close()
    receiver_socket.close()


def begin(ui):
    server_ip = "127.0.0.1"
    server_port = 9999
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
