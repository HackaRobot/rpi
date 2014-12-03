#!/usr/bin/python

from Tkinter import *
import time

class App:

    def callback(self, event):
        if self.state != "ROCK_N_ROLL":
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
            print x, "    ", round(delta2, 3)

    def tick(self):
        self.countdown -= 1
        if self.countdown == 0:
            self.var.set("Rockin n rollin")
            self.state = "ROCK_N_ROLL"
            self.starttime = time.time()
        elif self.countdown >= 0:
            self.var.set("Start in: " + repr(self.countdown))
            self.timer.after(1000, self.tick)

    def __init__(self, master):

        self.lastevt = time.time()
        self.starttime = time.time()
        self.started = False
        self.countdown = 5
        self.state = "INIT"

        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Start", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        self.var = StringVar()
        self.var.set("Click Start to begin")
        self.timer = Label(frame, textvariable=self.var)
        self.timer.pack(side=BOTTOM)

        self.canvas = Canvas(master, width=700, height=100)
        self.canvas.bind("<Motion>", self.callback)
        self.canvas.pack()
        self.canvas.create_rectangle(100, 0, 600, 100, fill="blue")

    def say_hi(self):
        if self.state == "INIT":
            self.starttime = time.time()
            self.started = True
            self.state = "COUNTING_DOWN"
            self.tick()

root = Tk()

app = App(root)

root.mainloop()
root.destroy() # optional; see description below
