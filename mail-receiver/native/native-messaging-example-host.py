# crx_python.py
"""
chrome extension messaging with local application.
"""

import time
import sys
import logging
from receiver import MailReceiver
from stream import Message

settings={
    "count" : "359066432@qq.com",
    # password = "你的邮箱授权码"
    "password" : "omhaidmyktahbgje",
    "mail_server" : "pop.qq.com",
}

receiver = MailReceiver(daemon=False)
receiver.update_settings(**settings)

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
    # 1.对windows平台的行结束符处理：\r\n--->\n
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    # 2.日志文件处理对象
    logging.basicConfig(filename="ctl.log",
                        level=logging.INFO,
                        format="%(levelname)s::%(asctime)s-%(module)s-%(lineno)d: %(message)s",
                        datefmt="%Y-%d-%m %H:%M:%S")

    # 3.与chrome extension进行通信
    deal_count = 1
    while True:
        try:
            message:Message = Message.from_stdin()
            if message:
                handle_message(message)
        except Exception as e:
            import traceback
            logging.error(f"{e},trace:{traceback.format_exc()}")

# Chrome extension to local application：与chrome-extension进行通信的class
def handle_message(message:Message):
    if message.type =="log":
        logging.info(">>> log")
    elif message.type =="start":
        logging.info(">>> start mail thread")
        receiver.start()
        # test.start()
    elif message.type =="setting":
        logging.info(f">>> update mail receiver {message.data}")
        receiver._config.update(message.data)
    elif message.type =="stop":
        logging.info("stop mail thread")
        receiver.stop()
    elif message.type =="query":
        ### query native app state
        return query_app_state()

if __name__ == "__main__":
    main()