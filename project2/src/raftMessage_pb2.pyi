from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AppendEntries(_message.Message):
    __slots__ = ["entries", "leaderCommit", "leaderId", "prevLogIndex", "prevLogTerm", "term"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    LEADERCOMMIT_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    PREVLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    PREVLOGTERM_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    leaderCommit: int
    leaderId: str
    prevLogIndex: int
    prevLogTerm: int
    term: int
    def __init__(self, term: _Optional[int] = ..., leaderId: _Optional[str] = ..., prevLogIndex: _Optional[int] = ..., prevLogTerm: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ..., leaderCommit: _Optional[int] = ...) -> None: ...

class AppendEntriesReply(_message.Message):
    __slots__ = ["id", "success", "term"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    id: int
    success: bool
    term: int
    def __init__(self, id: _Optional[int] = ..., term: _Optional[int] = ..., success: bool = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ["command", "term"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    command: str
    term: int
    def __init__(self, term: _Optional[int] = ..., command: _Optional[str] = ...) -> None: ...

class RequestVote(_message.Message):
    __slots__ = ["candidateId", "lastLogIndex", "lastLogTerm", "term"]
    CANDIDATEID_FIELD_NUMBER: _ClassVar[int]
    LASTLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    LASTLOGTERM_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    candidateId: str
    lastLogIndex: int
    lastLogTerm: int
    term: int
    def __init__(self, term: _Optional[int] = ..., candidateId: _Optional[str] = ..., lastLogIndex: _Optional[int] = ..., lastLogTerm: _Optional[int] = ...) -> None: ...

class RequestVoteReply(_message.Message):
    __slots__ = ["id", "term", "voteGranted"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTEGRANTED_FIELD_NUMBER: _ClassVar[int]
    id: int
    term: int
    voteGranted: bool
    def __init__(self, id: _Optional[int] = ..., term: _Optional[int] = ..., voteGranted: bool = ...) -> None: ...
