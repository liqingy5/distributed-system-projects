import grpc
import group_chat_pb2
import group_chat_pb2_grpc
import threading
import uuid
import json
import sys
import argparse

COMMANDS = {
    "u": 1,  # login
    "j": 2,  # join
    "a": 3,  # chat
    "l": 4,  # like
    "r": 5,  # dislike
    "p": 6,   # history
    "q": 7,   # quit
    "v": 8    # view
}

DEBUG = False


class ChatClient():
    def __init__(self):
        self.channel = None
        self.stub = None
        self.loginName = None
        self.groupName = None
        self.listen_thread = None
        self.exit = False
        self.uuid = str(uuid.uuid4())
        self.resetFlag = False

    # Getting user input and sending messages to server

    def send(self):
        print("Type 'u <username>' to login, 'j <groupname>' to join a group, 'a <message>' to chat, 'l <message_id>' to like a message, 'r <message_id>' to dislike a message, 'p' to get history, 'q' to quit 'v' to view the current server Id")
        self.input()

    # Getting terminal line input and split to id and message, return the ChatInput

    def input(self):
        # Loop for keeping reading user input
        while True:
            try:
                if self.resetFlag:
                    self.resetFlag = False
                    break
                inputs = input().split(maxsplit=1)
                if (len(inputs) == 1):
                    _com = inputs[0]
                    _message = ""
                    # Exit the program if detect quit command
                    if (_com == "q"):
                        self.exit = True
                        if (self.loginName == None and self.groupName == None):
                            break
                        request = group_chat_pb2.ChatInput(
                            type=7, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0, uuid=self.uuid)
                        response = self.stub.chatFunction(request)
                        if (self.channel != None):
                            self.channel.close()
                        break
                    # Print history messagges if detect p command
                    elif (_com == 'p'):
                        if (self.loginName == None or self.groupName == None):
                            print("Please login and join a group first")
                            continue
                        request = group_chat_pb2.ChatInput(
                            userName=self.loginName, groupName=self.groupName, type=6, message="", messageId=0, uuid=self.uuid)
                        response = self.stub.chatFunction(request)
                        self.output(response)
                    elif (_com == 'v'):
                        request = group_chat_pb2.ChatInput(
                            userName="", groupName="", type=8, message="", messageId=0, uuid=self.uuid)
                        response = self.stub.chatFunction(request)
                        views = []
                        for r in response.messages:
                            views.append(r.content)
                        if (response != False):
                            print(
                                f"servers that can current communicate with each other: {views}")
                        else:
                            print(f"Internal error please try later")

                    else:
                        raise ValueError
                else:
                    _com, _message = inputs
                    _type = COMMANDS.get(_com, None)
                    # print invalid if command not found
                    if not _type:
                        print("Invalid command")
                        continue
                    # Send user name to the server
                    if _type == 1:
                        request = group_chat_pb2.ChatInput(
                            type=_type, message=_message, userName=_message, groupName="", messageId=0, uuid=self.uuid)
                        response = self.stub.chatFunction(request)
                        if response != False:
                            self.loginName = _message
                            print("Login as: " + self.loginName)
                        else:
                            print("Login failed, please try again")
                    # Send join group message to the server if logged in
                    elif _type == 2 and self.loginName is not None:
                        self.groupName = _message
                        request = group_chat_pb2.ChatInput(
                            type=_type, message=_message, userName=self.loginName, groupName=_message, messageId=0, uuid=self.uuid)
                        response = self.stub.chatFunction(request)
                        # if (response.status == "success"):
                        if (response != False):
                            print("Group: " + self.groupName)
                            print("Participants: " + ', '.join(response.user))
                            # Success logged in and joined in will start the thread for listening new messages in groupChat from server
                            self.listen_thread = threading.Thread(
                                target=self.listen, daemon=True)
                            self.listen_thread.start()
                    # If logged in and joined a group
                    elif self.loginName is not None and self.groupName is not None:
                        # Append new messages
                        if _type == 3:
                            request = group_chat_pb2.ChatInput(
                                type=_type, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0, uuid=self.uuid)
                            print("------------------------------------")
                            response = self.stub.chatFunction(request)
                        # Add like to the message
                        elif _type == 4:
                            try:
                                _msgId = int(_message)
                                request = group_chat_pb2.ChatInput(
                                    type=_type, message="", userName=self.loginName, groupName=self.groupName, messageId=_msgId, uuid=self.uuid)
                                response = self.stub.chatFunction(request)
                                if (response != False and len(response.messages) > 0):
                                    self.output(response)
                            except ValueError:
                                print("Error type")
                        # Remove like from the message
                        elif _type == 5:
                            try:
                                _msgId = int(_message)
                                request = group_chat_pb2.ChatInput(
                                    type=_type, message="", userName=self.loginName, groupName=self.groupName, messageId=_msgId, uuid=self.uuid)
                                response = self.stub.chatFunction(request)
                                if (response != False and len(response.messages) > 0):
                                    self.output(response)
                            except ValueError:
                                print("Error type")
                        else:
                            print("Internal error,plesae try again")
                    else:
                        if (self.loginName == None):
                            print("Please login first")
                        elif (self.groupName == None):
                            print("Please join a group first")

            except ValueError as e:
                print(
                    "Invalid input format. Please enter a command followed by a message.")
                continue
            except grpc.RpcError as e:
                print("Connect to server failed, please try again or different servers")
                break

        # Kill the listen thread
        self.reset()
        if (self.exit == True):
            print("Exiting...")
            sys.exit(0)
        self.run()

    # listening to server messages

    def listen(self):
        try:
            for r in self.stub.getMessages(group_chat_pb2.ChatInput(
                    userName=self.loginName, groupName=self.groupName, type=0, message="", messageId=0, uuid=self.uuid)):
                # -999 means the client has request to disconnect, stop the thread for listening
                if r.id == -999:
                    break
                # -998 means there is a changed in participant members, print current participants
                if (self.exit == False):
                    if r.id == -998:
                        if (r.content == self.groupName):
                            print("Participants: "+r.user)
                    else:
                        print("{0}. {1}: {2} {3: >10}".format(
                            r.id, r.user, r.content, r.numberOfLikes > 0 and "likes: "+str(r.numberOfLikes) or ""))
        except grpc.RpcError as e:
            printLog("Server disconnected")
            self.reset(True)

    def run(self):
        print("Please type 'c <hostname> <portnumber> to connect to Server")
        # waiting user input for address and port number
        while True:
            try:
                inputs = input().split()
                if (len(inputs) != 3):
                    if (len(inputs) == 1 and inputs[0] == 'q'):
                        self.exit = True
                        sys.exit(0)
                    else:
                        raise ValueError
                _com, _address, _port = inputs
                if (_com == 'c'):
                    self.channel = grpc.insecure_channel(_address+":"+_port)
                    self.stub = group_chat_pb2_grpc.ChatServerStub(
                        self.channel)
                    self.send()
                    break
                else:
                    raise ValueError
            except ValueError:
                print(
                    "Invalid input format. Please type 'c <hostname> <portnumber> to connect to Server")
                continue

    # output messages from server

    def output(self, response):
        print("------------------------------------")
        if (response == False):
            print("Internal error, please try again")
            return
        for r in response.messages:
            print("{0}. {1}: {2} {3: >10}".format(
                r.id, r.user, r.content, r.numberOfLikes > 0 and "likes: "+str(r.numberOfLikes) or ""))
        print("------------------------------------")

    def reset(self, flag = False):
        if (self.channel != None):
            self.channel.close()
        self.channel = None
        self.stub = None
        self.groupName = None
        self.loginName = None
        self.uuid = str(uuid.uuid4())
        self.resetFlag = flag


def printLog(msg):
    global DEBUG
    if DEBUG:
        print(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", help="Debug", action="store_true")
    args = parser.parse_args()
    if args.D:
        DEBUG = True
    client = ChatClient()
    print("Client started")
    client.run()
