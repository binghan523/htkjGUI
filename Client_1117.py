import time
import os
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
    - 线程
    - 主窗口UI 按钮触发处理方法
    - 子窗口实例
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
    signal_nodeStatus = pyqtSignal(object)
    # 与生长速率折线图窗口实现信号传输
    signal_systemStatus = pyqtSignal(object, object, object)
    # step，持续推进
    signal_step = pyqtSignal()

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
        # 判断主窗口是否正在运行
        self.is_MainWindow_running = True

        # *******************************************************
        # 线程

        # socket收发线程
        self.thread_rx = threading.Thread(target=self.conn.rx)  # 数据放入self.rxbuf_q
        self.thread_tx = threading.Thread(target=self.conn.tx)
        # 监测是否收到数据，并解析
        self.thread_parseRecvAndHandle = threading.Thread(target=self.parseAndHandle_recv)
        # 初始化建立画3D图界面刷新线程的对象
        self.thread_plotNodeStatus = PlotNode()
        # 初始化建立画折线图界面刷新线程的对象
        self.thread_plotSystemStatus = PlotSystem()
        # 创建打开节点显示窗口的线程
        # self.thread_ui_ChildUI_Node = threading.Thread(target=self.ui_ChildUI_NodeStatus_show)
        # 创建持续推进仿真的发送线程
        self.thread_advanceSimulation = threading.Thread(target=self.ui_run_timedSending)

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
        # 子窗口实例

        # 在主窗口类的初始化函数中对子窗口进行实例化。若在其它函数中进行实例化，可能会出现子窗口闪退的问题
        # alt+Enter快速创建以选中词为名的函数，类，参数等
        # 实例化节点3D图子窗口
        self.ChildUI_NodeStatus = ChildWinNodeStatus()
        self.ChildUI_NodeStatus.signal_exit.connect(self.activeExit_nodeUI)
        # 实例化生长速率子窗口
        self.ChildUi_SystemStatus = ChildWinSystemStatus()
        self.ChildUi_SystemStatus.signal_exit.connect(self.activeExit_systemUI)

        # *******************************************************
        # 信号与槽触发

        # 接收到节点数据之后，触发在子窗口上画3D图
        self.signal_nodeStatus.connect(self.ui_plotNodeStatus_child)
        # 接收到生长速率数据后，触发在子窗口上画折线图
        self.signal_systemStatus.connect(self.ui_plotSystemStatus_child)
        self.signal_step.connect(self.ui_run_timedSending)

        # *******************************************************
        # 其它

        # # 节点状态数据锁
        # self.lock_node = threading.Lock()
        # # 系统状态数据锁
        # self.lock_system = threading.Lock()
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
            self.is_MainWindow_running = False
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

    def activeExit_nodeUI(self):
        """
        处理节点窗口被手动关闭的反应
        - 关闭node画图线程
        """
        self.thread_plotNodeStatus.terminate()

    def activeExit_systemUI(self):
        """
        处理节点窗口被手动关闭的反应
        - 关闭system画图线程
        """
        self.thread_plotSystemStatus.terminate()

    def parseAndHandle_recv(self):
        """
        用于数据处理线程：
        while循环检查 收 缓存self.rxbuf_q，若有数据
        - 解析数据type，根据type运行相应函数handle
            - 收 4，R_SIM_STEP_CON
                - 置is_ACK为True
                - 刷新主界面系统仿真时间label，self.ui_runningTime
            - 收 6，R_SIM_SUSPEND_NODESTATUS
                - 消息窗提示收到暂停推进请求和节点状态数据
                    - 置标志位self.is_allowed_promote为False，用于停止仿真推进线程self.thread_advanceSimulation
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
        while self.is_MainWindow_running:
            is_plot = ack_times % 40
            if len(self.rxbuf_q):
                py_data = self.rxbuf_q.pop(0)
                # print(py_data)
                dtype = py_data['type']
                if dtype == self.R_SIM_STEP_CON:
                    self.ui_runningTime()
                    ack_times += 1
                    self.is_ACK = True
                    # self.signal_step.emit()
                    # self.ui_run_timedSending()
                if dtype == self.R_SIM_SUSPEND_NODESTATUS and is_plot == 0:
                    self.ui_print_message('********************************\n' + 'Receive pause push request and node status information.')
                    # self.is_allowed_promote = False
                    self.data_NodeStatus = py_data
                    self.buttonNodeStatus.click()
                if dtype == self.R_SIM_SYSTEMSTATUS and is_plot == 0:
                    self.ui_print_message('********************************\n' + 'Receive system status information.')
                    self.data_SystemStatus = py_data
                    self.buttonSystemStatus.click()

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
                self.thread_parseRecvAndHandle.start()
                self.thread_advanceSimulation.start()
                # 创建线程处理服务器返回的数据
                # threading.Thread(target=lambda: self.response_handle()).start()
            except Exception as e:
                self.ui_print_message('********************************\n' + 'Connection failed! Please check that the server is turned on.')
                print(e)
            # self.ui_runningTime()
            # self.timer.start(1000)

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
        重启系统，0
        :return:
        :return:
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
        while self.is_MainWindow_running:
            # if self.is_connected and self.is_allowed_promote:
            # 当已与仿真主控连接且允许继续推进时，才执行
            try:
                # 已收到确认消息，则继续发送，否则直接进行下次循环
                if self.is_ACK and self.is_connected and self.is_allowed_promote is True:
                    # 累计已运行时间
                    time_remaining = interval - time.time() % interval
                    time.sleep(time_remaining)
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
            - 初始化nodeStatus_dict，提取数据self.data_NodeStatus
                - 若无数据，pass，用于排除刚开始，还未收到数据按钮就被点击的情况
                - 若有数据
                    - 上锁释放锁，保护数据
                    - 按需分类重新组装成nodeStatus_dict
                    - nodeStatus_dict
            - 组装完毕，将数据通过信号与槽发射，触发self.ui_plotStatus_child画图
        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            self.ChildUI_NodeStatus.show()
            # self.thread_plotNodeStatus.start()
            if len(self.data_NodeStatus):
                nodeStatus_dict = dict()
                nodeStatus_dict.update(
                    {
                        'num_nodes': 0,
                        # addr == leader, 是簇头；否则，不是
                        'addr': [],  # int
                        'leader': [],  # int
                        'started': [],  # bool，是否正在运行
                        'joined': [],  # bool，是否入网
                        'type': [],  # bool，在传来的数据中，key为type
                        'malicious': [],  # bool，是否恶意
                        'x': [],  # double
                        'y': [],  # double
                        'z': [],  # double
                    }
                )
                nodeStatus_dict['num_nodes'] = self.data_NodeStatus['state']['num_nodes']
                nodes = self.data_NodeStatus['state']['nodes']
                for i in range(nodeStatus_dict['num_nodes']):
                    nodeStatus_dict['addr'].append(nodes[i]['addr'])
                    nodeStatus_dict['leader'].append(nodes[i]['leader'])
                    nodeStatus_dict['started'].append(nodes[i]['started'])
                    nodeStatus_dict['joined'].append(nodes[i]['joined'])
                    nodeStatus_dict['type'].append(nodes[i]['type'])
                    nodeStatus_dict['malicious'].append(nodes[i]['malicious'])
                    nodeStatus_dict['x'].append(nodes[i]['x'] / 1000)  # km
                    nodeStatus_dict['y'].append(nodes[i]['y'] / 1000)
                    nodeStatus_dict['z'].append(nodes[i]['z'] / 1000)
                # 用完self.dataNodeStatus即扔，免得卡死
                self.data_NodeStatus = dict()
                print('NodeStatus: ', nodeStatus_dict)
                self.signal_nodeStatus.emit(nodeStatus_dict)
            else:
                # 刚开始，还未收到数据，按钮就被点击
                pass

    def ui_systemStatus_handle(self):
        """
        系统状态按钮被触发，或收到系统状态数据触发
        - 检测是否已连接成功，用于在未连接时按钮就被点击给出提示
        - 若已连接服务器
            - 打开生长速率折线UI
            - 打开共识时间折线UI
            - 若数据长度为0，pass
            - 若有数据
                - 提取数据self.data_SystemStatus
                - 若数据含有共识时间 0
                    - 组装共识时间list、生长速率list、已推进时间list
                    - signal_systemStatus发射信号，至ui_plotSystemStatus_child画两张折线图，且默认置防篡改率为100%
                - 若数据含防篡改率 1
                    - signal_systemStatus发射信号，至ui_plotSystemStatus_child置防篡改率label
        """
        if self.is_connected is False:
            self.ui_print_message('Please establish a connection first!')
        else:
            self.ChildUi_SystemStatus.show()
            if len(self.data_SystemStatus):
                value = self.data_SystemStatus['value']
                if self.data_SystemStatus['stat'] == 0:
                    self.list_consensusLatency.append(value)
                    rate_growth = 1 / value
                    self.list_growth_rate.append(rate_growth)
                    self.list_growth_rate_SimulationTime.append(self.time_simulated)
                    self.signal_systemStatus.emit(self.list_consensusLatency, self.list_growth_rate, self.list_growth_rate_SimulationTime)
                if self.data_SystemStatus['stat'] == 1:
                    self.signal_systemStatus.emit(value, None, None)
            else:
                pass

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

    def ui_plotNodeStatus_child(self, nodeStatus):
        """接收到节点数据后，在子窗口上画图"""
        self.thread_plotNodeStatus.nodeStatus = nodeStatus
        self.thread_plotNodeStatus.signal.connect(self.ChildUI_NodeStatus.child_plotNode)
        self.thread_plotNodeStatus.start()  # 放在ui_nodeStatus_handle里面了

    def ui_plotSystemStatus_child(self, par1, par2, par3):
        """
        由ui_SystemStatus_handle()的self.signal_nodeStatus.emit()触发
        - 判断收到的数据为防篡改率还是共识时间
            - 若par2 为None，接收到防篡改率
                :param par1: value
                :param par2: None
                :param par3: None
            - 若par2 为数据，接收到生长速率
                - 默认置防篡改率为100%
                :param par1: self.list_consensusLatency
                :param par2: self.list_growth_rate
                :param par3: self.list_growth_rate_SimulationTime
                - 将数据交给Class PlotSystem的实例对象thread_plotSystemStatus，启动该线程画图
        :return:
        """
        # 若窗口已经打开，则保持，否则打开
        if par2 is None:
            if par1 != 1:
                self.ChildUi_SystemStatus.rate_anti.setText(str(par1))
        else:
            self.ChildUi_SystemStatus.rate_anti.setText('100%')
            self.thread_plotSystemStatus.consensusLatency = par1
            self.thread_plotSystemStatus.rateGrowth = par2
            self.thread_plotSystemStatus.simulationTime = par3
            self.thread_plotSystemStatus.signal.connect(self.ChildUi_SystemStatus.child_plotSystem)
            self.thread_plotSystemStatus.start()


class PlotNode(QThread):
    """
    给予画图多线程
    提供点数据分析功能
    """
    signal = pyqtSignal(object, object, object, object)  # 定义信号，根据信息交互设置参数位

    def __init__(self):
        super(PlotNode, self).__init__()
        self.nodeStatus = {}
        self.distance = 0  # 用于3D图的视角高度设定
        self.num_nodes = None
        self.x = None
        self.y = None
        self.z = None
        self.started = None
        self.malicious = None
        # 初始化numpy.ndarray类型的数据，用于画散点图
        self.pos = None
        self.size = None
        self.color = None

    def plotNodeStatus(self):
        """
        初始化画散点图所需的点数据：position，size，color
        监测是否有
        :return:
        """
        if len(self.nodeStatus):
            self.distance = 0  # 用于3D图的视角高度设定
            self.num_nodes = self.nodeStatus['num_nodes']
            self.x = self.nodeStatus['x']
            self.y = self.nodeStatus['y']
            self.z = self.nodeStatus['z']
            self.started = self.nodeStatus['started']
            self.malicious = self.nodeStatus['malicious']

            # 设置numpy.ndarray类型的数据，用于画散点图
            self.pos = np.empty((self.num_nodes, 3))
            self.size = np.empty(self.num_nodes)
            self.color = np.empty((self.num_nodes, 4))

            for i in range(self.num_nodes):
                self.pos[i] = (self.x[i], self.y[i], self.z[i])
                max_num = max(self.x[i], self.y[i], self.z[i])
                if abs(self.distance) < abs(max_num):
                    self.distance = abs(max_num)
                self.size[i] = 0.5
                if self.started[i] is True and self.malicious[i] is False:
                    self.color[i] = (0.0, 1.0, 0.0, 0.5)  # 绿色
                elif self.malicious[i] is True:
                    self.color[i] = (1.0, 0.0, 0.0, 0.5)  # 红色
                else:
                    self.color[i] = (1, 1, 1, 0.5)  # 灰色

            self.nodeStatus = dict()
            return True

        return False

    def run(self):
        # 处理数据，准备发射
        if self.plotNodeStatus():
            # 向连接槽发射信号，触发self.ChildUI_NodeStatus.child_plotNode
            self.signal.emit(self.distance, self.pos, self.size, self.color)


class PlotSystem(QThread):
    """
    处理生长速率与共识时间，画折线图
    """
    signal = pyqtSignal(object, object, object)

    def __init__(self):
        super(PlotSystem, self).__init__()
        self.consensusLatency = []
        self.rateGrowth = []
        self.simulationTime = []

    def plotSystemStatus(self):
        """
        好像用不到这个函数，用也是对数据作二次处理
        """
        pass

    def run(self):
        # 向连接槽发射信号，触发窗口类中画图函数
        self.signal.emit(self.consensusLatency, self.rateGrowth, self.simulationTime)


class ChildWinNodeStatus(QDialog, Ui_NodeStatus):
    signal_exit = pyqtSignal()

    def __init__(self):
        super(ChildWinNodeStatus, self).__init__()
        self.setupUi(self)
        # 设置窗口最小化与最大化按钮，关闭按钮置灰
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        # pyside2中需要先声明第三方控件，因为PlotWidget为第三方PyQtgraph里面的
        # loader.registerCustomWidget(pg.PlotWidget)
        # self.ui = uic.loadUi("ui_client/NodeStatus.ui")

    def child_plotNode(self, distance, pos, size, color):
        self.guiplot.clear()
        self.guiplot.opts['distance'] = distance * 3  # 初始视角高度距中心的距离
        g = gl.GLGridItem()
        size_axes = distance * 3
        g.setSize(x=size_axes, y=size_axes, z=size_axes)
        self.guiplot.addItem(g)
        sp = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        self.guiplot.addItem(sp)

    def closeEvent(self, event):
        self.signal_exit.emit()


class ChildWinSystemStatus(QDialog, Ui_SystemStatus):
    signal_exit = pyqtSignal()

    def __init__(self):
        super(ChildWinSystemStatus, self).__init__()
        self.setupUi(self)
        # 设置窗口最小化与最大化按钮，关闭按钮置灰
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        #
        # self.p = self.guiplot.addPlot()
        # self.p.setDownsampling(mode='peak')
        # self.p.setClipToView(True)
        # self.curve = self.p.plot()
        #
        # self.data = np.empty(100)
        # self.ptr = 0

    def child_plotSystem(self, consensusLatency, growth_rate, list_time):
        """
        由PlotSystem类的实例signal emit触发，画共识时间与 生长速率折线图
        :param consensusLatency:
        :param growth_rate:
        :param list_time:
        :return:
        """
        if consensusLatency:
            self.guiplot_consensus.clear()
            self.guiplot_consensus.plot(list_time, consensusLatency)
            self.guiplot_growthRate.clear()
            self.guiplot_growthRate.plot(list_time, growth_rate)
        else:
            pass

    def closeEvent(self, event):
        self.signal_exit.emit()


app = QApplication([])
app.setWindowIcon(QIcon('icon.jpg'))
clientWindow = ClientTCP()
childWindow = ChildWinNodeStatus()
clientWindow.show()
app.exit(app.exec_())

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     app.setWindowIcon(QIcon=('logo.jpg'))
#     clientWindow = ClientTCP()
#     childWindow = ChildWinNodeStatus()
#     clientWindow.show()
#     sys.exit(app.exec_())
