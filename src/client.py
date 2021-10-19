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
#if used outside of transfering data, this means that the message being sent has finished.
CLI_STAT: pathlib.Path = args.io_file[4]
#signal that the server must read a thing
CLI_READ_SIG: pathlib.Path = args.io_file[5]

CLI_IO = [CLI_OUT, CLI_READ_SIG, CLI_STAT]

def get_io(io: pathlib.Path) -> int:
    with io.open("r") as f:
        while True:
            content = f.read()
            try:
                content = int(content)
                return content
            except ValueError:
                pass

def set_io(io: pathlib.Path, stat: int) -> None:
    assert stat in [1, 0]
    with io.open("w") as f:
        f.write(str(stat))

#reset all client io to zero
for i in CLI_IO:
    set_io(i, 0)

def encode(obj):
    """encode a object to a list of 1's and 0's using msgpack"""
    return [1 if i is True else 0 for i in bs.Bits(auto=msgpack.packb(obj))]

def decode(bits: list):
    """decode a list of 1's and 0's to a object using msgpack"""
    #oh god no a one liner
    return msgpack.loads(bs.Bits(auto=[True if i == 1 else False for i in bs.Bits(auto=bits)]).tobytes())

def wait_for(io: pathlib.Path, val):
    while True:
        if val == get_io(io):
            break

message = encode("Hello, world!")

def send_message(msg):
    for i in msg:
        #set output
        set_io(CLI_OUT, i)
        #set ready to read
        set_io(CLI_READ_SIG, 1)
        #wait for SRV_STAT to be 1, meaning it has been read
        wait_for(SRV_STAT, 1)
        #reset CLI_READ_SIG, telling server that it recognizing the value has been read
        set_io(CLI_READ_SIG, 0)
        #wait for server_stat to be 0, meaning that it is ready for the next value
        wait_for(SRV_STAT, 0)

    #tell the server the message is done
    set_io(CLI_STAT, 1)
    #wait for server to agnowlage (stat=1)
    wait_for(SRV_STAT, 1)
    #reset out
    set_io(CLI_STAT, 0)
    #wait for server to do the same
    wait_for(SRV_STAT, 0)

send_message(message)


