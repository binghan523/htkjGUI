import time
import os
import sys
import math
import threading
from ClientSocket import ClientSocket

from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
import pyqtgraph.opengl as gl
import numpy as np

# 静态加载
from DisplayControl import Ui_MainWindow
from NodeStatus import Ui_NodeStatus
from SystemStatus import Ui_SystemStatus


# *******************************************************
# 这样有个好处，每次更改UI的时候，免去了改一次就要转化为python文件的麻烦
# Uic_MainWindow = uic.loadUiType("ui_client/DisplayControl.ui")[0]

# 然而静态加载节点窗口还是出错，还是在类内用loadUi吧，暂且注释掉
# Uic_NodeStatus_class = uic.loadUiType("ui_client/NodeStatus.ui")[0]
# *******************************************************


class ClientTCP(QMainWindow, Ui_MainWindow):
    """
    客户端，主窗口UI
    - 信号与槽
    - 与服务器交互协议，type
    - socket
        - 实体为 实例.csock
    - 标志位
    - 子窗口实例与线程
    - 主窗口UI 按钮触发处理方法
    - 信号与槽触发
    - 其它
    """

    # *******************************************************
    # 与服务器交互协议，type

    # 收到服务器反馈，推进确认消息
    R_SIM_STEP_CON = 4
    # 收到服务器仿真暂停请求，附带节点状态消息
    R_SIM_SUSPEND_NODESTATUS = 6
    # 收到服务器统计量
    R_SIM_SYSTEMSTATUS = 9

    # *******************************************************
    # 信号与槽

    # 与子窗口实现信号传输
    # signal_nodeStatus = pyqtSignal(object)
    # 与生长速率折线图窗口实现信号传输
    # signal_systemStatus = pyqtSignal(object, object, object)
    # step，持续推进
    # signal_step = pyqtSignal()
    # 用于帮助thread_parseRecvAndHandle刷新时间
    signal_setTime = pyqtSignal()

    def __init__(self):

        super(ClientTCP, self).__init__()
        self.setupUi(self)

        # *******************************************************
        # socket

        # ClientSocket对象
        self.conn = ClientSocket()
        # socket实体
        # self.conn.csock
        # 设置回调函数
        self.conn.setRecvCallback(self.recv)

        # *******************************************************
        # 标志位

        # 处理服务器响应线程是否正在运行
        self.is_running = True
        # 处理多次点击连接按钮情况
        self.is_connected = False
        # 是否允许发送推进仿真消息
        self.is_allowed_promote = False
        # 是否收到推进之后的反馈消息，若收到才可进行下一次定时推进，否则，等待
        self.is_ACK = False
        # 判断节点窗口是否正在运行
        self.is_nodeWindow_show = False
        # 判断主窗口是否正在运行
        self.is_systemWindow_show = False

        # *******************************************************
        # 窗口实例与线程

        # 在主窗口类的初始化函数中对子窗口进行实例化。若在其它函数中进行实例化，可能会出现子窗口闪退的问题
        # 实例化节点3D图子窗口
        self.ChildUI_NodeStatus = ChildWinNodeStatus()
        # 实例化生长速率子窗口
        self.ChildUi_SystemStatus = ChildWinSystemStatus()

        # socket收发线程
        self.thread_rx = threading.Thread(target=self.conn.rx)  # 数据放入self.rxbuf_q
        self.thread_tx = threading.Thread(target=self.conn.tx)
        # 监测是否收到数据，并解析
        self.thread_parseRecvAndHandle = threading.Thread(target=self.parseAndHandle_recv)
        # 创建持续推进仿真的发送线程
        self.thread_advanceSimulation = threading.Thread(target=self.ui_run_timedSending)

        # 初始化建立画3D图界面刷新线程的对象
        self.QThread_plotNodeStatus = QThreadPlotNode(self.ChildUI_NodeStatus)
        # 初始化建立画折线图界面刷新线程的对象
        self.QThread_plotSystemStatus = QThreadPlotSystem(self.ChildUi_SystemStatus)

        # *******************************************************
        # 主窗口UI 按钮触发处理方法

        self.buttonStart.clicked.connect(self.ui_startSystem_handle)
        self.buttonRun.clicked.connect(self.ui_runSystem_handle)
        self.buttonSuspend.clicked.connect(self.ui_suspendSystem_handle)
        self.connectButton.clicked.connect(self.ui_linkAndStart)
        self.buttonNodeStatus.clicked.connect(self.ui_nodeStatus_handle)
        self.buttonSystemStatus.clicked.connect(self.ui_systemStatus_handle)
        self.buttonLoadBusiness.clicked.connect(self.ui_business_handle)
        self.runSpeed.currentIndexChanged.connect(self.ui_runSystem_handle)
        # self.buttonClose.clicked.connect(self.ui_closeSystem_handle)
        # self.speedSlider.valueChanged.connect(self.ui_runSystem_handle)  # valueChanged, sliderPressed, sliderMoved, sliderReleased

        # *******************************************************
        # 信号与槽触发

        # 更新主窗口UI的系统运行时间
        self.signal_setTime.connect(self.ui_runningTime)
        # 接收到节点数据之后，触发在子窗口上画3D图
        # self.signal_nodeStatus.connect(self.ui_plotNodeStatus_child)
        # 接收到生长速率数据后，触发在子窗口上画折线图
        # self.signal_systemStatus.connect(self.ui_plotSystemStatus_child)
        # 推进仿真
        # self.signal_step.connect(self.ui_run_timedSending)

        # *******************************************************
        # 其它

        # # 节点状态数据锁
        self.lock_node = threading.Lock()
        # # 系统状态数据锁
        self.lock_system = threading.Lock()
        # 存放接收到的数据
        self.rxbuf_q = []
        # 存放节点状态数据，由self.ui_linkAndStart放入，self.response_nodeStatus_handle提取并处理
        self.data_NodeStatus = dict()
        # 存放系统统计数据，由self.ui_linkAndStart放入，self.response_systemStatus_handle提取并处理
        self.data_SystemStatus = dict()
        # 存储响应控制函数
        self.response_handle_functions = dict()
        # 存储共识时间
        self.list_consensusLatency = []
        # 存储生长速率
        self.list_growth_rate = []
        # 存储收到生长速率的系统已推进时刻
        self.list_growth_rate_SimulationTime = []
        # 系统已推进到的时间
        self.time_simulated = 0.00
        # 系统运行速度
        self.speed = 0
        # 设置允许收到的type表
        self.type_list = [self.R_SIM_STEP_CON, self.R_SIM_SUSPEND_NODESTATUS, self.R_SIM_SYSTEMSTATUS]

    def recv(self, pyvar):
        """
        接收数据，并把python数据放入缓存self.rxbuf_q中
        """
        self.rxbuf_q.append(pyvar)

    def exit(self):
        """关闭client socket,退出连接"""
        self.is_running = False
        self.conn.csock.close()
        self.is_connected = False
        self.ui_print_message('********************************\n' + 'Disconnected successfully.')

    def closeEvent(self, event):
        """
        主窗口关闭后，令子窗口也关闭
        对主窗口的函数closeEvent进行重构
        - 退出软件时结束所有进程
        :param event:
        :return:
        """
        try:
            self.is_allowed_promote = False
            reply = QMessageBox.question(self,
                                         '本程序',
                                         '是否要退出本程序',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No
                                         )
            if reply == QMessageBox.Yes:
                event.accept()
                os._exit(0)
            else:
                event.ignore()
        except Exception as e:
            print(e)
            pass

    def parseAndHandle_recv(self):
        """
        用于数据处理线程：
        while循环检查 收 缓存self.rxbuf_q，若有数据
        - 解析数据type，根据type运行相应函数handle
            - 收 4，R_SIM_STEP_CON
                - 置is_ACK为True
                - 刷新主界面系统仿真时间label，self.ui_runningTime
            - 收 6，R_SIM_SUSPEND_NODESTATUS
                - 消息窗提示收到节点状态数据
                - 将Node数据传给self.data_NodeStatus
                - 触发节点状态按钮，打开节点窗口UI
                    - ui_nodeStatus_handle提取self.data_NodeStatus，做后续画图操作
            - 收 9，R_SIM_SYSTEMSTATUS
                - 消息窗提示收到系统状态数据
                - 将Node数据传给self.data_SystemStatus
                    - ui_systemStatus_handle提取self.data_SystemStatus，做后续UI操作
                - 此处不打开系统状态UI，因为需要进一步判断接收的是防篡改率，还是共识时间，当确定之后再打开对应窗口
        """
        ack_times = 0
        while True:
            # 控制帧率
            is_plotAllowed = ack_times % 20
            if len(self.rxbuf_q):
                py_data = self.rxbuf_q.pop(0)
                # print(py_data)
                dtype = py_data['type']
                if dtype == self.R_SIM_STEP_CON:
                    self.is_ACK = True
                    setTime_time = time.process_time()
                    # self.ui_runningTime()
                    print('setTime is: %.6f' % setTime_time)
                    self.signal_setTime.emit()
                    ack_times += 1
                if dtype == self.R_SIM_SUSPEND_NODESTATUS and is_plotAllowed == 0:
                    # self.ui_print_message('********************************\n' + 'Receive node status information.')
                    if not self.is_nodeWindow_show:
                        self.buttonNodeStatus.click()
                    # 若收到节点数据要暂停发送，则启用下行代码
                    # self.is_allowed_promote = False
                    self.data_NodeStatus = py_data

                    self.lock_node.acquire()
                    append_time = time.process_time()
                    # self.QThread_plotNodeStatus.buf_nodeStatus.append(self.data_NodeStatus)
                    self.QThread_plotNodeStatus.append_buf(self.data_NodeStatus)
                    print('append time is: %.5f' % append_time)
                    self.lock_node.release()

                if dtype == self.R_SIM_SYSTEMSTATUS and is_plotAllowed == 0:
                    # self.ui_print_message('********************************\n' + 'Receive system status information.')
                    if not self.is_systemWindow_show:
                        self.buttonSystemStatus.click()
                    self.data_SystemStatus = py_data
                    self.lock_system.acquire()
                    self.QThread_plotSystemStatus.buf_systemStatus.append(self.data_SystemStatus)
                    self.QThread_plotSystemStatus.time_simulated = self.time_simulated
                    self.lock_system.release()

    # ****************************************************
    # UI功能模块，button收到点击，触发

    def ui_linkAndStart(self):
        """
        连接按钮被触发
        - UI获取输入框中 IP和Port，进行socket连接
            - 根据标志位self.is_connected判断连接是否已经建立
            - 若连接已建立，消息窗反馈
            - 若未建立，socket.connect()
                - 若连接成功，消息窗反馈成功
                    - 启动主UI收发线程
                    - 启动主UI数据解析线程self.thread_parseRecvAndHandle
                - 若失败，消息窗反馈，请检查服务器状况并重试
        """
        # 连接服务器
        if self.is_connected is True:
            self.ui_print_message('********************************\n' + 'Already connected. If you want to reconnect, please disconnect the previous connection.')
        else:
            try:
                self.ui_print_message('********************************\n' + 'Connecting to server...')
                self.conn.csock.connect(self.ui_getSERVERADDR())
                self.ui_print_message('Successfully connected.')
                self.is_connected = True
                self.thread_tx.start()
                self.thread_rx.start()
                self.QThread_plotNodeStatus.start()
                self.QThread_plotSystemStatus.start()
                self.thread_parseRecvAndHandle.start()
                self.thread_advanceSimulation.start()

            except Exception as e:
                self.ui_print_message('********************************\n' + 'Connection failed! Please check that the server is turned on.')
                print(e)

    def ui_getSERVERADDR(self):
        """
        从UI中获取用户输入的服务器IP和port，返回
        :return:
        :return:
        """
        server_ip = self.ip.text()
        server_port = int(self.port.text())
        SERVERADDR = (server_ip, server_port)
        return SERVERADDR

    def ui_startSystem_handle(self):
        """
        启动系统，0
        - 启动画图QThread子线程
        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            message = {
                'type': 0
            }
            self.conn.send(message)
            self.ui_print_message('********************************\n' + 'Start system...')

    def ui_run_timedSending(self, interval=0.1):
        """
        定时发送报文，推进仿真
        - 由signal_step触发，每次is_ACK变为True时，都会设置触发信号
        - 设置已运行到的时间self.time_simulated，累积量，记录已推进到的时刻
        - 设标志位is_ACK。
        - 暂停按钮触发后，设置is_ACK标志位为False，便可暂停发送
        """
        while True:
            # if self.is_connected and self.is_allowed_promote:
            # 当已与仿真主控连接且允许继续推进时，才执行
            try:
                # 已收到确认消息，则继续发送，否则直接进行下次循环
                if self.is_ACK and self.is_connected and self.is_allowed_promote is True:
                    # 累计已运行时间
                    # time_remaining = interval - time.time() % interval
                    # time.sleep(time_remaining)
                    # 直接相加在python中会有小数位数出错，因此借用time接力
                    time_float = self.time_simulated + round(float(self.speed) / 1000, 2)
                    self.time_simulated = round(time_float, 2)
                    # 准备消息
                    message = {
                        'type': 1,
                        'time': self.time_simulated
                    }
                    # 发送之后置self.is_ACK为False，当收到反馈消息后置True
                    self.is_ACK = False
                    # 执行定时发送操作
                    step_time = time.process_time()
                    print('step_time is: %.6f' % step_time)
                    self.conn.send(message)
            except Exception as e:
                raise e

    def ui_runSystem_handle(self):
        """
        推进仿真主控运行到某时刻
        由运行系统按钮或速度滑块移动触发
        - 判断是否连接成功
        - 若连接成功
            - 给予新的子线程，利用ui_run_timedSending()函数，定时发送
        :return:
        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            # 获取当前运行速度
            self.ui_runningSpeed()
            self.ui_print_message('********************************\n' + 'Run the system at a speed of %d ms each 100 ms.' % self.speed)

            try:
                # 线程
                self.is_allowed_promote = True
                self.is_ACK = True
                # self.signal_step.emit()
                # self.ui_run_timedSending()
                # self.thread_advanceSimulation.start()
            except Exception as e:
                # 若是重复start线程引起的错误则不管
                if type(e) is RuntimeError:
                    pass
                else:
                    raise e

    def ui_suspendSystem_handle(self):
        """
        停止发送推进消息，无需发送停止命令，也无需等待确认
        结合ui_run_timedSending()，置标志位self.is_allowed_promote为False
        :return:
        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            self.is_allowed_promote = False
            self.ui_print_message('********************************\n' + 'Pause system...')

    def ui_nodeStatus_handle(self):
        """
        节点状态按钮被触发，或收到节点状态数据触发
        - 检测是否已连接成功，用于在未连接时按钮就被点击给出提示
        - 若已连接服务器
            - 打开节点UI
            - 将新收到的节点数据交给QThread子线程处理
        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            if not self.is_nodeWindow_show:
                self.is_nodeWindow_show = True
                self.ChildUI_NodeStatus.show()

    def ui_systemStatus_handle(self):
        """
        系统状态按钮被触发，或收到系统状态数据触发
        - 检测是否已连接成功，用于在未连接时按钮就被点击给出提示
        - 若已连接服务器
            - 打开生长速率折线UI
            - 打开共识时间折线UI

        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            if not self.is_systemWindow_show:
                self.is_systemWindow_show = True
                self.ChildUi_SystemStatus.show()

    def ui_business_handle(self, business):
        """
        闲置
        :param business:
        :return:
        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            print(business)
            self.ui_print_message('********************************\n' + 'Loading business...')

    # def ui_closeSystem_handle(self):
    #     """
    #     关闭系统，关闭socket
    #     :return:
    #     """
    #     if self.is_connected is False:
    #         self.ui_print_message('Please establish a connection first!')
    #     else:
    #         message = {
    #             type: 'c'
    #         }
    #         self.conn.send(message)
    #         self.exit()

    def ui_runningSpeed(self):
        """
        speed is an int.
        每100ms推进20,50,100,200,500ms
        让ui_runSystem_handle()获取
        :param:
        :return: speed
        """
        text = self.runSpeed.currentText()
        if text == '1/5':
            self.speed = 20
        if text == '1/2':
            self.speed = 50
        if text == '1':
            self.speed = 100
        if text == '2':
            self.speed = 200
        if text == '5':
            self.speed = 500

    def ui_runningTime(self):
        """
        刷新仿真已推进到的时刻self.time_simulated
        :return:
        """
        # 向下取整数部分，s
        t_int = int(self.time_simulated)
        # 取小数部分，* 1000 为ms
        decimal_part = math.modf(self.time_simulated)
        t_dec = round(decimal_part[0], 2)
        t_dec_ms = int(t_dec * 1000)
        if self.time_simulated < 1:
            # 不足1秒
            text = str(t_dec_ms) + 'ms'
        elif self.time_simulated < 60:
            # 不足1分
            s = str(t_int) + 's'
            ms = str(t_dec_ms) + 'ms'
            text = s + ms
        elif self.time_simulated < 3600:
            # 不足一小时
            # 注意：python的整除为//,/为除带小数
            m = str(t_int // 60) + 'm'
            s = str(t_int % 60) + 's'
            ms = str(t_dec_ms) + 'ms'
            text = m + s + ms
        else:
            # 超过一小时
            h = str(t_int // 3600) + 'h'
            m = str((t_int % 3600) // 60) + 'm'
            s = str(t_int % 60) + 's'
            ms = str(t_dec_ms) + 'ms'
            text = h + m + s + ms
        self.timeLabel.setText(text)

    def ui_print_message(self, message):
        """
        在textEdit中打印系统运行提示，和消息
        注意：传入的message必须为str
        """
        self.MessageBody.append(message)
        # 保持滑动块最下
        self.MessageBody.moveCursor(QTextCursor.End)


class QThreadPlotNode(QThread):
    """
    本类作用；
    - analyze()函数处理节点状态数据，return处理后的数据
    - _argument:传入节点子窗口实例
    - _signal用来向向UI实例emit画图用的数据

    run()方法
    - 采用牛奶策略，循环持续检测self.buf_nodeStatus
    - 若buf有数据，则取出，运行analyze()处理，处理完后analyze()return
    - emit处理完后的数据，交_argument收到的子窗口实例的画图函数画图
    """
    signal = pyqtSignal(object, object, object, object)

    def __init__(self, _argument):
        """
        :param _argument: 为节点数据处理类的实例，由主窗口UI实例化，并在实例化本类时传入
        """
        super(QThreadPlotNode, self).__init__()
        self.class_childUI = _argument
        self.signal.connect(_argument.child_plotNode)
        self.buf_nodeStatus = list()  # 用于存储持续收到的节点数据

    def append_buf(self, node):
        """用于在主窗口中调用，append"""
        self.buf_nodeStatus.append(node)

    @staticmethod
    def analyzeNode(dataNode):
        """
        初始化画散点图所需的点数据：position，size，color，并return
        - 节点数据格式化，每个节点的不同属性组成对应的专属list，list的长度应恰为num_nodes
        - 组装成画图所用的dict，包含distance，pos，size，color
        :return: nodeStatus_dict
        """
        num_nodes = dataNode['state']['num_nodes']
        nodes = dataNode['state']['nodes']
        # 用于3D图的视角高度设定
        distance = 0
        # 设置numpy.ndarray类型的数据，用于画散点图
        pos = np.empty((num_nodes, 3))
        size = np.empty(num_nodes)
        color = np.empty((num_nodes, 4))

        for i in range(num_nodes):
            pos[i] = (nodes[i]['x'] / 1000, nodes[i]['y'] / 1000, nodes[i]['z'] / 1000)
            max_xyz = max(pos[i][0], pos[i][1], pos[i][2])
            if abs(distance) < abs(max_xyz):
                distance = abs(max_xyz)
            size[i] = 0.5
            if nodes[i]['started'] is True and nodes[i]['malicious'] is False:
                # 节点类型，1为簇首 黄，2为成员 绿，5为CA 天蓝，10为客户 蓝
                if nodes[i]['type'] == 1:
                    color[i] = (1.0, 1.0, 0.0, 1)  # 黄色
                if nodes[i]['type'] == 2:
                    color[i] = (0.0, 1.0, 0.0, 1)  # 绿色
                if nodes[i]['type'] == 5:
                    color[i] = (0.0, 1.0, 1.0, 1)  # 天蓝色
                if nodes[i]['type'] == 10:
                    color[i] = (0.0, 0.0, 1.0, 1)  # 蓝色
            elif nodes[i]['malicious'] is True:
                color[i] = (1.0, 0.0, 0.0, 0.5)  # 红色
            else:
                color[i] = (1, 1, 1, 0.5)  # 灰色

        # print('distance: {0},\npos: {1},\nsize: {2},\ncolor: {3}'.format(distance, pos, size, color))
        return distance, pos, size, color

    def run(self):
        while True:
            if len(self.buf_nodeStatus):
                dataNode = self.buf_nodeStatus.pop(0)
                distance, pos, size, color = self.analyzeNode(dataNode)
                self.signal.emit(distance, pos, size, color)


class QThreadPlotSystem(QThread):
    """
    处理生长速率与共识时间，画折线图
    本类作用；
    - analyze()函数处理系统状态数据
    - _argument:传入系统子窗口实例
    - _signal用来向UI实例emit画图用的数据，connect传来实例的child_plotSystem()

    run()方法：
    - 采用牛奶策略，循环持续检测self.buf_systemStatus
    - 若buf有数据，则取出，运行analyzeSystem()处理，处理完后analyze()return
    - emit处理完后的数据，交_argument收到的子窗口实例的画图函数画图
    """
    signal = pyqtSignal(object, object, object)

    def __init__(self, _argument):
        super(QThreadPlotSystem, self).__init__()

        self.class_childUI_system = _argument
        self.signal.connect(_argument.child_plotSystem)
        self.buf_systemStatus = []
        self.time_simulated = 0.00

        self.consensusLatency = []
        self.rateGrowth = []
        self.simulationTime = []

    def analyzeSystem(self, dataSystem):
        """
            处理系统数据，并return处理后的数据，用于run()中emit给传来的子窗口实例画图
            """
        value = dataSystem['value']
        if dataSystem['stat'] == 0:
            self.consensusLatency.append(value)
            rate_growth = 1 / value
            self.rateGrowth.append(rate_growth)
            self.simulationTime.append(self.time_simulated)
            # 向连接槽发射信号，触发窗口类中画图函数
            self.signal.emit(self.consensusLatency, self.rateGrowth, self.simulationTime)
        if dataSystem['stat'] == 1:
            self.class_childUI_system.rate_anti.setText(str(value))

    def run(self):
        while True:
            if len(self.buf_systemStatus):
                dataSystem = self.buf_systemStatus.pop(0)
                print('dataSystem is :', dataSystem)
                self.analyzeSystem(dataSystem)


class ChildWinNodeStatus(QDialog, Ui_NodeStatus):

    def __init__(self):
        super(ChildWinNodeStatus, self).__init__()
        self.setupUi(self)
        # 设置窗口最小化与最大化按钮，关闭按钮置灰
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        # pyside2中需要先声明第三方控件，因为PlotWidget为第三方PyQtgraph里面的
        # loader.registerCustomWidget(pg.PlotWidget)
        # self.ui = uic.loadUi("ui_client/NodeStatus.ui")

        # 初始化画图窗口设置，节省addItem(sp)的时间
        time_start = time.process_time()
        self.distance = 40  # 设置初始视角高度
        self.pos = np.zeros((1, 3))  # 初始化100个点位置
        self.size = np.ones(1) * 0.5  # 设置初始点大小0.5
        self.color = np.zeros((1, 4))  # 设置初始100个点的颜色，(0, 0, 0, 0)为透明无色
        self.g = gl.GLGridItem()
        self.size_axes = self.distance * 3
        self.g.setSize(x=self.size_axes, y=self.size_axes, z=self.size_axes)
        self.guiplot.addItem(self.g)
        self.sp = gl.GLScatterPlotItem(pos=self.pos, size=self.size, color=self.color, pxMode=False)
        self.guiplot.addItem(self.sp)  # 最主要的时间花费在这
        time_end = time.process_time()
        print('Time spent on draw is: %.6f' % (time_end - time_start))

    def child_plotNode(self, distance, pos, size, color):
        """
        收到节点数据，更新画图
        - 已达到微秒级，卡顿的原因不在这
        """
        time_draw = time.process_time()
        print('draw:', time_draw)
        # self.guiplot.clear() # clear会把item都清掉，不要用
        self.guiplot.opts['distance'] = distance * 3
        self.size_axes = distance * 3
        self.g.setSize(x=self.size_axes, y=self.size_axes, z=self.size_axes)
        # self.guiplot.addItem(g)
        self.sp.setData(pos=pos, size=size, color=color, pxMode=False)


class ChildWinSystemStatus(QDialog, Ui_SystemStatus):

    def __init__(self):
        super(ChildWinSystemStatus, self).__init__()
        self.setupUi(self)
        # 设置窗口最小化与最大化按钮，关闭按钮置灰
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

    def child_plotSystem(self, consensusLatency, growth_rate, list_time):
        """
        由PlotSystem类的实例signal emit触发，画 共识时间 与 生长速率 折线图
        :param consensusLatency:
        :param growth_rate:
        :param list_time:
        :return:
        """
        if consensusLatency:
            # self.guiplot_consensus.clear()
            self.guiplot_consensus.plot(list_time, consensusLatency)
            # self.guiplot_growthRate.clear()
            self.guiplot_growthRate.plot(list_time, growth_rate)
        else:
            pass


app = QApplication(sys.argv)
app.setWindowIcon(QIcon('icon.jpg'))
clientWindow = ClientTCP()
childWindow = ChildWinNodeStatus()
clientWindow.show()
sys.exit(app.exec_())
