from io import TextIOWrapper
from typing import Iterator
from dataclasses import dataclass
import json
import watchfiles

# def watch():
#     return watchfiles.watch("./broadcast.jsonl")

# def awatch():
#     return watchfiles.awatch("./broadcast.jsonl")

# def main():
#     for line in watch():
#         print(line)

# {"type": "broadcast", "data": "hello\n", "timestamp": 1695289718.6574712, "origin": "2020:abcd::212:4b00:1caa:3874", "received_from": "2020:abcd::212:4b00:1caa:3874", "recv_time": 1695289719.9195614}

@dataclass
class Message:
    """Class to represent a message sent over the network.

    Parameters
    ----------
    type : str
        The type of message.
    data : str
        The data in the message.
    timestamp : float
        The timestamp of the message.
    origin : str
        The origin of the message.
    """
    type: str
    data: str
    timestamp: float
    recv_time: float
    origin: str
    received_from: str

    # def __init__(self, type: str, data: str, timestamp: float, recv_time: float, origin: str, received_from: str):
    #     self.type = type
    #     self.data = data
    #     self.timestamp = timestamp
    #     self.recv_time = recv_time
    #     self.origin = origin
    #     self.received_from = received_from
        

    # def __str__(self):
    #     return f"{self.type} {self.data} {self.timestamp} {self.origin}"

    # def __repr__(self):
    #     return f"Message({self.type}, {self.data}, {self.timestamp}, {self.origin})"
    

class MessageWatch(Iterator[Message]):
    """Class to watch live data from a sensor.
    """
    watch: Iterator[watchfiles.Change]
    file_pos: int
    file: TextIOWrapper

    def __init__(self, path: str):
        self.watch = watchfiles.watch(path)
        self.file = open(path, "r")
        self.file_pos = self.file.tell()

    def __iter__(self) -> Iterator[Message]:
        return self
    
    def __next__(self) -> Message:
        next(self.watch)
        self.file.seek(self.file_pos)
        line = self.file.readline()
        self.file_pos = self.file.tell()
        return Message(**json.loads(line))
    

for message in MessageWatch("./broadcast.jsonl"):
    print(message)