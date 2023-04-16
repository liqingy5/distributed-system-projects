from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChatInput(_message.Message):
    __slots__ = ["groupName", "message", "messageId", "serverId", "type", "userName", "uuid"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SERVERID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    message: str
    messageId: int
    serverId: int
    type: int
    userName: str
    uuid: str
    def __init__(self, userName: _Optional[str] = ..., groupName: _Optional[str] = ..., type: _Optional[int] = ..., message: _Optional[str] = ..., messageId: _Optional[int] = ..., uuid: _Optional[str] = ..., serverId: _Optional[int] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ["content", "id", "numberOfLikes", "user"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFLIKES_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    content: str
    id: int
    numberOfLikes: int
    user: str
    def __init__(self, id: _Optional[int] = ..., user: _Optional[str] = ..., content: _Optional[str] = ..., numberOfLikes: _Optional[int] = ...) -> None: ...

class ChatOutput(_message.Message):
    __slots__ = ["messages", "status", "user"]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    status: str
    user: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[str] = ..., messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., user: _Optional[_Iterable[str]] = ...) -> None: ...

class ChatServerRequest(_message.Message):
    __slots__ = ["mode", "request", "server_id", "vector"]
    MODE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    mode: int
    request: ChatInput
    server_id: int
    vector: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, vector: _Optional[_Iterable[int]] = ..., request: _Optional[_Union[ChatInput, _Mapping]] = ..., server_id: _Optional[int] = ..., mode: _Optional[int] = ...) -> None: ...

class ChatServerResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ChatServerSyncRequest(_message.Message):
    __slots__ = ["server_id", "vector"]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    vector: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, vector: _Optional[_Iterable[int]] = ..., server_id: _Optional[int] = ...) -> None: ...

class ChatServerSyncResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
