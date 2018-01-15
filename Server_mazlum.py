import threading
import queue
import socket
import sys
import time


class loggerThread (threading.Thread):
    def __init__(self, name,logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.logQueue=logQueue


    def run(self):
        print(self.name + " starting.")
        while True:
            if self.logQueue.qsize() > 0:
                log_msg = self.logQueue.get()
                try:
                    print(str(time.ctime()) + " - " + str(log_msg))

                except socket.error:
                    print(str(time.ctime()) + "sorun oluştu")

                    break

        print(self.name + " exiting." )


class SenderThread(threading.Thread):
    def __init__(self, name, cSocket, address, threadQueue, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.cSocket = cSocket
        self.address = address
        self.lQueue = logQueue
        self.fihrist = fihrist
        self.tQueue = threadQueue


    def outgoing_parser(self, data):
        self.nickname = ""
        protocol=data[0:3]

        if  data[0:3] == "USR" :
            nickname = data[4:]


            if nickname not in self.fihrist.keys():
                self.nickname = nickname
                response = "HEL " + nickname
                qq_msg=(None,None,None,None,response)
                self.tQueue.put((qq_msg))
                self.fihrist[nickname] = self.tQueue
                for key in self.fihrist.keys():
                    qq_msg=(None, None, None,None,"SYS " + self.nickname + "yeni kullanıcı tanımlandı")
                    self.fihrist[key].put((qq_msg))
                self.lQueue.put(self.nickname + " kullanıcısı tanımlandı.")
                return 0
            else:

                response = "REJ " + nickname
                return 0

        elif  data[0:3]== "LSQ":
            response = "LSA "

            for key in sorted(self.fihrist.keys()):
                response += key + ":"
            qq_msg=(None,None,response)
            self.tQueue.put((qq_msg))
            return 0

        elif  data[0:3] == "TIC":
            response = "TOC"
            self.cSocket(response)
            return 0

        elif  data[0:3] == "SAY":

            response = "SOK"
            qq_msg=(None,None,response)
            self.tQueue.put((qq_msg))
            msg = data[4:]


            for key in self.fihrist.keys():
                qq_msg=(None,None,response)
                self.fihrist[key].put((qq_msg))
            return 0

        elif  data[0:3] == "MSG":
            msg = data[4:].split(':',1)
            nick = msg[0]
            msg = msg[1]

            if nick not in self.fihrist.keys():
                response = "MNO " + nick

            else:
                q_msg = (nick, self.nickname, msg)
                self.fihrist[nick].put(q_msg)
                response = "MOK"
            qq_msg=(response)
            self.tQueue.put((qq_msg))
            return 0
        else:
            response = "ERR"
            qq_msg=(response)
            self.tQueue.put((qq_msg))
            return 0

    def run(self):
        self.lQueue.put("Starting " + self.name)
        while True:
                outgoing_data = self.cSocket.recv(1024).decode()
                self.outgoing_parser(outgoing_data)

        self.lQueue.put("Exiting " + self.name)




class WriteThread(threading.Thread):
    def __init__(self, name, cSocket, address, threadQueue, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.cSocket = cSocket
        self.address = address
        self.lQueue = logQueue
        self.tQueue = threadQueue


    def incoming_parser(self,data):
        if data[0]:
            going_msg = str("MSG " + data[1] + ":" + data[2])
            self.cSocket.send(going_msg.encode())


        elif data[1]:
            going_msg = str("SAY " + data[1] + ":" + data[2])
            self.cSocket.send(going_msg.encode())

        else:
            going_msg= str(data[-1])
            self.cSocket.send(going_msg.encode())

    def run(self):

        self.lQueue.put("Starting " + self.name)
        while True:
           if self.tQueue.qsize() > 0:
               q_msg = self.tQueue.get()
               self.incoming_parser(q_msg)

        self.lQueue.put("Exiting " + self.name)


def main():
    global fihrist
    host = ''
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    fihrist = {}
    print ("Soket olusturuldu")

    try:
        s.bind((host, port))
    except socket.error as msg:
        print( "Bind basarisiz. Hata kodu: " + str(msg[0]) + " Message " + msg[1])
        sys.exit()

    print ("Soket bind basarili")

    s.listen(10)
    print ("Soket dinlemede")
    #threadQueue = queue.Queue()
    logQueue = queue.Queue()
    lThread = loggerThread("Logger", logQueue)
    lThread.start()
    counter=0
    while 1:
        logQueue.put("Waiting for connection")
        threadQueue = queue.Queue()
        try:
            conn, addr = s.accept()
            logQueue.put("Got a connection from " + str(addr))
        except KeyboardInterrupt:
            s.close()
            logQueue.put('QUIT')
            break

        print ("Baglanildi " + addr[0] + ":" + str(addr[1]))

        senderThread = SenderThread('ReadThread-'+str(counter),conn,addr,threadQueue,logQueue)
        senderThread.start()
        writeThread = WriteThread('WriteThread-'+str(counter), conn, addr, threadQueue, logQueue)
        writeThread.start()
        counter+=1



if __name__ == '__main__':
    main()
