from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

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

figure = Figure(figsize=(5, 4), dpi=100)
plot = figure.add_subplot(1, 1, 1)

plot.plot(0.5, 0.3, color="red", marker="o", linestyle="")

x = [ 0.1, 0.2, 0.3 ]
y = [ -0.1, -0.2, -0.3 ]
plot.plot(x, y, color="blue", marker="x", linestyle="")

plt_canvas = FigureCanvasTkAgg(figure, root)
plt_canvas.get_tk_widget().grid(row=0, column=0)


def plt_click(event):
    print(event)
    plot.plot(event.xdata, event.ydata, color='green', marker='x', linestyle='')
    plt_canvas.draw()


figure.canvas.callbacks.connect('button_press_event', plt_click)

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
