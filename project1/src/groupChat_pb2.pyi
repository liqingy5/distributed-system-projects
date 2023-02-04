from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HistoryMessage(_message.Message):
    __slots__ = ["content", "id", "numberOfLikes"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFLIKES_FIELD_NUMBER: _ClassVar[int]
    content: str
    id: int
    numberOfLikes: int
    def __init__(self, id: _Optional[int] = ..., content: _Optional[str] = ..., numberOfLikes: _Optional[int] = ...) -> None: ...

class JoinRequest(_message.Message):
    __slots__ = ["groupName", "userName"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    userName: str
    def __init__(self, groupName: _Optional[str] = ..., userName: _Optional[str] = ...) -> None: ...

class JoinResponse(_message.Message):
    __slots__ = ["messages", "names"]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[HistoryMessage]
    names: _containers.RepeatedCompositeFieldContainer[Participant]
    def __init__(self, messages: _Optional[_Iterable[_Union[HistoryMessage, _Mapping]]] = ..., names: _Optional[_Iterable[_Union[Participant, _Mapping]]] = ...) -> None: ...

class LikeReponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class LikeRequest(_message.Message):
    __slots__ = ["groupName", "id", "username"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    id: int
    username: str
    def __init__(self, groupName: _Optional[str] = ..., id: _Optional[int] = ..., username: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ["userName"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    userName: str
    def __init__(self, userName: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class NewMessageRequest(_message.Message):
    __slots__ = ["groupName", "messageContent", "username"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGECONTENT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    messageContent: str
    username: str
    def __init__(self, groupName: _Optional[str] = ..., messageContent: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...

class NewMessageResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class Participant(_message.Message):
    __slots__ = ["userName"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    userName: str
    def __init__(self, userName: _Optional[str] = ...) -> None: ...

class ReceiveMessageRequest(_message.Message):
    __slots__ = ["groupName"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    def __init__(self, groupName: _Optional[str] = ...) -> None: ...

class RemoveLikeReponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class RemoveLikeRequest(_message.Message):
    __slots__ = ["groupName", "id", "username"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    id: int
    username: str
    def __init__(self, groupName: _Optional[str] = ..., id: _Optional[int] = ..., username: _Optional[str] = ...) -> None: ...

class ShowHistoryRequest(_message.Message):
    __slots__ = ["groupName"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    def __init__(self, groupName: _Optional[str] = ...) -> None: ...

class ShowHistoryResponse(_message.Message):
    __slots__ = ["messages"]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[HistoryMessage]
    def __init__(self, messages: _Optional[_Iterable[_Union[HistoryMessage, _Mapping]]] = ...) -> None: ...
