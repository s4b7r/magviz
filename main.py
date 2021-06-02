from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



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
    # record the item and its location
    _drag_data["item"] = find_closest_dot(event.xdata, dots_xs)
    _drag_data["x"] = event.xdata
    _drag_data["y"] = event.ydata
    print(f'drag_start {_drag_data}')


def drag_stop(event):
    """End drag of an object"""
    # reset the drag information
    _drag_data["item"] = None
    _drag_data["x"] = 0
    _drag_data["y"] = 0
    print(f'drag_stop {_drag_data}')


def drag(event):
    """Handle dragging of an object"""
    if _drag_data['item'] is not None:
        # compute how much the mouse has moved
        delta_x = event.xdata - _drag_data["x"]
        delta_y = 0
        # move the object the appropriate amount
        dots_xs[_drag_data['item']] += delta_x
        replot_dots(dots_xs)
        # record the new position
        _drag_data["x"] = event.xdata
        _drag_data["y"] = event.ydata
        print(f'drag {_drag_data}')


root = Tk()
root.bind('<Escape>', quit)

fig = Figure(figsize=(5, 4), dpi=100)
axes = fig.subplots(nrows=2, ncols=1, sharex='col', sharey=False,
                    gridspec_kw={'height_ratios': [4, 1]})
magplot = axes[0]
coilplot = axes[1]
coilplot.set_xlim(-1, 1)

plt_canvas = FigureCanvasTkAgg(fig, root)
plt_canvas.get_tk_widget().grid(row=0, column=0)

magplot.plot(x := np.linspace(-1, 1, 50), np.sin(x))

dots_xs = [
        -.5,
        .5
        ]
DOT_Y = 0


def replot_dots(dots_xs):
    coilplot.clear()
    for dot_x in dots_xs:
        coilplot.plot(dot_x, DOT_Y, color='red', marker='o', linestyle='')
    plt_canvas.draw()


replot_dots(dots_xs)

fig.canvas.callbacks.connect('button_press_event', drag_start)
fig.canvas.callbacks.connect('button_release_event', drag_stop)
fig.canvas.callbacks.connect('motion_notify_event', drag)

root.mainloop()
