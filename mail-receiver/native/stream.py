
import json
import struct
from typing import Any
from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
import sys
import logging

@dataclass
class Message(DataClassJsonMixin):
    type:str = "log"
    data:Any = None

    @classmethod
    def pack_header(cls,message)->bytes:
        if isinstance(message,str):
            message = message.encode("utf-8")
        else:
            message = message
        return struct.pack("I",len(message))

    @classmethod
    def unpack_header(cls,header)->int:
        assert isinstance(header,bytes),f"invalid header type:{type(header)}.can only be bytes-like object"
        return struct.unpack("I",header)[0]


    def send(self,message=None):
        if  message is None:
            message = self.to_json()
        logging.info(f"send message:{message} to stdout,type:{type(message)}")
        if isinstance(message,str):
            message = message.encode("utf-8")
        else:
            message = message
        _header = Message.pack_header(message=message)
        # send header
        sys.stdout.buffer.write(_header)
        sys.stdout.buffer.write(message)
        sys.stdout.flush()   

    @classmethod
    def from_stdin(cls):
        # read header
        msg_header = sys.stdin.buffer.read(4)
        if len(msg_header) == 0:
            return None
        # Unpack message length as 4 byte integer, tuple = struct.unpack(fmt, buffer).
        msg_length = struct.unpack("I", msg_header)[0]
        # read msg-body (bytes)
        msg = sys.stdin.buffer.read(msg_length)   
        assert isinstance(msg,bytes),"stdin message must be bytes"
        _msg = msg.decode("utf-8")
        if "ping" not in _msg:
            logging.info(f"获取到消息:{_msg}")
        try:
            return cls.from_json(_msg)
        except Exception:
            logging.error("not a json format message")
            return None

        