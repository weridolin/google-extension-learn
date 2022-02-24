from asyncio.log import logger
from email import message
import logging
from threading import Timer
import threading
from email.utils import parseaddr
from email.header import decode_header
import poplib
from email.parser import Parser
from queue import Queue
import json
from stream import Message

class MailReceiver(Timer):
    cache = Queue()

    _config = {
        "count":None,
        "password":None,
        "mail_server":None,
    }
    new_index = 0 # 最新一封邮件的索引，从改索引后的邮件都为新邮件
    
    def __init__(self, interval: float,daemon ,args=None, kwargs=None) -> None:
        super().__init__(interval, self._receive, args, kwargs)
        self.daemon = daemon # set backend thread
        self.stop_flag = threading.Event()
        self.name="receiver timer"
        self.__client = None

    def update_settings(self,**kwargs):
        MailReceiver._config.update(**kwargs)

    def _connect(self):
        assert MailReceiver._config["count"]!= None,"mail count cannot be None"
        assert MailReceiver._config["password"]!=None,"mail authentication code cannot be None"
        assert MailReceiver._config["mail_server"]!=None,"mail server cannot be None"
        self.__client = poplib.POP3(MailReceiver._config["mail_server"])
        # user account authentication
        self.__client.user(MailReceiver._config["count"])
        self.__client.pass_(MailReceiver._config["password"])

    def _receive(self):
        # 接收最新收到的邮件
        # new_index
        _,mails,_ = self.__client.list()
        print(len(mails),MailReceiver.new_index)
        _mail_list = []
        if  len(mails) > MailReceiver.new_index:
            # 获取 MailReceiver.new_index 后的每一封邮件,同时更新 MailReceiver.new_index
            while MailReceiver.new_index < len(mails):
                MailReceiver.new_index +=1
                _, lines, _ = self.__client.retr(MailReceiver.new_index)
                _mail_list.append(lines)
        elif len(mails) == MailReceiver.new_index:
            _, lines, _ = self.__client.retr(MailReceiver.new_index)
            _mail_list.append(lines)     
        res = self._parse(_mail_list)
        msg:Message =Message(type="log",data=f"init mail count:{MailReceiver.new_index}")
        msg.send()
        # message = Message(type="log",data=res)
        # message.send()
        
    def _parse(self,messages):
        _result = []
        for lines in messages:
            _msg = b'\r\n'.join(lines).decode('utf-8')
            _msg = Parser().parsestr(_msg)
            _from,to,subject = self._parse_header(_msg)
            _result.append({
                "header":{
                    "from":_from,
                    "to":to,
                    "subject":subject
                },
                "body":"self._parse_body(msg=_msg)"
            })
        return _result

    def _parse_header(self,msg):
        _from = msg.get("From")
        _to = msg.get("To")
        _subject = msg.get("Subject")
        if _from:
            _from_name,_from_count = parseaddr(_from)
            _from =f"{decode_str(_from_name)},<{_from_count}>"
        if _to:
            _to_name,_to_count = parseaddr(_to)
            _to = f"{decode_str(_to_name)},<{_to_count}>"
        if _subject:
            _subject = decode_str(_subject)
        return _from,_to,_subject

    def _parse_body(self,msg):
        result = ""
        if (msg.is_multipart()):
            # todo text
            parts = msg.get_payload()
            for _, part in enumerate(parts):
                result+= self._parse_body(part)
        else:
            # 获取邮件文本内容类型
            content_type = msg.get_content_type() 
            if content_type=='text/plain' or content_type=='text/html':
                # 获取文本内容
                content = msg.get_payload(decode=True)
                # 获取编码方式
                charset = check_charset(msg)
                if charset:
                    content = content.decode(charset)
                    result = content
            else:
                print("附件??????")
        return result

    def _get_mails_count(self):
        _, mails, _ = self.__client.list()
        return len(mails)

    def run(self) -> None: 
        # 获取邮箱列表当前的邮件数目
        self._connect()
        MailReceiver.new_index = self._get_mails_count()
        msg:Message =Message(type="log",data=f"init mail count:{MailReceiver.new_index}")
        msg.send()
        self.function = self._receive
        self.stop_flag.clear()
        while not self.stop_flag.is_set():
            try:
                super().run()
                self.finished.clear()
            except KeyboardInterrupt:
                break
            except Exception as exc:
                logging.error(f"a error happen:{exc}",exc_info=True)
    
    def stop(self):
        self.stop_flag.set()
        self.__client.quit()

def check_charset(msg):
    # get charset from message object.
    charset = msg.get_charset()
    # if can not get charset
    if charset is None:
    #    get message header content-type value and retrieve the charset from the value.
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

if __name__ == "__main__":
    settings={
        "count" : "359066432@qq.com",
        # password = "你的邮箱授权码"
        "mail_server" : "pop.qq.com",
    }

    t = MailReceiver(2,False)
    t.update_settings(**settings)
    t.start()
