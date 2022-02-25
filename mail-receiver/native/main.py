# crx_python.py
"""
chrome extension messaging with local application.
"""

from datetime import datetime
import time
import sys
import logging
from tkinter.tix import Tree
from receiver import MailReceiver,PingCheck,MessageReceiver
from stream import Message

settings={
    "count" : "359066432@qq.com",
    # password = "你的邮箱授权码"
    "mail_server" : "pop.qq.com",

}

receiver = MailReceiver(daemon=True)
receiver.update_settings(**settings)
ping_checker = PingCheck(interval=2,daemon=True)
msg_receiver  = MessageReceiver()

def query_app_state():
    msg = Message(
        type="query",
        data= {
            "config":MailReceiver._config,
            "context":MailReceiver.context
        }
    )
    msg.send()


# 主函数入口
def main():
    # 对windows平台的行结束符处理：\r\n--->\n
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    logging.basicConfig(filename="ctl.log",
                        level=logging.INFO,
                        format="%(levelname)s::%(asctime)s-%(module)s-%(lineno)d: %(message)s",
                        datefmt="%Y-%d-%m %H:%M:%S")

    # 启动读取输入流线程
    msg_receiver.start()
    while True:
        msg = msg_receiver.msg_queue.get()
        if msg:
            handle_message(message=msg)

# Chrome extension to local application：与chrome-extension进行通信的class
def handle_message(message:Message):
    if message.type =="log":
        logging.info(f">>> log:{message.to_json()}")
    elif message.type =="start":
        logging.info(">>> start mail thread")
        receiver.start()
        # test.start()
    elif message.type =="setting":
        logging.info(f">>> update mail receiver {message.data}")
        receiver._config.update(message.data)
    elif message.type =="stop":
        logging.info("stop mail thread")
        # receiver.join()
        # ping_checker.join()
        # msg_receiver.join()
        sys.exit(0)
    elif message.type =="query":
        ### query native app state
        return query_app_state()
    elif message.type =="ping":
        PingCheck.last_ping_time = datetime.now()
        if not ping_checker.is_alive():
            logging.info(">>> start ping thread")
            ping_checker.start()

if __name__ == "__main__":
    main()