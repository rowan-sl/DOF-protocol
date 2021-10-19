import argparse
import pathlib
from typing import Iterable, NoReturn, Optional
import bitstring as bs
import msgpack
import uuid
import time
#commandline args
from args import args

#output, general
#zero and one, bianary values
SRV_OUT: pathlib.Path = args.io_file[0]
#signal that server has read a thing
#one = read a thing, zero = normal status
SRV_STAT: pathlib.Path = args.io_file[1]
#signal that client must read a thing
#one = must read, zero = nothing new
SRV_READ_SIG: pathlib.Path = args.io_file[2]
#client out, server in
CLI_OUT: pathlib.Path = args.io_file[3]
#signal that client has read a thing
CLI_STAT: pathlib.Path = args.io_file[4]
#signal that the server must read a thing
CLI_READ_SIG: pathlib.Path = args.io_file[5]

ALL_IO = [SRV_OUT, SRV_READ_SIG, SRV_STAT, CLI_OUT, CLI_READ_SIG, CLI_STAT]

def encode(obj):
    """encode a object to a list of 1's and 0's using msgpack"""
    return [1 if i is True else 0 for i in bs.Bits(auto=msgpack.packb(obj))]

def decode(bits: list):
    """decode a list of 1's and 0's to a object using msgpack"""
    return msgpack.loads(bs.Bits(auto=[True if i == 1 else False for i in bs.Bits(auto=bits)]).tobytes())

def get_io(io: pathlib.Path) -> int:
    "gets value from io and returns it as a int."
    with io.open("r") as f:
        while True:
            content = f.read()
            try:
                content = int(content)
                return content
            except ValueError:
                pass

def set_io(io: pathlib.Path, stat: int) -> None:
    "sets output to stat"
    assert stat in [1, 0]
    with io.open("w") as f:
        f.write(str(stat))

def wait_for(io: pathlib.Path, val):
    while True:
        if val == get_io(io):
            break

message = []

def recieve(val: int):
    "called when a value is recieved that is a new piece of data from the client"
    print(val)
    message.append(val)

#reset all io to zero
for i in ALL_IO:
    set_io(i, 0)

while True:
    #check if we need to read a thing
    stat = get_io(CLI_READ_SIG)
    #there is something to read
    if stat:
        #get that thing
        val = get_io(CLI_OUT)
        recieve(val)
        #tell client that it has been read
        set_io(SRV_STAT, 1)
        #wait for client to disable read signal
        wait_for(CLI_READ_SIG, 0)
        #reset server status, ready to move on
        set_io(SRV_STAT, 0)
    #check if that was the end of the message
    done = get_io(CLI_STAT)
    if done:
        #print the message
        print(decode(message))
        message = []
        #tell the client we go the message
        set_io(SRV_STAT, 1)
        #wait for client to agnowlage
        wait_for(CLI_STAT, 0)
        #reset srv stat
        set_io(SRV_STAT, 0)
        #ready to move on
