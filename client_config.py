# 服务器相关配置
# SERVER_IP = '127.0.0.1'
# SERVER_PORT = 55500
# LOCALADDR = (SERVER_IP, SERVER_PORT)


# 数据协议相关配置
# DELIMITER = '|'# 自定义协议数据分隔符


# 命令设置
command = {
    'type': 'command',

    'reboot': 0,
    'start': 1,
    'suspend': 2,
    'node_status': 3,
    'load_business': 4,
    'adjust_speed': 5,
    'close_system': 'c',# 关闭仿真系统
    'data': 'd',
    'exit': 'e'# 客户端退出连接
}