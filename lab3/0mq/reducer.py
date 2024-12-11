from collections import defaultdict
import sys
import zmq
import threading

class Reducer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.word_counts = defaultdict(int)

    def run(self):
        context = zmq.Context()
        mapper_socket = context.socket(zmq.PULL)
        mapper_socket.bind(f"tcp://*:{self.port}")

        while True:
            word = mapper_socket.recv_string()
            self.word_counts[word] += 1
            print(f"Reducer on port {self.port}: '{word}' count is now {self.word_counts[word]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error - Usage: python Reducer.py <port>")
        sys.exit(1)     # script outputs error message and exits (sys.exit(1)), if no argument (<port>) is provided

    port = sys.argv[1]
    reducer = Reducer(port)
    reducer.run()
