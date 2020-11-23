from client_config import *
import socket
import threading
import json

'''
客户端socket
- 多线程收发tx，rx
- 目前考虑在GUI中，做线程
'''


class ClientSocket(object):
    """
    客户端socket
    - 实例化之后，socket为 实例.csock
    """

    def __init__(self):
        self.csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.txbuf_q = list()  # FIFO 先入先出
        self.txbuf_q_sem = threading.Semaphore(value=0)

        self.recv_cb = None
        self.recv_data = None

    def tx(self):
        """
        发送函数
        - 先acquire获取信号
            - 若计数器为0,则阻塞，等待其它线程release
            - 若计数器大于0,则使计数器减1，返回

        """
        while True:
            self.txbuf_q_sem.acquire(blocking=True)
            # txbuf_q先入先出，pop(0)为remove and return其第一个元素
            buf = self.txbuf_q.pop(0)
            self.csock.sendall(buf)

    def rx(self):
        """
        接收函数
        - 持续接收数据，不断接续
            - 根据已接收的长度，判断是否收全。报文长度为前4个字节
            - 处理完单条报文，利用回调函数setRecvCallback()，将处理完的数据
        :return:
        """
        rxbuf = bytes()
        while True:
            buf = self.csock.recv(0x100000)  # 1MB
            rxbuf = rxbuf + buf
            # [dlen] [data]
            while len(rxbuf) > 4:
                dlen = int.from_bytes(rxbuf[0:4], 'little')
                # 若收全了单条数据
                if len(rxbuf) >= 4 + dlen:
                    # 取出数据段
                    buf = rxbuf[4:4 + dlen]
                    print('buf:', buf)
                    # buf => pyvar
                    pyvar = json.loads(buf.decode('utf-8'))
                    self.recv_cb(pyvar)
                    # 当rxbuf接收完一条后，长度小于4个字节，退出循环，执行上一层循环，继续接收下一条报文
                    rxbuf = rxbuf[4 + dlen:]
                # 若未收全单条数据，退出本层循环，返回大循环继续接收
                else:
                    break

    def setRecvCallback(self, cb):
        """设置回调函数"""
        self.recv_cb = cb  # GUI类的self.recv
        # self.recv_data = data  # GUI类的self

    def send(self, py_buf):
        """
        发送函数
        - 先给python数据转成json，utf-8，转len（）成4字节，加报头
        - 将报文数据放入发送缓存txbuf_q
        - semaphore release，解除tx线程阻塞，socket.send()
        """
        sbuf = self.package_utf8(py_buf)
        self.txbuf_q.append(sbuf)
        self.txbuf_q_sem.release()

    @staticmethod
    def package_utf8(py_mes):
        """发送前，将python消息封装，加报头，返回二进制报文"""
        j_mes = json.dumps(py_mes)
        j_mes_byte = j_mes.encode('utf-8')
        d_len = len(j_mes_byte)
        package_len = int.to_bytes(d_len, 4, 'little')
        return package_len + j_mes_byte
