#!/usr/bin/python

from Tkinter import *
import time

from Tkinter import *


class App:

    def callback(self, event):
        if not self.started:
            return
        tstamp = time.time()
        delta = tstamp - self.lastevt
        if delta > 0.30:
            self.lastevt = tstamp
            delta2 = tstamp - self.starttime
            x = event.x - 100
            if x < 0:
                x = 0
            if x > 500:
                x = 500
            print round(delta2, 3), "    ", x

    def __init__(self, master):

        self.lastevt = time.time()
        self.starttime = time.time()
        self.started = False

        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Start", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        self.canvas = Canvas(master, width=700, height=100)
        self.canvas.bind("<Motion>", self.callback)
        self.canvas.pack()
        self.canvas.create_rectangle(100, 0, 600, 100, fill="blue")

    def say_hi(self):
        self.starttime = time.time()
        self.started = True

root = Tk()

app = App(root)

root.mainloop()
root.destroy() # optional; see description below

