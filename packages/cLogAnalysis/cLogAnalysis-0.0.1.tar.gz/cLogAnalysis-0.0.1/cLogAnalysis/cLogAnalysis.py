# 记录日志
from urllib.parse import quote

from cPython import cPython as cp
from enum import Enum
import base64


class LogAnalysis:
    class Type(Enum):
        DEBUG = -1
        INFO = 0
        WARNING = 1
        ERROR = 2

    def __init__(self, name, category, username, password):
        self.name = name
        self.category = category
        encoded_bytes = base64.b64encode(('%s:%s' % (username, password)).encode('utf-8'))
        encoded_text = encoded_bytes.decode('utf-8')
        self.authorization = 'Basic %s' % encoded_text

    def analysis(self,  type: Type, value):
        return cp.post_for_request('http://ikuai.xiaoc.cn:828/god/info/add?name=%s&value=%s&category=%s&type=%s' % (
            quote(self.name), quote(value), quote(self.category), type.value),
                            headers={'Authorization': self.authorization})


if __name__ == '__main__':
    t = LogAnalysis('测试', '测试', 'test', 'test')
    print(t.analysis(t.Type.WARNING, '测试'))
