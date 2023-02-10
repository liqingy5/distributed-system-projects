from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChatInput(_message.Message):
    __slots__ = ["message", "type"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    message: str
    type: int
    def __init__(self, type: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ["content", "id", "numberOfLikes"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFLIKES_FIELD_NUMBER: _ClassVar[int]
    content: str
    id: int
    numberOfLikes: int
    def __init__(self, id: _Optional[int] = ..., content: _Optional[str] = ..., numberOfLikes: _Optional[int] = ...) -> None: ...

class ChatOutput(_message.Message):
    __slots__ = ["messages", "status"]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    status: str
    def __init__(self, status: _Optional[str] = ..., messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ...) -> None: ...
