from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AppendEntriesRequest(_message.Message):
    __slots__ = ["entry", "leaderCommit", "leaderId", "prevLogIndex", "prevLogTerm", "term"]
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    LEADERCOMMIT_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    PREVLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    PREVLOGTERM_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    entry: Entry
    leaderCommit: int
    leaderId: int
    prevLogIndex: int
    prevLogTerm: int
    term: int
    def __init__(self, term: _Optional[int] = ..., leaderId: _Optional[int] = ..., prevLogIndex: _Optional[int] = ..., prevLogTerm: _Optional[int] = ..., entry: _Optional[_Union[Entry, _Mapping]] = ..., leaderCommit: _Optional[int] = ...) -> None: ...

class AppendEntriesResponse(_message.Message):
    __slots__ = ["success", "term"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    success: bool
    term: int
    def __init__(self, term: _Optional[int] = ..., success: bool = ...) -> None: ...

class ChatInput(_message.Message):
    __slots__ = ["groupName", "message", "messageId", "type", "userName", "uuid"]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    groupName: str
    message: str
    messageId: int
    type: int
    userName: str
    uuid: str
    def __init__(self, userName: _Optional[str] = ..., groupName: _Optional[str] = ..., type: _Optional[int] = ..., message: _Optional[str] = ..., messageId: _Optional[int] = ..., uuid: _Optional[str] = ...) -> None: ...

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

class ClientAppendRequest(_message.Message):
    __slots__ = ["decree"]
    DECREE_FIELD_NUMBER: _ClassVar[int]
    decree: str
    def __init__(self, decree: _Optional[str] = ...) -> None: ...

class ClientAppendResponse(_message.Message):
    __slots__ = ["index", "leader", "rc"]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    LEADER_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    index: int
    leader: int
    rc: int
    def __init__(self, rc: _Optional[int] = ..., leader: _Optional[int] = ..., index: _Optional[int] = ...) -> None: ...

class ClientRequestIndexRequest(_message.Message):
    __slots__ = ["index"]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    index: int
    def __init__(self, index: _Optional[int] = ...) -> None: ...

class ClientRequestIndexResponse(_message.Message):
    __slots__ = ["decree", "index", "leader", "rc"]
    DECREE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    LEADER_FIELD_NUMBER: _ClassVar[int]
    RC_FIELD_NUMBER: _ClassVar[int]
    decree: str
    index: int
    leader: int
    rc: int
    def __init__(self, rc: _Optional[int] = ..., leader: _Optional[int] = ..., index: _Optional[int] = ..., decree: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Entry(_message.Message):
    __slots__ = ["decree", "index", "term"]
    DECREE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    decree: str
    index: int
    term: int
    def __init__(self, term: _Optional[int] = ..., index: _Optional[int] = ..., decree: _Optional[str] = ...) -> None: ...

class RequestVoteRequest(_message.Message):
    __slots__ = ["cadidateId", "lastLogIndex", "lastLogTerm", "term"]
    CADIDATEID_FIELD_NUMBER: _ClassVar[int]
    LASTLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    LASTLOGTERM_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    cadidateId: int
    lastLogIndex: int
    lastLogTerm: int
    term: int
    def __init__(self, term: _Optional[int] = ..., cadidateId: _Optional[int] = ..., lastLogIndex: _Optional[int] = ..., lastLogTerm: _Optional[int] = ...) -> None: ...

class RequestVoteResponse(_message.Message):
    __slots__ = ["term", "voteGranted"]
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTEGRANTED_FIELD_NUMBER: _ClassVar[int]
    term: int
    voteGranted: bool
    def __init__(self, term: _Optional[int] = ..., voteGranted: bool = ...) -> None: ...
