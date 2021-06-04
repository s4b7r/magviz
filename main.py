from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from magfield import BerechneFeld



_drag_data = {"x": 0, "y": 0, "item": None}

# Drag logic from https://stackoverflow.com/questions/6740855/board-drawing-code-to-move-an-oval/6789351#6789351

def find_closest_dot(event_x, dots_xs):
    closest_diff = np.inf
    closest_dot = None
    for dot, dot_x in enumerate(dots_xs):
        xdiff = abs(dot_x - event_x)
        if xdiff < closest_diff:
            closest_diff = xdiff
            closest_dot = dot
    return closest_dot


def drag_start(event):
    """Begining drag of an object"""
    if event.inaxes == coilplot:
        # record the item and its location
        _drag_data["item"] = find_closest_dot(event.xdata, dots_xs)
        _drag_data["x"] = event.xdata
        _drag_data["y"] = event.ydata


def drag_stop(event):
    """End drag of an object"""
    # reset the drag information
    _drag_data["item"] = None
    _drag_data["x"] = 0
    _drag_data["y"] = 0


def drag(event):
    """Handle dragging of an object"""
    if _drag_data['item'] is not None and event.inaxes == coilplot:
        # compute how much the mouse has moved
        delta_x = event.xdata - _drag_data["x"]
        # move the object the appropriate amount
        dots_xs[_drag_data['item']] += delta_x
        update_plot()
        # record the new position
        _drag_data["x"] = event.xdata
        _drag_data["y"] = event.ydata


root = Tk()
root.bind('<Escape>', quit)

YLIMSTART = -.25
YLIMEND = -YLIMSTART
YLIMS = YLIMSTART, YLIMEND
XLIMSTART = -.25
XLIMEND = -XLIMSTART
XLIMS = XLIMSTART, XLIMEND
ZSTART = 0
ZEND = 1e-2
ZLIMS = ZSTART, ZEND
NUM_ZS = 5
ZPLANE = 8e-3

MAGPLOT_YSTART = -3e-5
MAGPLOT_YEND = -MAGPLOT_YSTART

fig = Figure(figsize=(5, 4), dpi=100)
axes = fig.subplots(nrows=4, ncols=2, sharex='col', sharey=False,
                    gridspec_kw={'height_ratios': [5, 1, 1, 1]})
magplot = axes[0, 0]
dirplot = axes[1, 0]
vecplot = axes[2, 0]
coilplot = axes[3, 0]

magplot_centered = axes[0, 1]
dirplot_centered = axes[1, 1]
vecplot_centered = axes[2, 1]
coilplot_centered = axes[3, 1]

# for ax in axes.flat:
#     ax.autoscale(False)

# matplotlib in tkinter from https://ishantheperson.github.io/posts/tkinter-matplotlib/

plt_canvas = FigureCanvasTkAgg(fig, root)
plt_canvas.get_tk_widget().pack(side="top",fill='both',expand=True)

dots_xs = [
        -.1,
        .1
        ]
DOT_Y = 0


NUM_YS = 100
LEITER_RESOLUTION = 100


def update_plot():
    dots_center = (dots_xs[1] - dots_xs[0]) / 2 + dots_xs[0]
    CENTERVIEW_WIDTH = .1
    centerview_start = dots_center - CENTERVIEW_WIDTH / 2
    centerview_end = centerview_start + CENTERVIEW_WIDTH
    centerview = (centerview_start, centerview_end)

    replot_dots(dots_xs, centerview)
    replot_mag(centerview)
    plt_canvas.draw()


def replot_vec(Bd, centerview):
    ys = np.linspace(*centerview, num=NUM_YS)
    for plot in [vecplot, vecplot_centered]:
        plot.clear()
        plot.quiver(ys, np.zeros(shape=ys.shape), Bd[0, :, 1], Bd[0, :, 2], color=(Bd[0, :]+1)*.5, headwidth=1.5, headlength=2, headaxislength=2)

    vecplot.set_xlim(YLIMS)
    vecplot_centered.set_xlim(centerview)


def replot_dir(Bv_tot, centerview):
    def get_field_dir(field_vec):
        field_dir = field_vec / np.expand_dims(np.linalg.norm(field_vec, ord=2, axis=2), axis=2)
        return field_dir

    Bd = get_field_dir(Bv_tot)
    colors = (Bd[0, :]+1)*.5
    ys = np.linspace(*centerview, num=NUM_YS)
    for plot in [dirplot, dirplot_centered]:
        plot.clear()
        plot.scatter(ys, np.zeros(shape=ys.shape), s=500, c=colors, marker='o', antialiased=False, edgecolors='')

    dirplot.set_xlim(YLIMS)
    dirplot_centered.set_xlim(centerview)

    replot_vec(Bd, centerview)

    return colors


def replot_mag(centerview):
    for plot in [magplot, magplot_centered]:
        plot.clear()

    ys = np.linspace(*centerview, num=NUM_YS)
    zs = np.linspace(*ZLIMS, NUM_ZS)
    zidx_zplane = np.argmin(np.abs(zs - ZPLANE))
    # print(f'z = {zs[zidx_zplane]}')
    Bv_tot = np.zeros(shape=(1, len(ys), len(zs), 3))
    for dotx in dots_xs:
        Leiter = [[x, dotx, 0] for x in np.linspace(start=XLIMSTART, stop=XLIMEND, num=LEITER_RESOLUTION)]
        Bx, By, Bz, _ = BerechneFeld(Leiter, Strom=1, xs=(0,), ys=ys, zs=zs)
        Bv = np.concatenate((np.expand_dims(Bx, Bx.ndim), np.expand_dims(By, By.ndim), np.expand_dims(Bz, Bz.ndim)), axis=3)

        # for plot in [magplot, magplot_centered]:
        #     plot.quiver(ys, zs, Bv[:, :, 1], Bv[:, :, 2])

        Bv_tot += Bv

    magplot.set_xlim(YLIMS)
    magplot_centered.set_xlim(centerview)

    colors = replot_dir(Bv_tot[:, :, zidx_zplane, :], centerview)
    
    ysmesh, zsmesh = np.meshgrid(ys, zs)
    for plot in [magplot, magplot_centered]:
        plot.quiver(ysmesh, zsmesh, Bv_tot[0, :, :, 1].T, Bv_tot[0, :, :, 2].T, color=colors)
        plot.plot(XLIMS, [zs[zidx_zplane]] * 2, c='r', linestyle=':')
        # plot.set_ylim(MAGPLOT_YSTART, MAGPLOT_YEND)


def replot_dots(dots_xs, centerview):
    for plot in [coilplot, coilplot_centered]:
        plot.clear()
        for dot_x in dots_xs:
            plot.plot(dot_x, DOT_Y, color='red', marker='o', linestyle='')
    coilplot.set_xlim(YLIMS)
    coilplot_centered.set_xlim(centerview)


update_plot()

fig.canvas.callbacks.connect('button_press_event', drag_start)
fig.canvas.callbacks.connect('button_release_event', drag_stop)
fig.canvas.callbacks.connect('motion_notify_event', drag)

root.mainloop()
