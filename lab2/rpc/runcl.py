import rpc
import logging
from time import sleep

from context import lab_logging

def callback(result_list):
    print("Result: {}".format(result_list.value))

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list,callback)

for i in range(5) :
    print("waiting for client")
    sleep(2)

cl.stop()
