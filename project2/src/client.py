import grpc
import raft_pb2
import raft_pb2_grpc
import threading
import uuid
import json

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

DEBUG = True


class raftClient():
    def __init__(self):
        self.peers = {}
        self.stubs = {}
        self.channels = {}
        self.loginName = None
        self.groupName = None
        self.listen_thread = None
        self.exit = False
        self.uuid = str(uuid.uuid4())
        print("Reading config file where we store the server addresses")
        if DEBUG:
            filename = "./config.json"
        else:
            filename = "./config_test.json"
        with open(filename, "r") as f:
            address_dict = json.load(f)
            for key, value in address_dict.items():
                self.peers[int(key)] = value
                channel = grpc.insecure_channel(value)
                stub = raft_pb2_grpc.RaftServerStub(channel)
                self.channels[int(key)] = channel
                self.stubs[int(key)] = stub

    # Getting user input and sending messages to server
    def send(self):
        print("Type 'u <username>' to login, 'j <groupname>' to join a group, 'a <message>' to chat, 'l <message_id>' to like a message, 'r <message_id>' to dislike a message, 'p' to get history, 'q' to quit 'v' to view the current server Id")
        self.input()

    # Getting terminal line input and split to id and message, return the ChatInput

    def input(self):
        # Loop for keeping reading user input
        while True:
            try:
                inputs = input().split(maxsplit=1)
                if (len(inputs) == 1):
                    _com = inputs[0]
                    _message = ""
                    # Exit the program if detect quit command
                    if (_com == "q"):
                        self.exit = True
                        if (self.loginName == None and self.groupName == None):
                            break
                        request = raft_pb2.ChatInput(
                            type=7, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0, uuid=self.uuid)
                        response = self.sendChatInput(request)
                        break
                    # Print history messagges if detect p command
                    elif (_com == 'p'):
                        if (self.loginName == None or self.groupName == None):
                            print("Please login and join a group first")
                            continue
                        request = raft_pb2.ChatInput(
                            userName=self.loginName, groupName=self.groupName, type=6, message="", messageId=0, uuid=self.uuid)
                        response = self.sendChatInput(request)
                        self.output(response)
                    elif (_com == 'v'):
                        request = raft_pb2.ChatInput(
                            userName="", groupName="", type=8, message="", messageId=0, uuid=self.uuid)
                        response = self.sendChatInput(request)
                        if (response != False):
                            print(
                                f"Current view at Server id {int(response.messages[0].content)}")
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
                        request = raft_pb2.ChatInput(
                            type=_type, message=_message, userName=_message, groupName="", messageId=0, uuid=self.uuid)
                        response = self.sendChatInput(request)
                        print(response)
                        if response != False:
                            self.loginName = _message
                            print("Login as: " + self.loginName)
                        else:
                            print("Login failed, please try again")
                    # Send join group message to the server if logged in
                    elif _type == 2 and self.loginName is not None:
                        self.groupName = _message
                        request = raft_pb2.ChatInput(
                            type=_type, message=_message, userName=self.loginName, groupName=_message, messageId=0, uuid=self.uuid)
                        response = self.sendChatInput(request)
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
                            request = raft_pb2.ChatInput(
                                type=_type, message=_message, userName=self.loginName, groupName=self.groupName, messageId=0, uuid=self.uuid)
                            response = self.sendChatInput(request)
                        # Add like to the message
                        elif _type == 4:
                            try:
                                _msgId = int(_message)
                                request = raft_pb2.ChatInput(
                                    type=_type, message="", userName=self.loginName, groupName=self.groupName, messageId=_msgId, uuid=self.uuid)
                                response = self.sendChatInput(request)
                                if (response != False and len(response.messages) > 0):
                                    self.output(response)
                            except ValueError:
                                print("Error type")
                        # Remove like from the message
                        elif _type == 5:
                            try:
                                _msgId = int(_message)
                                request = raft_pb2.ChatInput(
                                    type=_type, message="", userName=self.loginName, groupName=self.groupName, messageId=_msgId, uuid=self.uuid)
                                response = self.sendChatInput(request)
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

            except ValueError:
                print(
                    "Invalid input format. Please enter a command followed by a message.")
                continue

        print("Exiting...")
        # Kill the listen thread
        if (self.listen_thread != None):
            self.listen_thread.join()
        # Close the channel connection
        for id in self.channels.keys():
            self.channels[id].close()

    # listening to server messages
    def listen(self):
        isListening = True
        while isListening:
            for stub in self.stubs.values():
                if (self.exit == True or isListening == False):
                    break
                try:
                    for r in stub.getMessages(raft_pb2.ChatInput(
                            userName=self.loginName, groupName=self.groupName, type=0, message="", messageId=0, uuid=self.uuid)):
                        # -999 means the client has request to disconnect, stop the thread for listening
                        if r.id == -999:
                            isListening = False
                            break
                        # -998 means there is a changed in participant members, print current participants
                        if (self.exit == False):
                            if r.id == -998:
                                if (r.content == self.groupName):
                                    print("Participants: "+r.user)
                            else:
                                print("{0}. {1}: {2} {3: >10}".format(
                                    r.id, r.user, r.content, r.numberOfLikes > 0 and "likes: "+str(r.numberOfLikes) or ""))
                except:
                    continue

    def sendChatInput(self, request):
        for id in self.stubs.keys():
            try:
                stub = self.stubs[id]
                response = stub.chatFunction(request)
                if response.status == "success":
                    return response
            except grpc.RpcError as e:
                continue
        return False

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


def run():
    print("Client Start!!!")
    client = raftClient()
    input_thread = threading.Thread(target=client.send)
    input_thread.start()
    input_thread.join()


if __name__ == '__main__':
    run()
