from time import sleep
import constRPC
import threading

from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self

class WaitForResponse(threading.Thread):
    def __init__(self, chan, server, callback):
        threading.Thread.__init__(self)
        self.chan = chan
        self.server = server
        self.callback = callback

    def run(self):
        
        msgrcv = self.chan.receive_from(self.server)

    
        print("Der Server hat dem Thread geantwortet:", msgrcv)

        self.callback(msgrcv[1])


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')

    def stop(self):
        self.chan.leave('client')

    def append(self, data, db_list, callback):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, constRPC.CALLBACK, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server
        msgrcv = self.chan.receive_from(self.server)  # wait for response

        

        if not constRPC.ACK == msgrcv[1]:
            print("Kein ACK bekommen/erhalten.")
            return

        waitThread = WaitForResponse(self.chan, self.server, callback)
        waitThread.start()

        print("Der Warte-Thread wird nun auf die Antwort des Servers warten!")

        return 


class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        sleep(5)
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested

                    self.chan.send_to({client}, constRPC.ACK)   # send ACK

                    result = self.append(msgrpc[2], msgrpc[3])  # do local call

                    self.chan.send_to({client}, result)         # return response
                else:
                    pass  # unsupported request, simply ignore
