# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DisplayControl.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(720, 479)
        MainWindow.setStyleSheet("*{    \n"
"    font-family:微软雅黑;\n"
"    font-size:15px;\n"
"    color: #1d649c;\n"
"}\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.ip = QtWidgets.QLineEdit(self.groupBox_2)
        self.ip.setObjectName("ip")
        self.horizontalLayout_3.addWidget(self.ip)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.port = QtWidgets.QLineEdit(self.groupBox_2)
        self.port.setObjectName("port")
        self.horizontalLayout_3.addWidget(self.port)
        self.connectButton = QtWidgets.QPushButton(self.groupBox_2)
        self.connectButton.setObjectName("connectButton")
        self.horizontalLayout_3.addWidget(self.connectButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.verticalLayout_4.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setStyleSheet("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonStart = QtWidgets.QPushButton(self.groupBox)
        self.buttonStart.setObjectName("buttonStart")
        self.verticalLayout.addWidget(self.buttonStart)
        self.buttonRun = QtWidgets.QPushButton(self.groupBox)
        self.buttonRun.setObjectName("buttonRun")
        self.verticalLayout.addWidget(self.buttonRun)
        self.buttonSuspend = QtWidgets.QPushButton(self.groupBox)
        self.buttonSuspend.setObjectName("buttonSuspend")
        self.verticalLayout.addWidget(self.buttonSuspend)
        self.buttonNodeStatus = QtWidgets.QPushButton(self.groupBox)
        self.buttonNodeStatus.setObjectName("buttonNodeStatus")
        self.verticalLayout.addWidget(self.buttonNodeStatus)
        self.buttonSystemStatus = QtWidgets.QPushButton(self.groupBox)
        self.buttonSystemStatus.setObjectName("buttonSystemStatus")
        self.verticalLayout.addWidget(self.buttonSystemStatus)
        self.buttonLoadBusiness = QtWidgets.QPushButton(self.groupBox)
        self.buttonLoadBusiness.setObjectName("buttonLoadBusiness")
        self.verticalLayout.addWidget(self.buttonLoadBusiness)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.MessageBody = QtWidgets.QTextEdit(self.groupBox)
        self.MessageBody.setStyleSheet("QTextEdit{\n"
"    background-image:bgpicture.png\n"
"}")
        self.MessageBody.setObjectName("MessageBody")
        self.horizontalLayout.addWidget(self.MessageBody)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 20)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.timeLabel = QtWidgets.QLabel(self.groupBox)
        self.timeLabel.setText("")
        self.timeLabel.setObjectName("timeLabel")
        self.horizontalLayout_2.addWidget(self.timeLabel)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.runSpeed = QtWidgets.QComboBox(self.groupBox)
        self.runSpeed.setObjectName("runSpeed")
        self.runSpeed.addItem("")
        self.runSpeed.addItem("")
        self.runSpeed.addItem("")
        self.runSpeed.addItem("")
        self.runSpeed.addItem("")
        self.horizontalLayout_2.addWidget(self.runSpeed)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 4)
        self.horizontalLayout_2.setStretch(3, 1)
        self.horizontalLayout_2.setStretch(4, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_4.setStretch(1, 5)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "显示控制"))
        self.groupBox_2.setTitle(_translate("MainWindow", "配置"))
        self.label_3.setText(_translate("MainWindow", "服务器IP："))
        self.ip.setText(_translate("MainWindow", "192.168.1.10"))
        self.label_4.setText(_translate("MainWindow", "服务器Port："))
        self.port.setText(_translate("MainWindow", "55500"))
        self.connectButton.setText(_translate("MainWindow", "连接"))
        self.groupBox.setTitle(_translate("MainWindow", "演示"))
        self.buttonStart.setText(_translate("MainWindow", "启动系统"))
        self.buttonRun.setText(_translate("MainWindow", "运行系统"))
        self.buttonSuspend.setText(_translate("MainWindow", "暂停系统"))
        self.buttonNodeStatus.setText(_translate("MainWindow", "节点状态"))
        self.buttonSystemStatus.setText(_translate("MainWindow", "系统状态"))
        self.buttonLoadBusiness.setText(_translate("MainWindow", "加载业务"))
        self.MessageBody.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'微软雅黑\'; font-size:15px; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label.setText(_translate("MainWindow", "系统运行时间："))
        self.label_2.setText(_translate("MainWindow", "系统运行速度："))
        self.runSpeed.setItemText(0, _translate("MainWindow", "1/5"))
        self.runSpeed.setItemText(1, _translate("MainWindow", "1/2"))
        self.runSpeed.setItemText(2, _translate("MainWindow", "1"))
        self.runSpeed.setItemText(3, _translate("MainWindow", "2"))
        self.runSpeed.setItemText(4, _translate("MainWindow", "5"))