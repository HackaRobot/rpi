#!/usr/bin/python
from collections import deque
import sys, time, select

class FSM:
    def __init__(self, fsm):
        self.events = deque()
        self.state = 'INIT'
        self.fsm = fsm

    def enqueue_event(self, event):
        #print "Enqueueing: " + event
        self.events.append(event)

    def have_events(self):
        return (len(self.events) > 0)

    def deliver_event(self, event):
        str = self.state + '-' + event
        if not str in self.fsm:
            raise RuntimeError("Don't know how to handle event {0} while in state {1}".format(event, self.state))
        (nextstate, action) = self.fsm[str]
        # print "Current state: {0}, event: {1}, next state: {2}".format(self.state, event, nextstate)
        self.state = nextstate;
        if action:
            action()

    def get_next_event(self):
        if len(self.events) == 0:
            raise RuntimeError("Event queue is empty!")
        return self.events.popleft()

    def run(self):
        while True:
            event = self.get_next_event()
            self.deliver_event(event)
