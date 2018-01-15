#!/usr/bin/env python3.4
import re
from difflib import SequenceMatcher
import threading
import queue
import socket
import time
import sys

def fihristParser(fileName):
    pattern = "([0-9\s]*)\s---\s(.*)$"
    ret = {}
    with open(fileName,'r') as f:
        for line in f:
            searchObj = re.match(pattern,line)
            if searchObj:
                ret[searchObj.group(2)] = searchObj.group(1)
    return ret

class loggerThread (threading.Thread):
    def __init__(self, name, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue

    def run(self):
        print(self.name + " starting.")
        while True:
            msg = self.logQueue.get()
            if msg == "QUIT":
                print(self.name + ": QUIT received.")
                break
            print(str(time.ctime()) + " - " + str(msg))
        print(self.name + " exiting." )

class clientThread(threading.Thread):
    def __init__(self, name, clientSocket, addr, fihrist, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue = logQueue
        self.c = clientSocket
        self.addr = addr
        self.fihrist = fihrist

    def run(self):
        self.logQueue.put(self.name + ": starting")
        while True:
            msg = self.c.recv(1024).decode()

            ret = self.parser(msg)  + "\n"
            self.c.send(ret.encode())
            if ret == 'BY\n':
                self.c.close()
                break

        self.logQueue.put(self.name + ": exiting")

    def parser(self, msg):
        # simple protocol
        if len(msg) < 2:
            return 'ER'

        if msg[0:2] == 'HI':
            return 'HI'

        if msg[0:2] == 'RQ':
            if len(msg) < 3:
                return 'ER'
            country = msg[3:].strip()
            if country in self.fihrist.keys():
                return 'RE ' + self.fihrist[country]
            else:
                return 'NF ' + country
        if msg[0:2] == 'QU':
            return 'BY'
        return 'ER'

def main():
    fihrist = fihristParser("codes.txt")

    # start the logger thread
    lQueue = queue.Queue()
    lThread = loggerThread("Logger", lQueue)
    lThread.start()

    # start listening
    s = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s.bind((host,port))
    s.listen(5)

    # give unique name to all of the threads
    counter = 0

    while True:
        # close the port gracefully
        try:
            c, addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            lQueue.put('QUIT')
            break

        lQueue.put('Got new connection from' + str(addr))
        newThread = clientThread('Thread-' + str(counter),
                                 c,
                                 addr,
                                 fihrist,
                                 lQueue)
        newThread.start()
        counter += 1

if __name__ == '__main__':
    main()


