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
    "p": 6   # history
}


class Client:
    def __init__(self, host, port):
        self.channel = grpc.insecure_channel(host + ':' + str(port))
        self.stub = groupChat_pb2_grpc.ChatServerStub(self.channel)
        self.loginName = None
        self.groupName = None
        self.listen_thread = None

    # Getting user input and sending messages to server
    def send(self):
        print("Client started \nType 'u <username>' to login, 'j <groupname>' to join a group, 'a <message>' to chat, 'l <message_id>' to like a message, 'r <message_id>' to dislike a message, 'p' to get history, 'q' to quit")
        self.input()

    # Getting terminal line input and split to id and message, return the ChatInput
    def input(self):
        while True:
            try:
                inputs = input().split(maxsplit=1)
                if (len(inputs) == 1):
                    _com = inputs[0]
                    _message = ""

                    if (_com == "q"):
                        if (self.loginName == None and self.groupName == None):
                            break
                        response = self.stub.chatFunction(groupChat_pb2.ChatInput(
                            type=7, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0))
                        break
                    elif (_com == 'p'):
                        if (self.loginName == None or self.groupName == None):
                            print("Please login and join a group first")
                            continue
                        response = self.stub.chatFunction(groupChat_pb2.ChatInput(
                            userName=self.loginName, groupName=self.groupName, type=6, message="", messageId=0))
                        self.output(response)
                    else:
                        raise ValueError
                else:
                    _com, _message = inputs
                    _type = COMMANDS.get(_com, None)
                    if not _type:
                        print("Invalid command")
                        continue
                    if _type == 1:
                        response = self.stub.chatFunction(groupChat_pb2.ChatInput(
                            type=_type, message=_message, userName=_message, groupName="", messageId=0))
                        if (response.status == "success"):
                            self.loginName = _message
                            print("Login as: " + self.loginName)
                        else:
                            print("Login failed, please try again")
                    elif _type == 2 and self.loginName is not None:
                        response = self.stub.chatFunction(groupChat_pb2.ChatInput(
                            type=_type, message=_message, userName=self.loginName, groupName=_message, messageId=0))
                        if (response.status == "success"):
                            self.groupName = _message
                            print("Group: " + self.groupName)
                            print("Participants: " + ', '.join(response.user))
                            # Thread for listening to server messages
                            self.listen_thread = threading.Thread(
                                target=self.listen, daemon=True)
                            self.listen_thread.start()
                        else:
                            print("Join chat group failed, please try again")
                    elif self.loginName is not None and self.groupName is not None:
                        if _type == 3:
                            response = self.stub.chatFunction(groupChat_pb2.ChatInput(
                                type=_type, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0))
                        elif _type == 4:
                            try:
                                _msgId = int(_message)
                            except ValueError:
                                print("Error type")
                            response = self.stub.chatFunction(groupChat_pb2.ChatInput(
                                type=_type, message="", userName=self.loginName, groupName=self.groupName, messageId=_msgId))
                            if (response.status == "success" and len(response.messages) > 0):
                                self.output(response)
                        elif _type == 5:
                            try:
                                _msgId = int(_message)
                            except ValueError:
                                print("Error type")
                            response = self.stub.chatFunction(groupChat_pb2.ChatInput(
                                type=_type, message="", userName=self.loginName, groupName=self.groupName, messageId=_msgId))
                            if (response.status == "success" and len(response.messages) > 0):
                                self.output(response)
                        else:
                            print("Internal error,plesae try again")
                    else:
                        if (self.loginName == None):
                            print("Please login first")
                        elif (self.groupName == None):
                            print("Please join a group first")

            except ValueError:
                print(
                    "Invalid input format. Please enter a command followed by a message.")
                continue

        print("Exiting...")
        self.listen_thread.stop()
        self.listen_thread.join()
        self.channel.close()
        exit()

    # listening to server messages
    def listen(self):
        for r in self.stub.getMessages(groupChat_pb2.ChatInput(userName=self.loginName, groupName=self.groupName, type=0, message="", messageId=0)):
            print("{0}. {1}: {2} {3: >10}".format(
                r.id, r.user, r.content, r.numberOfLikes > 0 and "likes: "+str(r.numberOfLikes) or ""))

    # output messages from server
    def output(self, response):
        print("------------------------------------")
        for r in response.messages:
            print("{0}. {1}: {2} {3: >10}".format(
                r.id, r.user, r.content, r.numberOfLikes > 0 and "likes: "+str(r.numberOfLikes) or ""))
        print("------------------------------------")


def run():
    client = Client(address, port)

    # Thread for sending messages to server
    input_thread = threading.Thread(target=client.send)
    input_thread.start()
    input_thread.join()


if __name__ == '__main__':
    logging.basicConfig()
    run()
