# # ***********************************************************************
# # https://www.thinbug.com/q/27571494
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import pyqtgraph as pg

class NestedDict(dict):
    def __getitem__(self, item):
        if item not in self:
            self[item] = NestedDict()
        return super().__getitem__(item)

mainList = [['BM', 'Butterfly', 'E-shop', '1400'],
            ['BM', 'Butterfly', 'Fler', '2450'],
            ['BM', 'Butterfly', 'Holesovice', '2450'],
            ['Climbing presents', 'Ear-rings', 'Holesovice', '136'],
            ['Climbing presents', 'Other jewellery', 'E-shop', '160'],
            ['Climbing presents', 'Other jewellery', 'Other', '112'],
            ['PP', 'Skirts', 'Fler', '1380'],
            ['PP', 'Skirts', 'Holesovice', '1320'],
            ['PP', 'Skirts', 'Sashe', '450'],
            ['PP', 'Bags', 'E-shop', '2500'],
            ['PP', 'Skirts', 'E-shop', '5600'],
            ['PP', 'Dresses', 'Other', '6551'],
            ['Mar', 'Dresses', 'Holesovice', '1000'],
            ['Mar', 'Skirts', 'Holesovice', '3000'],
            ['Mar', 'Ear-rings', 'Holesovice', '2000']]

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 50
w.showMaximized()
w.setWindowTitle('pyqtgraph example: GLViewWidget')

# 这起到了加坐标轴的作用
ax = gl.GLAxisItem()
ax.setSize(10,10,10)
w.addItem(ax)

labels = dict(zip(list(set([x[0] for x in mainList])), [2*i for i,j in enumerate(list(set([x[0] for x in mainList])))]))
shops = dict(zip(list(set([x[2] for x in mainList])), [2*i for i,j in enumerate(list(set([x[2] for x in mainList])))]))
items = dict(zip(list(set([x[1] for x in mainList])), [2*i for i,j in enumerate(list(set([x[1] for x in mainList])))]))

d = NestedDict()

for tag, item, source, qty in mainList:
    d[tag][source][item] = qty

# 添加legend，但是好像并没有起作用
legend = pg.LegendItem()

colors = {}
for i in items.keys():
    colors[i] = (round(5*np.random.rand()*np.random.rand(),2),
                 round(5*np.random.rand()*np.random.rand(),2),
                 round(5*np.random.rand()*np.random.rand(),2),
                 round(5*np.random.rand()*np.random.rand(),2))

for key, value in d.items():
    for nkey, nvalue in value.items():
        val = []
        for index, nvalue_ in enumerate(nvalue.values()):
            if index == 0:
                val.append(0)
            else:
                val.append(float(list(nvalue.values())[index-1])/1000)
            size = np.empty((1,1,3))
            size[...,0:2] = 1
            size[...,2] = float(list(nvalue.values())[index])/1000
            bg = gl.GLBarGraphItem(np.array([[[labels[key], shops[nkey], sum(val)]]]), size)
            bg.setColor(colors[list(nvalue.keys())[index]])
            w.addItem(bg)
#            legend.addItem(colors[list(nvalue.keys())[index]], list(nvalue.keys())[index])
#            w.addItem(legend)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

# # ***********************************************************************
# import json
#
#
# def pack(pyvar):
#     jvar = json.dumps(pyvar)
#     jvar_byte = jvar.encode('utf-8')
#     dlen = len(jvar_byte)
#     print('dlen = %d' % dlen)
#     packlen = int.to_bytes(dlen, 4, 'little')
#     return packlen + jvar_byte
#
# a = {
#     'type': 1,
#     'time': 0.02
# }
#
# jvar = json.dumps(a)
# byvar = jvar.encode('utf-8')
# print(jvar, len(jvar))
# print(byvar, len(byvar))
# print(pack(a))

# # ***********************************************************************
# class ClientSocket(object):
#
#     def __init__(self):
#         """初始化套接字"""
#         self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#         self.rxbuf = None
#         # recv_data()处理完报文，没有return，通过这让client的处理函数获取
#         self.re_data = None
#
#         # # selectors
#         # self.sel = selectors.DefaultSelector()
#         # self.socket_list = []
#
#     def connect_server(self, LOCALADDR):
#         """连接服务器"""
#         self.conn.connect(LOCALADDR)
#
#
#
#     def check_json(self, data):
#         try:
#             recv_data = json.loads(data)
#             return recv_data
#         except:
#             print('Received data format error! Please wait for the server to resend.')
#             error_message = 'Your data format error! Please check and resend.'
#             self.send_data(error_message)
#             return False
#
#     def recv_data(self):
#         """
#         获得服务器返回数据
#         n == 0 的机制待完善
#         :return:
#         """
#         is_complete = True
#         while is_complete:
#             try:
#                 # 如果之前已收到，则接上，如果没有，则接收
#
#                 if self.rxbuf:
#                     self.rxbuf = self.rxbuf + self.conn.recv(65536)
#                 else:
#                     self.rxbuf = self.conn.recv(65536)
#                 n = len(self.rxbuf)
#                 while n:
#                     print('receive')
#                     # 若报文头都没有收够，则退出循环，接着让外面循环recv_data()，接着收
#                     if n < 4:
#                         print('<4')
#                         break
#                     # [length] field is complete
#                     data_len = int.from_bytes(self.rxbuf[0:4], 'little')
#                     # 报文头已收好，但本次消息未收全，循环recv_data()，接着收
#                     if n < 4 + data_len:
#                         break
#                     # [length][data] fields are complete
#                     recv_json = self.rxbuf[2:2 + data_len].decode('utf-8')
#                     # process recv_json
#                     # 因为return则函数中断，因此通过让client调用recv_data()函数后，获取self.re_data得到报文信息
#                     self.re_data += self.check_json(recv_json)
#
#                     # 本次消息处理完，后续消息接上，进行下次循环
#                     self.rxbuf = self.rxbuf[2 + data_len:]
#                     n = len(self.rxbuf)
#                     # 待完善。如果没有剩余消息，则接收完毕，退出函数。但是有个缺陷，万一正好接收了一个报文，则会漏掉后面的一条报文。
#                     if n == 0:
#                         is_complete = False
#                         return self.re_data
#             except socket.error as e:
#                 err = e.args[0]
#                 if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
#                     pass
#                 else:
#                     raise e
#
#
#     def package_utf8(self, message_json):
#         """发送前，封装报文，加报头，返回二进制报文"""
#         message_json_byte = message_json.encode('utf-8')
#         data_len = len(message_json_byte)  # 获取data的字节数应该用len，getsizeof()获取的是变量占用的大小
#         pack_len = int.to_bytes(data_len, 4, 'little')  # 报头4字节长
#         return pack_len + message_json_byte
#
#     def send_data(self, message):
#         """向服务器发送命令"""
#         # self.conn.sendall(json.dumps(message).encode('utf-8'))
#         self.conn.sendall(self.package_utf8(json.dumps(message)))
#
#
#
# if __name__ == '__main__':
#     cs = ClientSocket()
#     cs.connect_server(('127.0.0.1', 55500))
#     cs.recv_data()
