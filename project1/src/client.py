import grpc
import groupChat_pb2
import groupChat_pb2_grpc
import logging
import threading
import time
import json


address = 'localhost'
port = 8001
timeSleep = 1


COMMANDS = {
    "u": 1,  # login
    "j": 2,  # join
    "a": 3,  # chat
    "l": 4,  # like
    "r": 5,  # dislike
    "p": 6  # history
}


class Client:
    def __init__(self, host, port):
        self.channel = grpc.insecure_channel(host + ':' + str(port))
        self.stub = groupChat_pb2_grpc.ChatServerStub(self.channel)
        self.loginName = None
        self.groupName = None
        self.participants = None

    # Getting user input and sending messages to server
    def send(self):
        self.input()

    # Getting terminal line input and split to id and message, return the ChatInput
    def input(self):
        while True:
            try:
                inputs = input().split(maxsplit=1)
                if (len(inputs) == 1):
                    if (inputs[0] == "q"):
                        break
                    else:
                        raise ValueError
                _com, _message = inputs
            except ValueError:
                print(
                    "Invalid input format. Please enter a command followed by a message.")
                continue
            _type = COMMANDS.get(_com, None)
            if not _type:
                print("Invalid command")
                continue
            if _type == 1:
                self.loginName = _message
                print("Login as: " + self.loginName)
                self.stub.chatFunction(groupChat_pb2.ChatInput(type=_type, message=_message, userName=self.loginName, groupName="", messageId=0))
            elif _type == 2:
                self.groupName = _message
                print("Entering group: " + self.groupName)
                self.stub.chatFunction(groupChat_pb2.ChatInput(type=_type, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0))
                # Thread for listening to server messages
                listen_thread = threading.Thread(target=self.listen)
                listen_thread.start()
            elif _type == 3:
                self.stub.chatFunction(groupChat_pb2.ChatInput(type=_type, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0))
            else:
                if self.loginName == None:
                    print("Please login first")
                elif self.groupName == None:
                    print("Please join a group first")
                else:
                    print("error")

        print("Exiting...")
        self.channel.close()
        exit()

    # listening to server messages
    def listen(self):
        while True:
            for r in self.stub.getMessages(groupChat_pb2.ChatInput(userName=self.loginName, groupName=self.groupName, type=0, message="", messageId=0)):
                print("Message from server: {0}. {1} {2: >10}".format(
                    r.id, r.content, r.numberOfLikes))

    # output messages from server
    def output(self, response):
        print(response.status)
        for message in response.messages:
            print("Message from server: {0}. {1} {2: >10}".format(
                message.id, message.content, message.numberOfLikes))


def run():
    client = Client(address, port)

    # Thread for sending messages to server
    input_thread = threading.Thread(target=client.send)
    input_thread.start()
    input_thread.join()


if __name__ == '__main__':
    logging.basicConfig()
    run()
