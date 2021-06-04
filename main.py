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

LIMSTART = -.25
LIMEND = -LIMSTART

MAGPLOT_YSTART = -3e-5
MAGPLOT_YEND = -MAGPLOT_YSTART

fig = Figure(figsize=(5, 4), dpi=100)
axes = fig.subplots(nrows=4, ncols=2, sharex='col', sharey=False,
                    gridspec_kw={'height_ratios': [5, 1, 1, 1]})
magplot = axes[0, 0]
magplot.set_ylim(MAGPLOT_YSTART, MAGPLOT_YEND)
dirplot = axes[1, 0]
vecplot = axes[2, 0]
coilplot = axes[3, 0]
coilplot.set_xlim(LIMSTART, LIMEND)

magplot_centered = axes[0, 1]
magplot.set_ylim(MAGPLOT_YSTART, MAGPLOT_YEND)
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
    replot_dots(dots_xs)
    replot_mag()
    plt_canvas.draw()


def replot_vec(Bd):
    ys = np.linspace(start=LIMSTART, stop=LIMEND, num=NUM_YS)
    for plot in [vecplot, vecplot_centered]:
        plot.clear()
        plot.quiver(ys, np.zeros(shape=ys.shape), Bd[0, :, 1], Bd[0, :, 2], color=(Bd[0, :]+1)*.5, headwidth=1.5, headlength=2, headaxislength=2)

    vecplot_centered.set_xlim(dots_xs[0], dots_xs[1])


def replot_dir(Bv_tot):
    def get_field_dir(field_vec):
        field_dir = field_vec / np.expand_dims(np.linalg.norm(field_vec, ord=2, axis=2), axis=2)
        return field_dir

    Bd = get_field_dir(Bv_tot)
    ys = np.linspace(start=LIMSTART, stop=LIMEND, num=NUM_YS)
    for plot in [dirplot, dirplot_centered]:
        plot.clear()
        plot.scatter(ys, np.zeros(shape=ys.shape), s=500, c=(Bd[0, :]+1)*.5, marker='o', antialiased=False, edgecolors='')

    dirplot_centered.set_xlim(dots_xs[0], dots_xs[1])

    replot_vec(Bd)


def replot_mag():
    for plot in [magplot, magplot_centered]:
        plot.clear()

    Bv_tot = np.zeros(shape=(1, NUM_YS, 3))
    for dotx in dots_xs:
        ys = np.linspace(start=LIMSTART, stop=LIMEND, num=NUM_YS)
        Leiter = [[x, dotx, 0] for x in np.linspace(start=LIMSTART, stop=LIMEND, num=LEITER_RESOLUTION)]
        Bx, By, Bz, _ = BerechneFeld(Leiter, Strom=1, xs=(0,), ys=ys, zs=(8e-3,))
        
        Bx = Bx[:, :, 0]
        By = By[:, :, 0]
        Bz = Bz[:, :, 0]
        Bx = Bx.reshape(*Bx.shape, 1)
        By = By.reshape(*By.shape, 1)
        Bz = Bz.reshape(*Bz.shape, 1)
        Bv = np.concatenate((Bx, By, Bz), axis=2)

        for plot in [magplot, magplot_centered]:
            plot.plot(ys, Bv[0, :, 2], color='k', linestyle=':')

        Bv_tot += Bv

    for plot in [magplot, magplot_centered]:
        plot.plot(ys, Bv_tot[0, :, 2], color='r')
    magplot_centered.set_xlim(dots_xs[0], dots_xs[1])

    replot_dir(Bv_tot)


def replot_dots(dots_xs):
    for plot in [coilplot, coilplot_centered]:
        plot.clear()
        for dot_x in dots_xs:
            plot.plot(dot_x, DOT_Y, color='red', marker='o', linestyle='')
    coilplot_centered.set_xlim(dots_xs[0], dots_xs[1])


update_plot()

fig.canvas.callbacks.connect('button_press_event', drag_start)
fig.canvas.callbacks.connect('button_release_event', drag_stop)
fig.canvas.callbacks.connect('motion_notify_event', drag)

root.mainloop()
