import zmq
import threading

import constPipe as const

class Splitter(threading.Thread):
    def __init__(self, text):
        threading.Thread.__init__(self)
        self.text = text

    def run(self):
        context = zmq.Context()
        mapper_socket = context.socket(zmq.PUSH)
        mapper_socket.bind(f"tcp://*:{const.PORT1}")
        lines = self.text.splitlines()

        for line in lines:
            print(f"Splitter: Sending line: {line}")
            mapper_socket.send_string(line)

if __name__ == "__main__":
    with open("Wordcount.txt", "r") as txt:
        text = txt.read()

    splitter = Splitter(text)
    splitter.start()
