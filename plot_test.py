# # **********************************************************************
# CrossHair，借鉴显示鼠标所在x值处的线的y值
"""
Demonstrates some customized mouse interaction by drawing a crosshair that follows
the mouse.
"""

# import initExample ## Add path to library (just for examples; you do not need this)
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point

#generate layout
app = QtGui.QApplication([])  # 初始化app
win = pg.GraphicsLayoutWidget(show=True)  # 设置widget，并属性show为True，即显示
win.setWindowTitle('pyqtgraph example: crosshair')  # 设置窗口名称
label = pg.LabelItem(justify='right')  # 设置label用于跟随鼠标显示横纵坐标有效值
win.addItem(label)  # 定义了label之后，要addItem之后才会真正加进去
p1 = win.addPlot(row=1, col=0)  # p1为p2的区域放大，并显示鼠标所在位置值
p2 = win.addPlot(row=2, col=0)  # p2为全部数据画出的折线致密的原图

# 定义区域
region = pg.LinearRegionItem()
region.setZValue(10)  # 不过这一句话好像没什么作用
# Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
# item when doing auto-range calculations.
p2.addItem(region, ignoreBounds=True)

#pg.dbg()
p1.setAutoVisible(y=True)


#create numpy arrays
#make the numbers large to show that the xrange shows data from 10000 to all the way 0
data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)

# 画图
p1.plot(data1, pen="r")
p1.plot(data2, pen="g")

p2.plot(data1, pen="w")

# 设置图2中放大区域被移动后的触发函数
def update():
    region.setZValue(10)
    minX, maxX = region.getRegion()  # 调整p1的横轴显示区域坐标范围
    p1.setXRange(minX, maxX, padding=0)

region.sigRegionChanged.connect(update)

def updateRegion(window, viewRange):
    rgn = viewRange[0]
    region.setRegion(rgn)

p1.sigRangeChanged.connect(updateRegion)

# 初始的region位置
region.setRegion([1000, 2000])

# 设置跟随鼠标移动的线
#cross hair
vLine = pg.InfiniteLine(angle=90, movable=False)  # angle控制线相对x轴正向的相对夹角
hLine = pg.InfiniteLine(angle=0, movable=False)
p1.addItem(vLine, ignoreBounds=True)
p1.addItem(hLine, ignoreBounds=True)


vb = p1.vb

# 跟随鼠标移动，提取鼠标的横轴值，并自定义纵轴的值显示
def mouseMoved(evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if p1.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        # 建议不用int，精度高时用float，这样可以显示横坐标的小数
        index = int(mousePoint.x())
        if index > 0 and index < len(data1):
            label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())



# 设置鼠标移动的触发，限制速率，移动则触发mouseMoved函数
proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
#p1.scene().sigMouseMoved.connect(mouseMoved_1)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


# # **********************************************************************
# # Basic plotting
# # 采纳Parametric，grid enabled和Multiple curves的红色线条
# # -*- coding: utf-8 -*-
# """
# This example demonstrates many of the 2D plotting capabilities
# in pyqtgraph. All of the plots may be panned/scaled by dragging with
# the left/right mouse buttons. Right click on any plot to show a context menu.
# """
#
# # import initExample ## Add path to library (just for examples; you do not need this)
#
#
# from pyqtgraph.Qt import QtGui, QtCore
# import numpy as np
# import pyqtgraph as pg
#
# #QtGui.QApplication.setGraphicsSystem('raster')
# app = QtGui.QApplication([])
# #mw = QtGui.QMainWindow()
# #mw.resize(800,800)
#
# win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
# win.resize(1000,600)
# win.setWindowTitle('pyqtgraph example: Plotting')
#
# # Enable antialiasing for prettier plots
# pg.setConfigOptions(antialias=True)
#
# p1 = win.addPlot(title="Basic array plotting", y=np.random.normal(size=100))
#
# p2 = win.addPlot(title="Multiple curves")
# p2.plot(np.random.normal(size=100), pen=(255,0,0), name="Red curve")
# p2.plot(np.random.normal(size=110)+5, pen=(0,255,0), name="Green curve")
# p2.plot(np.random.normal(size=120)+10, pen=(0,0,255), name="Blue curve")
#
# p3 = win.addPlot(title="Drawing with points")
# p3.plot(np.random.normal(size=100), pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
#
#
# win.nextRow()
#
# p4 = win.addPlot(title="Parametric, grid enabled")
# x = np.cos(np.linspace(0, 2*np.pi, 1000))
# y = np.sin(np.linspace(0, 4*np.pi, 1000))
# p4.plot(x, y)
# p4.showGrid(x=True, y=True)
#
# p5 = win.addPlot(title="Scatter plot, axis labels, log scale")
# x = np.random.normal(size=1000) * 1e-5
# y = x*1000 + 0.005 * np.random.normal(size=1000)
# y -= y.min()-1.0
# mask = x > 1e-15
# x = x[mask]
# y = y[mask]
# p5.plot(x, y, pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(100, 100, 255, 50))
# p5.setLabel('left', "Y Axis", units='A')
# p5.setLabel('bottom', "Y Axis", units='s')
# p5.setLogMode(x=True, y=False)
#
# p6 = win.addPlot(title="Updating plot")
# curve = p6.plot(pen='y')
# data = np.random.normal(size=(10,1000))
# ptr = 0
# def update():
#     global curve, data, ptr, p6
#     curve.setData(data[ptr%10])
#     if ptr == 0:
#         p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
#     ptr += 1
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(50)
#
#
# win.nextRow()
#
# p7 = win.addPlot(title="Filled plot, axis disabled")
# y = np.sin(np.linspace(0, 10, 1000)) + np.random.normal(size=1000, scale=0.1)
# p7.plot(y, fillLevel=-0.3, brush=(50,50,200,100))
# p7.showAxis('bottom', False)
#
#
# x2 = np.linspace(-100, 100, 1000)
# data2 = np.sin(x2) / x2
# p8 = win.addPlot(title="Region Selection")
# p8.plot(data2, pen=(255,255,255,200))
# lr = pg.LinearRegionItem([400,700])
# lr.setZValue(-10)
# p8.addItem(lr)
#
# p9 = win.addPlot(title="Zoom on selected region")
# p9.plot(data2)
# def updatePlot():
#     p9.setXRange(*lr.getRegion(), padding=0)
# def updateRegion():
#     lr.setRegion(p9.getViewBox().viewRange()[0])
# lr.sigRegionChanged.connect(updatePlot)
# p9.sigXRangeChanged.connect(updateRegion)
# updatePlot()
#
# ## Start Qt event loop unless running in interactive mode or using pyside.
# if __name__ == '__main__':
#     import sys
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()



# # **********************************************************************
# # LegendItem
# """
# Demonstrates basic use of LegendItem
# """
# # import initExample ## Add path to library (just for examples; you do not need this)
#
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
# import numpy as np
#
# win = pg.plot()
# win.setWindowTitle('pyqtgraph example: BarGraphItem')
#
# # # option1: only for .plot(), following c1,c2 for example-----------------------
# # win.addLegend(frame=False, rowCount=1, colCount=2)
#
# # bar graph
# x = np.arange(10)
# y = np.sin(x+2) * 3
# bg1 = pg.BarGraphItem(x=x, height=y, width=0.3, brush='b', pen='w', name='bar')
# win.addItem(bg1)
#
# # curve
# c1 = win.plot([np.random.randint(0,8) for i in range(10)], pen='r', symbol='t', symbolPen='r', symbolBrush='g', name='curve1')
# c2 = win.plot([2,1,4,3,1,3,2,4,3,2], pen='g', fillLevel=0, fillBrush=(255,255,255,30), name='curve2')
#
# # scatter plot
# s1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120), name='scatter')
# spots = [{'pos': [i, np.random.randint(-3, 3)], 'data': 1} for i in range(10)]
# s1.addPoints(spots)
# win.addItem(s1)
#
# # # option2: generic method------------------------------------------------
# legend = pg.LegendItem((80,60), offset=(70,20))
# legend.setParentItem(win.graphicsItem())
# legend.addItem(bg1, 'bar')
# legend.addItem(c1, 'curve1')
# legend.addItem(c2, 'curve2')
# legend.addItem(s1, 'scatter')
#
#
# ## Start Qt event loop unless running in interactive mode or using pyside.
# if __name__ == '__main__':
#     import sys
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()

# # **********************************************************************
# # 在3D部件上放2D部件做图例legend
# # import initExample
# import pyqtgraph as pg
# import pyqtgraph.opengl as gl
# import numpy as np
# from pyqtgraph.Qt import QtGui
#
# pg.mkQApp()
#
# w = pg.LayoutWidget()
#
#
# class GraphicsView(pg.GraphicsView):
#     """
#     GraphicsView subclass that uses GLViewWidget as its canvas.
#     This allows 2D graphics to be overlaid on a 3D background.
#     """
#
#     def __init__(self):
#         self.glView = gl.GLViewWidget()
#         pg.GraphicsView.__init__(self, background=None)
#         self.setStyleSheet("background: transparent")
#         self.setViewport(self.glView)
#
#     def paintEvent(self, event):
#         """
#         Distribute paint events to both widgets
#         """
#         self.glView.paintEvent(event)
#         return pg.GraphicsView.paintEvent(self, event)
#
#     def mousePressEvent(self, event):
#         """
#         Distribute mouse events to both widgets
#         """
#         pg.GraphicsView.mousePressEvent(self, event)
#         self.glView.mousePressEvent(event)
#
#     def mouseMoveEvent(self, event):
#         """
#         Distribute mouse events to both widgets
#         """
#         pg.GraphicsView.mouseMoveEvent(self, event)
#         self.glView.mouseMoveEvent(event)
#
#     def mouseReleaseEvent(self, event):
#         """
#         Distribute mouse events to both widgets
#         """
#         pg.GraphicsView.mouseReleaseEvent(self, event)
#         self.glView.mouseReleaseEvent(event)
#
#
# view = GraphicsView()
# glView = view.glView
# w.addWidget(glView)
# w.resize(800, 800)
# w.show()
#
# ## Compute surface vertex data
# cols = 90
# rows = 100
# x = np.linspace(-8, 8, cols + 1).reshape(cols + 1, 1)
# y = np.linspace(-8, 8, rows + 1).reshape(1, rows + 1)
# d = (x ** 2 + y ** 2) * 0.1
# d2 = d ** 0.5 + 0.1
# z = np.sin(d + 0.5) / d2
#
# # Assign color based on height
# cm = pg.ColorMap([0, 0.5, 1],
#                  [(1., 0., 0., 1.),
#                   (0., 0., 1., 1.),
#                   (0., 1., 0., 1.)])
# colors = cm.map((z + z.min()) / (z.max() - z.min()), mode='float')
#
# plot = gl.GLSurfacePlotItem(x=x[:, 0], y=y[0, :], z=z, shader='shaded', smooth=True, colors=colors)
# glView.addItem(plot)
#
# # Make a 2D color bar using the same ColorMap
# colorBar = pg.GradientLegend(size=(50, 200), offset=(15, -25))
# colorBar.setGradient(cm.getGradient())
# labels = dict([("%0.2f" % (v * (z.max() - z.min()) + z.min()), v) for v in np.linspace(0, 1, 4)])
# colorBar.setLabels(labels)
# view.addItem(colorBar)
#
#
# if __name__ == '__main__':
#     import sys
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()
# # **********************************************************************
# # 添加坐标轴
# import sys
# import numpy as np
# import pyqtgraph.opengl as gl
# from pyqtgraph.Qt import QtWidgets
# from pyqtgraph import Vector
#
#
# class plot3D(object):
#     def __init__(self):
#         self.line_input = 0
#         self.app = QtWidgets.QApplication(sys.argv)
#         self.w = gl.GLViewWidget()
#         axis = gl.GLAxisItem()
#         self.w.addItem(axis)
#
#     def plot_line(self):
#         pl_line = np.array([(338.12, 508.03, 0.0), (338.12, 0.0, 0.0)])
#         color = (250, 0, 0, 0.7)
#         newline = gl.GLLinePlotItem(pos=pl_line, color=color, width=2, antialias=False)
#         self.w.addItem(newline)
#         self.w.show()
#
#     def exec(self):
#         self.app.exec()
#
#
# pl3d = plot3D()
# pl3d.plot_line()
# pl3d.exec()


# # **********************************************************************
# # 给GLViewWidget图像加坐标轴
# # https://stackoverflow.com/questions/56890547/how-to-add-axis-features-labels-ticks-values-to-a-3d-plot-with-glviewwidget
# from pyqtgraph.Qt import QtCore, QtGui
# import pyqtgraph.opengl as gl
# import pyqtgraph as pg
# import OpenGL.GL as ogl
# import numpy as np
#
# class CustomTextItem(gl.GLGraphicsItem.GLGraphicsItem):
#     def __init__(self, X, Y, Z, text):
#         gl.GLGraphicsItem.GLGraphicsItem.__init__(self)
#         self.text = text
#         self.X = X
#         self.Y = Y
#         self.Z = Z
#
#     def setGLViewWidget(self, GLViewWidget):
#         self.GLViewWidget = GLViewWidget
#
#     def setText(self, text):
#         self.text = text
#         self.update()
#
#     def setX(self, X):
#         self.X = X
#         self.update()
#
#     def setY(self, Y):
#         self.Y = Y
#         self.update()
#
#     def setZ(self, Z):
#         self.Z = Z
#         self.update()
#
#     def paint(self):
#         self.GLViewWidget.qglColor(QtCore.Qt.black)
#         self.GLViewWidget.renderText(self.X, self.Y, self.Z, self.text)
#
#
# class Custom3DAxis(gl.GLAxisItem):
#     """Class defined to extend 'gl.GLAxisItem'."""
#     def __init__(self, parent, color=(0,0,0,.6)):
#         gl.GLAxisItem.__init__(self)
#         self.parent = parent
#         self.c = color
#
#     def add_labels(self):
#         """Adds axes labels."""
#         x,y,z = self.size()
#         #X label
#         self.xLabel = CustomTextItem(X=x/2, Y=-y/20, Z=-z/20, text="X")
#         self.xLabel.setGLViewWidget(self.parent)
#         self.parent.addItem(self.xLabel)
#         #Y label
#         self.yLabel = CustomTextItem(X=-x/20, Y=y/2, Z=-z/20, text="Y")
#         self.yLabel.setGLViewWidget(self.parent)
#         self.parent.addItem(self.yLabel)
#         #Z label
#         self.zLabel = CustomTextItem(X=-x/20, Y=-y/20, Z=z/2, text="Z")
#         self.zLabel.setGLViewWidget(self.parent)
#         self.parent.addItem(self.zLabel)
#
#     def add_tick_values(self, xticks=[], yticks=[], zticks=[]):
#         """Adds ticks values."""
#         x,y,z = self.size()
#         xtpos = np.linspace(0, x, len(xticks))
#         ytpos = np.linspace(0, y, len(yticks))
#         ztpos = np.linspace(0, z, len(zticks))
#         #X label
#         for i, xt in enumerate(xticks):
#             val = CustomTextItem(X=xtpos[i], Y=-y/20, Z=-z/20, text=str(xt))
#             val.setGLViewWidget(self.parent)
#             self.parent.addItem(val)
#         #Y label
#         for i, yt in enumerate(yticks):
#             val = CustomTextItem(X=-x/20, Y=ytpos[i], Z=-z/20, text=str(yt))
#             val.setGLViewWidget(self.parent)
#             self.parent.addItem(val)
#         #Z label
#         for i, zt in enumerate(zticks):
#             val = CustomTextItem(X=-x/20, Y=-y/20, Z=ztpos[i], text=str(zt))
#             val.setGLViewWidget(self.parent)
#             self.parent.addItem(val)
#
#     def paint(self):
#         self.setupGLState()
#         if self.antialias:
#             ogl.glEnable(ogl.GL_LINE_SMOOTH)
#             ogl.glHint(ogl.GL_LINE_SMOOTH_HINT, ogl.GL_NICEST)
#         ogl.glBegin(ogl.GL_LINES)
#
#         x,y,z = self.size()
#         #Draw Z
#         ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
#         ogl.glVertex3f(0, 0, 0)
#         ogl.glVertex3f(0, 0, z)
#         #Draw Y
#         ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
#         ogl.glVertex3f(0, 0, 0)
#         ogl.glVertex3f(0, y, 0)
#         #Draw X
#         ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
#         ogl.glVertex3f(0, 0, 0)
#         ogl.glVertex3f(x, 0, 0)
#         ogl.glEnd()
#
#
# app = QtGui.QApplication([])
# fig1 = gl.GLViewWidget()
# background_color = app.palette().color(QtGui.QPalette.Background)
# fig1.setBackgroundColor(background_color)
#
# n = 51
# y = np.linspace(-10,10,n)
# x = np.linspace(-10,10,100)
# for i in range(n):
#     yi = np.array([y[i]]*100)
#     d = (x**2 + yi**2)**0.5
#     z = 10 * np.cos(d) / (d+1)
#     pts = np.vstack([x,yi,z]).transpose()
#     plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
#     fig1.addItem(plt)
#
#
# axis = Custom3DAxis(fig1, color=(0.2,0.2,0.2,.6))
# axis.setSize(x=12, y=12, z=12)
# # Add axes labels
# axis.add_labels()
# # Add axes tick values
# axis.add_tick_values(xticks=[0,4,8,12], yticks=[0,6,12], zticks=[0,3,6,9,12])
# fig1.addItem(axis)
# fig1.opts['distance'] = 40
#
# fig1.show()
#
# if __name__ == '__main__':
#     import sys
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()



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
