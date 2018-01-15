#!/usr/bin/env python
from multiprocessing import Queue, Process
import threading
import time
from decimal import *
getcontext().prec = 100

logQueue = Queue()

class loggerThread (threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print(self.name + " starting.")
        while True:
            msg = logQueue.get()
            if msg == "QUIT":
                print(self.name + ": QUIT received.")
                break
            print(str(time.ctime()) + " - " + str(msg))
        print(self.name + " exiting." )

def nilakantha_step(k):
    if k % 2:
        sign = 1
    else:
        sign = -1
    ret = Decimal(sign) / (Decimal(k)*2 * (Decimal(k)*2+1) * (Decimal(k)*2+ 2))
    return ret

def workerProcess(name, workQueue, outQueue):
    logQueue.put("Process %s starting" % (name))
    while True:
        if workQueue.qsize() > 0:
            msg = workQueue.get()
            logQueue.put("Message received: %s" % (msg))
            if msg == "QUIT":
                break
            else:
                start = msg[0]
                end = msg[1]
                sum = 0
                for k in range(start, end):
                    sum += nilakantha_step(k)
                outQueue.put(sum)
                logQueue.put("Process %s sums: %s" % (name,sum))
        time.sleep(.0001)
    logQueue.put("Process %s ending" % (name))

N = 1000000
numProcesses = 8
workQueues = []
workers = []
sumQueue = Queue()

logThread = loggerThread("Logger")
logThread.start()

for name in range(numProcesses):
    processQueue = Queue()
    p = Process(target=workerProcess, args=(name, processQueue, sumQueue))
    workers.append(p)
    workQueues.append(processQueue)

for p in workers:
    time.sleep(.01)
    p.start()

for q in range(numProcesses):
    start = int((N / numProcesses) * q) + 1
    end = int((N / numProcesses) * q + (N / numProcesses)) + 1
    workQueues[q].put([start, end])

sum = 3

counter = numProcesses
while counter > 0:
    sum += 4 * sumQueue.get()
    counter -= 1
logQueue.put(sum)

for q in workQueues:
    q.put("QUIT")

for p in workers:
    p.join()

logQueue.put("QUIT")

logThread.join()
