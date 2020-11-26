# **********************************************************************
# import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

plt = pg.plot()
plt.setWindowTitle('pyqtgraph example: Legend')
plt.addLegend()

c1 = plt.plot([1,3,2,4], pen='r', name='red plot')
c2 = plt.plot([2,1,4,3], pen='g', fillLevel=0, fillBrush=(255,255,255,30), name='green plot')
c3 = plt.addLine(y=4, pen='y')
# TODO: add legend item indicating "maximum value"

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


# {   "type": 6,
#     "num_nodes": 10,
#     "nodes": [
#     {"addr": 0, "leader": 0, "started": true, "joined": false, "type": true, "name": "0", "x": 1.1, "y": 1.2, "z": 1.3, "malicious": true},
#     {"addr": 1, "leader": 0, "started": true, "joined": false, "type": true, "name": "1", "x": 2.1, "y": 3.2, "z": 3.3, "malicious": false},
#     {"addr": 2, "leader": 0, "started": true, "joined": false, "type": true, "name": "2", "x": 3.1, "y": 0.2, "z": 1.3, "malicious": true},
#     {"addr": 3, "leader": 0, "started": true, "joined": false, "type": true, "name": "3", "x": 10.1, "y": 5.2, "z": 9.3, "malicious": false},
#     {"addr": 4, "leader": 0, "started": true, "joined": false, "type": true, "name": "4", "x": 2.1, "y": 1.2, "z": 4.3, "malicious": false},
#     {"addr": 5, "leader": 0, "started": true, "joined": false, "type": true, "name": "5", "x": 8.1, "y": 9.2, "z": 2.3, "malicious": false},
#     {"addr": 6, "leader": 0, "started": true, "joined": false, "type": true, "name": "6", "x": 7.1, "y": 7.2, "z": 7.3, "malicious": false},
#     {"addr": 7, "leader": 0, "started": true, "joined": false, "type": true, "name": "7", "x": 4.1, "y": 1.2, "z": 6.3, "malicious": false},
#     {"addr": 8, "leader": 0, "started": true, "joined": false, "type": true, "name": "8", "x": 12.1, "y": 0.2, "z": 4.3, "malicious": false},
#     {"addr": 9, "leader": 0, "started": true, "joined": false, "type": true, "name": "9", "x": 0.1, "y": 9.2, "z": 9.3, "malicious": false}
# ]}

# {"type": 4}

# {
# "type"  : 9,
# "stat"  : 0,
# "value" : 2.50
# }




'''绿色表示正常，红色表示异常或者，灰色表示未接入'''

# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
# import initExample  ## Add path to library (just for examples; you do not need this)

# import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
# import numpy as np
#
# win = pg.GraphicsLayoutWidget(show=True)
# win.setWindowTitle('pyqtgraph example: Scrolling Plots')
#
# # 1) Simplest approach -- update data in the array such that plot appears to scroll
# #    In these examples, the array size is fixed.
# # p1 = win.addPlot()
# p2 = win.addPlot()
# data1 = np.random.normal(size=300)
# # curve1 = p1.plot(data1)
# curve2 = p2.plot(data1)
# ptr1 = 0
#
#
# def update1():
#     global data1, ptr1
#     data1[:-1] = data1[1:]  # shift data in the array one sample left
#     # (see also: np.roll)
#     data1[-1] = np.random.normal()
#     # curve1.setData(data1)
#
#     ptr1 += 1
#     curve2.setData(data1)
#     curve2.setPos(ptr1, 0)
#
#
# # 2) Allow data to accumulate. In these examples, the array doubles in length
# #    whenever it is full.
# win.nextRow()
# # p3 = win.addPlot()
# p4 = win.addPlot()
# # Use automatic downsampling and clipping to reduce the drawing load
# # p3.setDownsampling(mode='peak')
# p4.setDownsampling(mode='peak')
# # p3.setClipToView(True)
# p4.setClipToView(True)
# # p3.setRange(xRange=[-100, 0])
# # p3.setLimits(xMax=0)
# # curve3 = p3.plot()
# curve4 = p4.plot()
#
# data3 = np.empty(100)
# ptr3 = 0
#
#
# def update2():
#     global data3, ptr3
#     data3[ptr3] = np.random.normal()
#     ptr3 += 1
#     if ptr3 >= data3.shape[0]:
#         tmp = data3
#         data3 = np.empty(data3.shape[0] * 2)
#         data3[:tmp.shape[0]] = tmp
#     # curve3.setData(data3[:ptr3])
#     # curve3.setPos(-ptr3, 0)
#     curve4.setData(data3[:ptr3])
#
#
# # 3) Plot in chunks, adding one new plot curve for every 100 samples
# chunkSize = 100
# # Remove chunks after we have 10
# maxChunks = 10
# startTime = pg.ptime.time()
# win.nextRow()
# p5 = win.addPlot(colspan=2)
# p5.setLabel('bottom', 'Time', 's')
# p5.setXRange(-10, 0)
# curves = []
# data5 = np.empty((chunkSize + 1, 2))
# ptr5 = 0
#
#
# def update3():
#     global p5, data5, ptr5, curves
#     now = pg.ptime.time()
#     for c in curves:
#         c.setPos(-(now - startTime), 0)
#
#     i = ptr5 % chunkSize
#     if i == 0:
#         curve = p5.plot()
#         curves.append(curve)
#         last = data5[-1]
#         data5 = np.empty((chunkSize + 1, 2))
#         data5[0] = last
#         while len(curves) > maxChunks:
#             c = curves.pop(0)
#             p5.removeItem(c)
#     else:
#         curve = curves[-1]
#     data5[i + 1, 0] = now - startTime
#     data5[i + 1, 1] = np.random.normal()
#     curve.setData(x=data5[:i + 2, 0], y=data5[:i + 2, 1])
#     ptr5 += 1
#
#
# # update all plots
# def update():
#     update1()
#     update2()
#     update3()
#
#
# timer = pg.QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(50)
#
# ## Start Qt event loop unless running in interactive mode or using pyside.
# if __name__ == '__main__':
#     QtGui.QApplication.instance().exec_()


# **********************************************************************
# import sys
# from PyQt5.QtWidgets import *
# from PyQt5 import uic, QtCore, QtGui
# import pyqtgraph.opengl as gl
# from PyQt5.QtCore import QTimer
# import numpy as np
#
# Uic_MainWindow = uic.loadUiType("ui_client/DisplayControl.ui")[0]
#
# class FatherUI(QMainWindow, Uic_MainWindow):
#     def __init__(self):
#         super(FatherUI, self).__init__()
#         self.setupUi(self)
#         self.childUI = childUI()
#         self.buttonNodeStatus.clicked.connect(self.childUI.ui_nodeStatus_handle)
#
# class childUI(QDialog):
#     def __init__(self):
#         super(childUI, self).__init__()
#
#     def update(self):
#         ## update volume colors
#         global phase, sp2  # , d2
#         # s = -np.cos(d2 * 2 + phase)
#         # color = np.empty((len(d2), 4), dtype=np.float32)
#         # color[:, 3] = np.clip(s * 0.1, 0, 1)
#         # color[:, 0] = np.clip(s * 3.0, 0, 1)
#         # color[:, 1] = np.clip(s * 1.0, 0, 1)
#         # color[:, 2] = np.clip(s ** 3, 0, 1)
#         # sp2.setData(color=color)
#         phase -= 0.1
#
#         ## update surface positions and colors
#         global sp3, d3, pos3
#         z = -np.cos(d3 * 2 + phase)
#         pos3[:, 2] = z
#         color = np.empty((len(d3), 4), dtype=np.float32)
#         color[:, 3] = 0.3
#         color[:, 0] = np.clip(z * 3.0, 0, 1)
#         color[:, 1] = np.clip(z * 1.0, 0, 1)
#         color[:, 2] = np.clip(z ** 3, 0, 1)
#         sp3.setData(pos=pos3, color=color)
#
#     def ui_nodeStatus_handle(self):
#         w = gl.GLViewWidget()
#         w.opts['distance'] = 20
#         w.show()
#         w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
#
#         g = gl.GLGridItem()
#         w.addItem(g)
#
#         pos = np.empty((53, 3))  # position
#         size = np.empty((53))
#         color = np.empty((53, 4))
#         pos[0] = (1, 0, 0)
#         size[0] = 0.5
#         color[0] = (1.0, 0.0, 0.0, 0.5)
#         pos[1] = (0, 1, 0)
#         size[1] = 0.2
#         color[1] = (0.0, 0.0, 1.0, 0.5)
#         pos[2] = (0, 0, 1)
#         color[2] = (0.0, 1.0, 0.0, 0.5)
#
#         z = 0.5
#         d = 6.0
#         for i in range(3, 53):
#             pos[i] = (0, 0, z)
#             size[i] = 2. / d
#             color[i] = (0.0, 1.0, 0.0, 0.5)
#             z *= 0.5
#             d *= 2.0
#
#         sp1 = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
#         sp1.translate(5, 5, 0)
#         w.addItem(sp1)
#
#         ##
#         ##  Second example shows a volume of points with rapidly updating color
#         ##  and pxMode=True
#         ##
#
#         # pos = np.random.random(size=(100000, 3))
#         # pos *= [10, -10, 10]
#         # pos[0] = (0, 0, 0)
#         # color = np.ones((pos.shape[0], 4))
#         # d2 = (pos ** 2).sum(axis=1) ** 0.5
#         # size = np.random.random(size=pos.shape[0]) * 10
#
#         pos = np.random.random(size=(5000, 3))
#         pos *= [10, -10, 10]
#         size = np.random.random(size=pos.shape[0]) * 10
#         sp2 = gl.GLScatterPlotItem(pos=pos, color=(1, 1, 1, 1), size=size)
#         phase = 0.
#
#         w.addItem(sp2)
#
#         ##
#         ##  Third example shows a grid of points with rapidly updating position
#         ##  and pxMode = False
#         ##
#
#         pos3 = np.zeros((100, 100, 3))
#         pos3[:, :, :2] = np.mgrid[:100, :100].transpose(1, 2, 0) * [-0.1, 0.1]
#         pos3 = pos3.reshape(10000, 3)
#         d3 = (pos3 ** 2).sum(axis=1) ** 0.5
#
#         sp3 = gl.GLScatterPlotItem(pos=pos3, color=(1, 1, 1, .3), size=0.1, pxMode=False)
#
#         w.addItem(sp3)
#
#         t = QtCore.QTimer()
#         t.timeout.connect(self.update)
#         t.start(50)
#
#
# if __name__ == '__main__':
#     appf = QApplication(sys.argv)
#     father = FatherUI()
#     father.show()
#     sys.exit(appf.exec_())
