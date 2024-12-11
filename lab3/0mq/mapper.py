import zmq
import threading

import constPipe as const

class Mapper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        splitter_socket = context.socket(zmq.PULL)
        splitter_socket.connect(f"tcp://localhost:{const.PORT1}")

        reducer1_socket = context.socket(zmq.PUSH)
        reducer1_socket.connect(f"tcp://localhost:{const.PORT2}")

        reducer2_socket = context.socket(zmq.PUSH)
        reducer2_socket.connect(f"tcp://localhost:{const.PORT3}")

        while True:
            sentence = splitter_socket.recv().decode('utf-8')
            print(f"Mapper: Received sentence: {sentence}")
            words = sentence.lower().split()

            for word in words:
                if word[0] < 'm':
                    print(f"Mapper: Sending '{word}' to Reducer 1")
                    reducer1_socket.send_string(word)
                else:
                    print(f"Mapper: Sending '{word}' to Reducer 2")
                    reducer2_socket.send_string(word)

if __name__ == "__main__":
    mapper = Mapper()
    mapper.start()
