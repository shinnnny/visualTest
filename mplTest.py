# -*-coding:utf-8 -*-

"""
# File       : mplTest.py
# Time       : 10/14/2021 7:24 PM
# Update     : 10/14/2021 7:24 PM
# Author     : Liang Zeting
# E-Mail     : m404_error_collapsed@outlook.com
# Description: 
"""

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.animation as an
import scipy.stats
import numpy as np
import matplotlib
import celluloid
import os

plt.rcParams['animation.ffmpeg_path'] = 'C:\\trans\\Software\\ffmpeg\\bin\\ffmpeg.exe'

matplotlib.use("TkAgg")

outputDir = os.path.join(os.getcwd(), "output")
picName = "test.png"
gifName = "test.gif"
htmlName = "test.html"
SAVE = False
NB_SIZE = 20
NB_GRID_SIZE = 8
RAN_STATE = 42
MEAN = 0
COV = 1
FRAMES = 10000
INTERVAL = 45
CMAP = 'coolwarm'
PLOT = 'surface'

fig: plt.Figure = plt.figure()
ax: Axes3D = fig.add_subplot(projection='3d')
ax.autoscale_view()
plt.axis('off')
# camera = celluloid.Camera(figure=fig)

np.random.seed(RAN_STATE)
l = np.linspace(-NB_GRID_SIZE, NB_GRID_SIZE, NB_SIZE)
x, y = np.meshgrid(l, l)
pos = np.dstack((x, y))
# z0 = np.zeros(x.shape)
distuv = scipy.stats.multivariate_normal(mean=[MEAN] * 2, cov=np.diag([COV] * 2))
z0 = distuv.pdf(pos)

# ax.quiver(x, y, z0, x, y, z, arrow_length_ratio=10e-5, normalize=True, cmap=cm.coolwarm,alpha=0.7)
if PLOT == 'wire':
    ax.plot_wireframe(x, y, z0, cmap=CMAP, alpha=0.7)
elif PLOT == 'surface':
    ax.plot_surface(x, y, z0, alpha=0.7, cmap=CMAP)
else:
    exit("PLOT form unmatched.")

# TODO: 1. 以每质数帧为分割，对区间内z坐标进行线性插值
# TODO: 2. 固定xy的meshgrid，以固定数量的区域在时变二维正态分布的曲面上进行时变滑动，在这些区域内以和meshgrid相同的数量进行采样，端点z的颜色由曲面热力图决定
z_terminals = [z0]
for i in range(((FRAMES - 1) // INTERVAL) + 1):
    # Normal 1
    distuv.mean = (np.random.random((1, 2)) - 0.5) * NB_GRID_SIZE
    distuv.cov = np.random.random((2, 2))
    temp = distuv.pdf(pos)
    # Laplace 2
    # distuv.mean = np.random.laplace(loc=(np.random.random((1, 2)) * 2 - 1) * NB_GRID_SIZE,
    #                                 scale=np.random.random((1, 2)),
    #                                 size=(1, 2))
    # distuv.cov = np.random.laplace(loc=np.random.random((1, 2)), scale=np.random.random((1, 2)),
    #                                size=(2, 2))
    # Normal 2
    distuv.mean = (np.random.random((1, 2)) - 0.5) * NB_GRID_SIZE
    distuv.cov = np.random.random((2, 2)) * NB_GRID_SIZE ** 2
    z_terminals.append(distuv.pdf(pos) - temp)

z_vals = []
for zt_idx, zt_vals in enumerate(z_terminals):
    if zt_idx == 0:
        z_vals.append(zt_vals)
        continue
    last = z_terminals[zt_idx - 1]
    if zt_idx != len(z_terminals) - 1:
        for i in range(1, INTERVAL):
            z_vals.append(last + (zt_vals - last) / INTERVAL * i)
        z_vals.append(zt_vals)
    else:
        for i in range(1, (FRAMES - 1) % INTERVAL):
            z_vals.append(last + (zt_vals - last) / ((FRAMES - 1) % INTERVAL) * i)
        z_vals.append(zt_vals)


def update_func(num):
    ax.clear()
    plt.axis('off')
    if PLOT == 'wire':
        ax.plot_wireframe(x, y, z_vals[num], alpha=0.7, cmap=CMAP)
    elif PLOT == 'surface':
        ax.plot_surface(x, y, z_vals[num], alpha=0.7, cmap=CMAP)

    ax.view_init(np.max(z_vals[num]) * 5, num)
    # camera.snap()


ani = an.FuncAnimation(fig, update_func, FRAMES, interval=25, blit=False, repeat=False)

plt.show()
plt.close(fig=fig)  # FIXME: 未能正确关闭
if SAVE:
    ani.save(os.path.join(outputDir, gifName))
    with open(os.path.join(outputDir, htmlName), "w") as html_file:
        print(ani.to_html5_video(), file=html_file)
    # fig.savefig(os.path.join(outputDir, picName))
    # animation = camera.animate()
    # animation.save(os.path.join(outputDir, gifName))
