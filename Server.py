import socket
import threading
import json
import random


class ServerTest(object):
    """
    自己写个服务器训练下
    功能：
    - 做连接，'127.0.0.0', 55500
    - 收到推进请求，直接反馈ACK，type:4
    - 隔段时间，发送暂停请求消息，并反馈节点数据，type:6
    - 隔段时间，发送系统状态信息，type:9
    """
    SIM_REBOOT = 0
    SIM_STEP = 1

    def __init__(self):
        self.ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ser.bind(('127.0.0.1', 55500))
        self.ser.listen(1)
        print('Waiting for connection...')

        # 推进计数
        self.counter_step = 0

    def run(self):
        while True:
            sock, addr = self.ser.accept()
            t = threading.Thread(target=self.handle, args=(sock, addr))
            t.start()

    def handle(self, sock, addr):
        """
        处理客户端收发控制
        - 收到reboot，print
        - 收到step，反馈type 4
        - step计数self.counter
            - 当self.counter为200的倍数时，发送暂停消息type6，并附带节点消息
            - 当self.counter为500的倍数时，发送系统状态消息type9
        :param sock:
        :param addr:
        :return:
        """
        print('Accept new connection from %s:%s...' % addr)
        bytevar = sock.recv(0x100000)
        mes = self.unpack(bytevar)
        print('Receive data {0}'.format(mes))
        if mes['type'] == self.SIM_REBOOT:
            print('Reboot.')
        elif mes['type'] == self.SIM_STEP:
            print('Step.')
            self.counter_step += 1
            response_mes = {
                'type': 4
            }
            sock.send(self.pack(response_mes))
        if self.counter_step % 200 == 0:
            # [mes_suspend]
            sock.send(self.pack(self.mes_suspendWithNodeStatus()))
        if self.counter_step % 500 == 0:
            # [mes_systemStatus]
            sock.send(self.pack(self.mes_syestemStatus()))

    @staticmethod
    def mes_suspendWithNodeStatus():
        """
        生成仿真暂停消息，附节点状态信息，并返回
        :return:
        """
        num_nodes = 10
        nodes = []
        node_single = dict()
        for i in range(num_nodes):
            node_single['addr'] = i
            node_single['name'] = i
            num_random1 = random.random()
            if 0 < num_random1 <= 0.5:
                node_single['leader'] = node_single['addr']
                node_single['started'] = True
                node_single['joined'] = True
                node_single['type'] = True
            else:
                node_single['leader'] = node_single['addr'] - 1  # 即不等
                node_single['started'] = False
                node_single['joined'] = False
                node_single['type'] = False
            num_random2 = random.random()
            if 0 < num_random2 <= 0.5:
                node_single['malicious'] = True
            else:
                node_single['malicious'] = False
            node_single['x'] = random.randint(1, 20)
            node_single['y'] = random.randint(1, 20)
            node_single['z'] = random.randint(1, 20)

            nodes.append(node_single)
        mes = {
            'type': 6,
            'num_nodes': num_nodes,
            'nodes': nodes
        }
        return mes

    @staticmethod
    def mes_syestemStatus():
        """
        生成系统状态信息，并返回
        - 随机数判断，0-0.5生成共识时间，0.5-1生成防篡改率
        :return:
        """
        mes = {
            'type': 9,
            'stat': None,
            'value': None
        }
        num_random1 = random.random()
        if 0 < num_random1 <= 0.5:
            mes['stat'] = 0
        else:
            mes['stat'] = 1
        num_random2 = random.random()
        mes['value'] = num_random2
        return mes

    @staticmethod
    def unpack(bytevar):
        jvar = bytevar[4:].decode('utf-8')
        pyvar = json.loads(jvar)
        print('Receive data from client: {0}'.format(pyvar))
        return pyvar

    @staticmethod
    def pack(pyvar):
        jvar_byte = json.dumps(pyvar, ensure_ascii=False, encoding='utf-8')
        dlen = len(jvar_byte)
        packlen = int.to_bytes(dlen, 4, 'little')
        return packlen + jvar_byte


if __name__ == '__main__':
    s = ServerTest()
    s.run()
