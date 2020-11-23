# from client_config import *
import socket
import json
import threading

'''

'''

class ClientSocket(object):
    def __init__(self):
        """初始化套接字"""
        self.csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.txbuf_q = [] # FIFO 先入先出
        self.txbuf_q_sem = threading.Semaphore()

        self.recv_cb   = None
        self.recv_data = None

    def tx(self):
        """发送"""
        while True:
            # 当无数据可发时，acquire阻塞，等待其它线程release
            self.txbuf_q_sem.acquire()
            # txbuf_q先入先出，pop(0)为remove and return其第一个元素
            buf = self.txbuf_q.pop(0)
            self.csock.sendall(buf)

    def rx(self):
        rxbuf = bytes()
        while True:
            buf = self.csock.recv(0x100000) # 1MB
            rxbuf = rxbuf + buf
            # [dlen] [data]
            while len(rxbuf) > 4:
                dlen = int.from_bytes(rxbuf[0:4], 'little')
                # 若收全了单条数据
                if len(rxbuf) >= 4+dlen:
                    # 取出仍为字节的数据段
                    buf = rxbuf[4:4+dlen]
                    # buf => pyvar
                    pyvar = json.loads(buf.decode('utf-8'))
                    # 由回调函数知，此处recv_cb()为Gui类中的self.recv(self, pyvar)
                    # 将pyvar放入GUI的rxbyf_q
                    self.recv_cb(self.recv_data, pyvar)
                    # 当rxbuf接收完一条后，长度小于4个字节，退出循环，执行上一层循环，继续接收下一条报文
                    rxbuf = rxbuf[4+dlen:]
                # 若未收全单条数据，退出本层循环，返回大循环继续接收
                else:
                    break


    def setRecvCallback(self, cb, data):
        """设置回调函数"""
        self.recv_cb   = cb  # GUI类的self.recv()
        self.recv_data = data  # GUI类的self

    def package_utf8(self, py_mes):
        """发送前，封装报文，加报头，返回二进制报文"""
        j_mes_byte = json.dumps(py_mes, ensure_ascii=False, encoding='utf-8')
        data_len = len(j_mes_byte)  # 获取data的字节数应该用len，getsizeof()获取的是变量占用的大小
        pack_len = int.to_bytes(data_len, 4, 'little')  # 报头4字节长
        return pack_len + j_mes_byte

    def send(self, py_buf):
        # 入队
        s_buf = self.package_utf8(py_buf)
        self.txbuf_q.append(s_buf)
        # release，让跑tx的线程的acquire解除阻塞，发送
        self.txbuf_q_sem.release()



class Gui(object):
    INIT     = 0 # 发送数据包
    SIM_STEP = 1 # 已发送sim-step.req，正在推进仿真，等待sim-step.con

    SIM_STEP_CON = 4

    def __init__(self):
        self.conn = ClientSocket()
        self.conn.setRecvCallback(self.recv, self)
        self.thread_tx = threading.Thread (target=self.conn.tx)
        self.thread_rx = threading.Thread (target=self.conn.rx)

        self.rxbuf_q = [] # 存放接收到的数据
        # FSM (finite state machine)
        self.state = INIT

    def recv(self, pyvar):
        # pyvar打算为处理好的python dict
        self.rxbuf_q.append(pyvar)

    def run(self):

        self.thread_tx.start()
        self.thread_rx.start()
        # TODO: 单独设个线程一直检测是否收到
        while True:
            # 时刻监测是否有数据收到，TODO: 这可以用做收到数据，做解析
            if len(self.rxbuf_q): # 接收到数据
                pyvar = rxbuf_q.pop(0)
                type = pyvar['type']
                if type == SIM_STEP_CON:
                    # TODO: 将标志位设为可继续推进，让推进线程继续发送

                if type == balabala:
                # TODO: 各种解析情况
        # self.thread_tx.join()
        # self.thread_rx.join()

    def on_start_clicked(self):
        # json_buf = None
        # TODO: 发送运行系统命令
        self.conn.csock.send(json_buf)

    def on_step_clicked(self): # 点击仿真推进
        self.conn.csock.send(jbuf)
        self.state = SIM_STEP

    def on_sim_step_con(self):
        if self.state == SIM_STEP:
            # ...





if __name__ == '__main__':
    cs = ClientSocket()
    cs.connect_server(('127.0.0.1', 55500))
    cs.recv_data()
