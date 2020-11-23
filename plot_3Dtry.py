# -*- coding: utf-8 -*-
"""
Demonstrates use of GLScatterPlotItem with rapidly-updating plots.
"""

# import initExample

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import time

app = QtGui.QApplication([])
w = gl.GLViewWidget()  # 定义窗口w为GLViewWidget部件
w.opts['distance'] = 20  # 初始视角高度
w.show()  # 显示窗口
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')  # 定义窗口标题

# g用来显示白色网格
g = gl.GLGridItem()
w.addItem(g)
# 注：网格的大小可以设置：
# g = gl.GLGridItem()
# size_axes = distance * 3
# g.setSize(x=size_axes, y=size_axes, z=size_axes)
# w.addItem(g)

# **************************************************************************************
#  一、例子：点集
#  First example is a set of points with pxMode=False
#  These demonstrate the ability to have points with real size down to a very small scale
#
pos = np.empty((53, 3))  # 存放点的位置，为53 * 3的向量，感觉说是矩阵更合适
size = np.empty((53))  # 存放点的大小
color = np.empty((53, 4))  # 存放点的颜色
pos[0] = (1, 0, 0)  # 第一个点的坐标
size[0] = 0.5  # 第一个点的大小
color[0] = (1.0, 0.0, 0.0, 1)  # 红色，最后一位为透明度
pos[1] = (0, 1, 0)
size[1] = 0.5
color[1] = (0.0, 0.0, 1.0, 1)  # 蓝色
pos[2] = (0, 0, 1)
size[2] = 1
color[2] = (0.0, 1.0, 0.0, 1)  # 绿色
pos[3] = (2, 0, 0)
size[3] = 0.5
color[3] = (1.0, 1.0, 0.0, 1)  # 黄色
pos[4] = (3, 0, 0)
size[4] = 0.5
color[4] = (1.0, 0.0, 1.0, 1)  # 紫红色
pos[5] = (4, 0, 0)
size[5] = 0.5
color[5] = (0.0, 1.0, 1.0, 1)  # 天蓝色
pos[6] = (5, 0, 0)
size[6] = 0.5
color[6] = (1.0, 1.0, 1.0, 1)  # 白色


z = 0.5
d = 6.0
# 对pos从第3个元素开始操作，生成最后一直往上叠的小绿点
for i in range(7, 53):
    pos[i] = (0, 0, z)
    size[i] = 2. / d
    color[i] = (0.0, 1.0, 0.0, 0.5)  # 绿色，第4个0为透明
    z *= 0.5
    d *= 2.0

sp1 = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)  # 设置Item
sp1.translate(5, 5, 0)  # 平移sp1，即横轴坐标整体+5，纵轴坐标整体+5
w.addItem(sp1)  # 当w使用addItem()后，才会生效显示图像

# **************************************************************************************
#  二、立方体区域点集，并迅速更新颜色
#  Second example shows a volume of points with rapidly updating color
#  and pxMode=True
#

pos2 = np.random.random(size=(100000, 3))  # 生成随机数点集
pos2 *= [10, -10, 10]  # 区域的长宽高都为10，于第四卦限
pos2[0] = (0, 0, 0)  # 第一个点为原点
color2 = np.ones((pos2.shape[0], 4))  # pos2的行数（点数），4列的元素全为1的向量
d2 = (pos2 ** 2).sum(axis=1) ** 0.5
size = np.random.random(size=pos2.shape[0]) * 10  # 点的大小
sp2 = gl.GLScatterPlotItem(pos=pos2, color=(1, 1, 1, 1), size=size)  # (1, 1, 1, 1)为白色
phase = 0.

w.addItem(sp2)

# **************************************************************************************
#  三、点网格
#  Third example shows a grid of points with rapidly updating position
#  and pxMode = False
#

pos3 = np.zeros((100, 100, 3))
pos3[:, :, :2] = np.mgrid[:100, :100].transpose(1, 2, 0) * [-0.1, 0.1]
pos3 = pos3.reshape(10000, 3)  # 经过上述操作得到10000行3列的ndarray，初始点铺平在平面的四分之一范围上
d3 = (pos3 ** 2).sum(axis=1) ** 0.5

sp3 = gl.GLScatterPlotItem(pos=pos3, color=(1, 1, 1, .3), size=0.1, pxMode=False)

w.addItem(sp3)


def update():
    """
    更新
    - 每次运行update都事phase减0.1，从而更新color2，和pos3的点的位置与color
    :return:
    """
    # update volume colors
    global phase, sp2, d2
    s = -np.cos(d2 * 2 + phase)
    color2 = np.empty((len(d2), 4), dtype=np.float32)
    color2[:, 3] = np.clip(s * 0.1, 0, 1)
    color2[:, 0] = np.clip(s * 3.0, 0, 1)
    color2[:, 1] = np.clip(s * 1.0, 0, 1)
    color2[:, 2] = np.clip(s ** 3, 0, 1)
    sp2.setData(color=color2)

    # start = time.process_time()
    phase -= 0.1
    # update surface positions and colors
    global sp3, d3, pos3
    # 每次运行更新pos3的点的位置
    z = -np.cos(d3 * 2 + phase)
    pos3[:, 2] = z
    color = np.empty((len(d3), 4), dtype=np.float32)
    color[:, 3] = 0.3
    color[:, 0] = np.clip(z * 3.0, 0, 1)
    color[:, 1] = np.clip(z * 1.0, 0, 1)
    color[:, 2] = np.clip(z ** 3, 0, 1)
    sp3.setData(pos=pos3, color=color)
    # end = time.process_time()
    # print('Time spent on update sp3 is: %.5f' % (end - start))

# 定时触发，每50ms运行一次update函数更新
t = QtCore.QTimer()
t.timeout.connect(update)
t.start(50)


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
