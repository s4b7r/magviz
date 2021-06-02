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
        # print(f'drag_start {_drag_data}')


def drag_stop(event):
    """End drag of an object"""
    # reset the drag information
    _drag_data["item"] = None
    _drag_data["x"] = 0
    _drag_data["y"] = 0
    # print(f'drag_stop {_drag_data}')


def drag(event):
    """Handle dragging of an object"""
    if _drag_data['item'] is not None and event.inaxes == coilplot:
        # compute how much the mouse has moved
        delta_x = event.xdata - _drag_data["x"]
        delta_y = 0
        # move the object the appropriate amount
        dots_xs[_drag_data['item']] += delta_x
        update_plot()
        # record the new position
        _drag_data["x"] = event.xdata
        _drag_data["y"] = event.ydata
        # print(f'drag {_drag_data}')


root = Tk()
root.bind('<Escape>', quit)

LIMSTART = -.25
LIMEND = -LIMSTART

fig = Figure(figsize=(5, 4), dpi=100)
axes = fig.subplots(nrows=3, ncols=1, sharex='col', sharey=False,
                    gridspec_kw={'height_ratios': [5, 1, 1]})
magplot = axes[0]
dirplot = axes[1]
coilplot = axes[2]
coilplot.set_xlim(LIMSTART, LIMEND)

plt_canvas = FigureCanvasTkAgg(fig, root)
plt_canvas.get_tk_widget().grid(row=0, column=0)

dots_xs = [
        -.1,
        .1
        ]
DOT_Y = 0


NUM_YS = 500
LEITER_RESOLUTION = 500


def update_plot():
    replot_dots(dots_xs)
    replot_mag()
    plt_canvas.draw()


def replot_dir(Bv_tot):
    def get_field_dir(field_vec):
        field_dir = field_vec / np.expand_dims(np.linalg.norm(field_vec, ord=2, axis=2), axis=2)
        field_dir += 1
        field_dir *= .5
        return field_dir

    Bd = get_field_dir(Bv_tot)
    ys = np.linspace(start=LIMSTART, stop=LIMEND, num=NUM_YS)
    dirplot.clear()
    dirplot.scatter(ys, np.zeros(shape=ys.shape), s=100, c=Bd[0, :], marker='o', antialiased=False, edgecolors='')


def replot_mag():
    magplot.clear()

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

        magplot.plot(ys, Bv[0, :, 2], color='k', linestyle=':')

        Bv_tot += Bv

    magplot.plot(ys, Bv_tot[0, :, 2], color='r')
    magplot.set_ylim(-3e-5, 3e-5)

    replot_dir(Bv_tot)


def replot_dots(dots_xs):
    coilplot.clear()
    for dot_x in dots_xs:
        coilplot.plot(dot_x, DOT_Y, color='red', marker='o', linestyle='')


update_plot()

fig.canvas.callbacks.connect('button_press_event', drag_start)
fig.canvas.callbacks.connect('button_release_event', drag_stop)
fig.canvas.callbacks.connect('motion_notify_event', drag)

root.mainloop()
