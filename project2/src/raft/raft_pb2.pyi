from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddServerRequest(_message.Message):
    __slots__ = ["server_address", "server_id"]
    SERVER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_address: str
    server_id: int
    def __init__(self, server_id: _Optional[int] = ..., server_address: _Optional[str] = ...) -> None: ...

class AddServerResponse(_message.Message):
    __slots__ = ["error", "result"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    error: str
    result: str
    def __init__(self, result: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class AppendEntriesRequest(_message.Message):
    __slots__ = ["entries", "leaderCommit", "leaderId", "prevLogIndex", "prevLogTerm", "term"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    LEADERCOMMIT_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    PREVLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    PREVLOGTERM_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    leaderCommit: int
    leaderId: int
    prevLogIndex: int
    prevLogTerm: int
    term: int
    def __init__(self, term: _Optional[int] = ..., leaderId: _Optional[int] = ..., prevLogIndex: _Optional[int] = ..., prevLogTerm: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ..., leaderCommit: _Optional[int] = ...) -> None: ...

class AppendEntriesResponse(_message.Message):
    __slots__ = ["id", "success", "term"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    id: int
    success: bool
    term: int
    def __init__(self, id: _Optional[int] = ..., term: _Optional[int] = ..., success: bool = ...) -> None: ...

class ClientAppendRequest(_message.Message):
    __slots__ = ["command", "value"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: int
    value: str
    def __init__(self, command: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...

class ClientAppendResponse(_message.Message):
    __slots__ = ["leaderHint", "response", "status"]
    LEADERHINT_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    leaderHint: int
    response: str
    status: int
    def __init__(self, status: _Optional[int] = ..., response: _Optional[str] = ..., leaderHint: _Optional[int] = ...) -> None: ...

class ClientQueryRequest(_message.Message):
    __slots__ = ["queryCommand"]
    QUERYCOMMAND_FIELD_NUMBER: _ClassVar[int]
    queryCommand: int
    def __init__(self, queryCommand: _Optional[int] = ...) -> None: ...

class ClientQueryResponse(_message.Message):
    __slots__ = ["leaderHint", "response", "status"]
    LEADERHINT_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    leaderHint: int
    response: str
    status: int
    def __init__(self, status: _Optional[int] = ..., response: _Optional[str] = ..., leaderHint: _Optional[int] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ["command", "term", "value"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: int
    term: int
    value: str
    def __init__(self, term: _Optional[int] = ..., command: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...

class RegisterClientRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class RegisterClientResponse(_message.Message):
    __slots__ = ["clientId", "leaderHint", "status"]
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    LEADERHINT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    clientId: int
    leaderHint: int
    status: int
    def __init__(self, status: _Optional[int] = ..., clientId: _Optional[int] = ..., leaderHint: _Optional[int] = ...) -> None: ...

class RemoveServerRequest(_message.Message):
    __slots__ = ["server_id"]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class RemoveServerResponse(_message.Message):
    __slots__ = ["error", "result"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    error: str
    result: str
    def __init__(self, result: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class VoteRequest(_message.Message):
    __slots__ = ["candidateId", "lastLogIndex", "lastLogTerm", "term"]
    CANDIDATEID_FIELD_NUMBER: _ClassVar[int]
    LASTLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    LASTLOGTERM_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    candidateId: int
    lastLogIndex: int
    lastLogTerm: int
    term: int
    def __init__(self, term: _Optional[int] = ..., candidateId: _Optional[int] = ..., lastLogIndex: _Optional[int] = ..., lastLogTerm: _Optional[int] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ["id", "term", "voteGranted"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTEGRANTED_FIELD_NUMBER: _ClassVar[int]
    id: int
    term: int
    voteGranted: bool
    def __init__(self, id: _Optional[int] = ..., term: _Optional[int] = ..., voteGranted: bool = ...) -> None: ...
