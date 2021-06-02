from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



_drag_data = {"x": 0, "y": 0, "item": None}


def drag_start(event):
    """Begining drag of an object"""
    # record the item and its location
    _drag_data["item"] = coil_canvas.find_closest(event.x, event.y)[0]
    _drag_data["x"] = event.x
    _drag_data["y"] = event.y


def drag_stop(event):
    """End drag of an object"""
    # reset the drag information
    _drag_data["item"] = None
    _drag_data["x"] = 0
    _drag_data["y"] = 0


def drag(event):
    """Handle dragging of an object"""
    # compute how much the mouse has moved
    delta_x = event.x - _drag_data["x"]
    delta_y = 0
    # move the object the appropriate amount
    coil_canvas.move(_drag_data["item"], delta_x, delta_y)
    # record the new position
    _drag_data["x"] = event.x
    _drag_data["y"] = event.y


root = Tk()
root.bind('<Escape>', quit)

fig = Figure(figsize=(5, 4), dpi=100)
figgrid = fig.add_gridspec(5, 1)
magplot = fig.add_subplot(figgrid[:-1, 0])
# magplot.set_title('[0, :-1]')
coilplot = fig.add_subplot(figgrid[-1:, 0])
# coilplot.set_title('[0, -1:]')

magplot.plot(x := np.linspace(-1, 1, 50), np.sin(x))

plt_canvas = FigureCanvasTkAgg(fig, root)
plt_canvas.get_tk_widget().grid(row=0, column=0)


def plt_click(event):
    print(event)
    if event.inaxes == magplot:
        magplot.plot(event.xdata, event.ydata, color='green', marker='x', linestyle='')
        plt_canvas.draw()


fig.canvas.callbacks.connect('button_press_event', plt_click)

COIL_CANVAS_HEIGHT = 20
coil_canvas = Canvas(root, width=500, height=COIL_CANVAS_HEIGHT, background='gray75')
coil_canvas.grid(column=0, row=1)

DOT_SIZE = 10
DOT_START_Y = (COIL_CANVAS_HEIGHT - DOT_SIZE) / 2
coil_canvas.create_oval(0, DOT_START_Y, DOT_SIZE, DOT_START_Y + DOT_SIZE, fill='red', outline='blue', tags=('token',))

coil_canvas.tag_bind("token", "<ButtonPress-1>", drag_start)
coil_canvas.tag_bind("token", "<ButtonRelease-1>", drag_stop)
coil_canvas.tag_bind("token", "<B1-Motion>", drag)

root.mainloop()
