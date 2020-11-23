import json


def pack(pyvar):
    jvar = json.dumps(pyvar)
    jvar_byte = jvar.encode('utf-8')
    dlen = len(jvar_byte)
    print('dlen = %d' % dlen)
    packlen = int.to_bytes(dlen, 4, 'little')
    return packlen + jvar_byte

a = {
    'type': 1,
    'time': 0.02
}

jvar = json.dumps(a)
byvar = jvar.encode('utf-8')
print(jvar, len(jvar))
print(byvar, len(byvar))
print(pack(a))

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