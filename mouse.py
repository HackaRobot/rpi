#!/usr/bin/python

from Tkinter import *
import time
import pygame.mixer

class App:

    def callback(self, event):
        if self.state != "ROCK_N_ROLL":
            return
        tstamp = time.time()
        delta = tstamp - self.lastevt
        xdelta = 100
        if self.lastpos != None:
            xdelta = abs(event.x - self.lastpos)
        else:
            self.lastpos = event.x
        if delta > 0.20 and xdelta > 10:
            self.lastevt = tstamp
            self.lastpos = event.x
            delta2 = tstamp - self.starttime
            x = event.x - 100
            if x < 0:
                x = 0
            if x > 500:
                x = 500
            print x, "    ", round(delta2, 3)

    def __init__(self, master):

        self.lastevt = time.time()
        self.starttime = 0
        self.countdown = 5
        self.state = "INIT"
        self.lastpos = None
        self.bg = None

        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Start", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        self.filetext = Text(frame, height=1, width=20)
        self.filetext.pack(side=RIGHT)
        self.timer = Label(frame, textvariable="Music file path")
        self.timer.pack(side=RIGHT)

        self.canvas = Canvas(master, width=700, height=200)
        self.canvas.bind("<Motion>", self.callback)
        self.canvas.pack()
        self.canvas.create_rectangle(100, 0, 600, 200, fill="blue")

        pygame.mixer.init(channels=2,frequency=48000,size=-16)

    def say_hi(self):
        if self.state == "INIT":
            mfile = self.filetext.get(1.0, END)[:-1]
            pygame.mixer.music.load(mfile)
            pygame.mixer.music.play(0)
            self.starttime = time.time()
            self.state = 'ROCK_N_ROLL'


root = Tk()

app = App(root)

root.mainloop()
root.destroy() # optional; see description below
