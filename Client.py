
import threading
import queue
import socket
import sys
import time


''''logger thread düzgün çalışıyor ama girdiler ve çıktılar birbirne giriyor
    kullanıcı arayüzü kullanmamız şart artık:)))))))))
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

   '''


class SenderThread (threading.Thread):
    def __init__(self, name, cSocket, threadQueue,logQueue):
        threading.Thread.__init__(self)
        self.nickname=None
        self.name = name
        self.cSocket = cSocket
        self.logQueue=logQueue
        self.threadQueue=threadQueue

    def csend(self,data):
        self.cSocket.send(data.encode())
    def run(self):
        self.logQueue.put("Starting " + self.name)

        while True:
            data=input("protcol gir!!")

            response = self.outgoing_parser(data)
            self.threadQueue.put(response)
        self.logQueue.put("Exiting " + self.name)

    def outgoing_parser(self, protocol):




        if protocol == "/n":
                nickname=input("nickname gir")
                response = "USR " + nickname
                self.csend(response)


        elif  protocol =="/l":
               response="LSQ"
               self.csend(response)

        elif protocol=="/q":
            while 1:
              response="TIC"
              self.csend(response)

        elif protocol=="/p":
              response="OUI"
              self.csend(response)

        elif protocol=="/k":

              response="SAY"
              msg=input("msg")
              self.csend(response+":"+str(msg))

        elif  protocol == "/m":
             msg=input("msg")
             nick=input("nickname1")
             message=nick +":"+msg
             response="MSG" +":"+message
             self.csend(response)


        else:
            response="ERR"
            self.csend(response)
            return 0





class ReaderThread (threading.Thread):
    def __init__(self, name, csoc,threadQueue,logQueue):
        threading.Thread.__init__(self)
        self.nickname=None
        self.name = name
        self.csoc = csoc
        self.threadQueue=threadQueue
        self.logQueue=logQueue


    def run(self):
        self.logQueue.put("Starting " + self.name)

        while True:
            data = self.csoc.recv(1024).decode()
            response = self.incoming_parser(data)
            self.threadQueue.put(response)

        self.logQueue.put("Exiting " + self.name)

    def incoming_parser(self, data):
        data = data.strip()
        protocol = data[0:3]
        #nickname = data[4:].strip()
        rest=data[4:]

        #self.csoc.send()!!!henüz kullanıcı arayüzü kullanmadığımız için bu kısmı  bir yerlere yazdırmayı gereksiz görüyorum.
        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            #self.csoc.send(response.encode())
            return
        if protocol == "BYE":

            self.csoc.close()
            return
        if protocol == "ERL":
            response = "server bulunamadı"
            #self.csoc.send(response.encode())
            return
        if protocol == "HEL":
            response = "kullanıcı tanımlandı <" + data[4:] + ">"
            #self.csoc.send(response.encode())
            self.nickname = data[4:]
            return
        if protocol == "REJ":
            response = "bu kullanıcı zaten var!!"
            #self.csoc.send(response.encode())
            return
        if protocol == "MNO":
            response = "yanlış kullanıcı " + data[4:]
            #self.csoc.send(response.encode())
            return
        if protocol == "MSG":


            usrName = (rest.split(":", 1)[0])
            restMessage = (rest.split(":", 1)[1])

            #self.csoc.send(response.encode())
            return
        if protocol == "SAY":
            usrName = (rest.split(":", 1)[0])
            restMessage = (rest.split(":", 1)[1])

            #self.csoc.send(response.encode())
            return
        if protocol == "TIC":
            response = "TOC"
            #self.csoc.send(response.encode())
            return
        if protocol == "SYS":
            response = "System" + data[4:]
            #self.csoc.send(response.encode())
            return
        if protocol == "LSA":
            rest = data[4:]
            splitted = rest.split(":")
            msg = "kayıtlı kullanıcılar: "
            for i in splitted:
                msg += i + ","
            msg = msg[:-1]
            #self.csoc.send(msg)/
            return







def main():
    logQueue = queue.Queue()
    #lThread = loggerThread("Logger", logQueue)
    #lThread.start()
    threadQueue = queue.Queue()
    if len(sys.argv) == 3:
        host = str(sys.argv[1])
        port = int(sys.argv[2])

    count=0


    while 1:
        host = '46.196.19.7'
        #host='0.0.0.0'
        # host = socket.gethostname()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #host = socket.gethostname()
        port = 12345

        try:
            s.connect((host, port))
        except Exception:
            print("Baglanti hatasi.")
            sys.exit(0)
        sendThread = SenderThread('senderThread-'+str(count),s,threadQueue,logQueue)
        sendThread.start()
        readThread = ReaderThread('ReadThread-' + str(count), s,threadQueue,logQueue)
        readThread.start()
        count+=1

        sendThread.join()
        readThread.join()

        s.close()

if __name__ == '__main__':
    main()