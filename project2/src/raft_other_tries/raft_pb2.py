# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\x12\x04raft\"p\n\tChatInput\x12\x10\n\x08userName\x18\x01 \x01(\t\x12\x11\n\tgroupName\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\x05\x12\x0f\n\x07message\x18\x04 \x01(\t\x12\x11\n\tmessageId\x18\x05 \x01(\x05\x12\x0c\n\x04uuid\x18\x06 \x01(\t\"O\n\nChatOutput\x12\x0e\n\x06status\x18\x01 \x01(\t\x12#\n\x08messages\x18\x02 \x03(\x0b\x32\x11.raft.ChatMessage\x12\x0c\n\x04user\x18\x03 \x03(\t\"O\n\x0b\x43hatMessage\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04user\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\x12\x15\n\rnumberOfLikes\x18\x04 \x01(\x05\"\x07\n\x05\x45mpty\"a\n\x12RequestVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x12\n\ncadidateId\x18\x02 \x01(\r\x12\x14\n\x0clastLogIndex\x18\x03 \x01(\x04\x12\x13\n\x0blastLogTerm\x18\x04 \x01(\x04\"8\n\x13RequestVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x13\n\x0bvoteGranted\x18\x02 \x01(\x08\"\x93\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x10\n\x08leaderId\x18\x02 \x01(\r\x12\x14\n\x0cprevLogIndex\x18\x03 \x01(\x04\x12\x13\n\x0bprevLogTerm\x18\x04 \x01(\x04\x12\x1a\n\x05\x65ntry\x18\x05 \x01(\x0b\x32\x0b.raft.Entry\x12\x14\n\x0cleaderCommit\x18\x06 \x01(\x04\"6\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x0f\n\x07success\x18\x02 \x01(\x08\"4\n\x05\x45ntry\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\r\n\x05index\x18\x02 \x01(\x04\x12\x0e\n\x06\x64\x65\x63ree\x18\x03 \x01(\t\"%\n\x13\x43lientAppendRequest\x12\x0e\n\x06\x64\x65\x63ree\x18\x01 \x01(\t\"A\n\x14\x43lientAppendResponse\x12\n\n\x02rc\x18\x01 \x01(\r\x12\x0e\n\x06leader\x18\x02 \x01(\x04\x12\r\n\x05index\x18\x03 \x01(\x04\"*\n\x19\x43lientRequestIndexRequest\x12\r\n\x05index\x18\x01 \x01(\x04\"W\n\x1a\x43lientRequestIndexResponse\x12\n\n\x02rc\x18\x01 \x01(\r\x12\x0e\n\x06leader\x18\x02 \x01(\x04\x12\r\n\x05index\x18\x03 \x01(\x04\x12\x0e\n\x06\x64\x65\x63ree\x18\x04 \x01(\t2\xa6\x03\n\nRaftServer\x12\x33\n\x0c\x63hatFunction\x12\x0f.raft.ChatInput\x1a\x10.raft.ChatOutput\"\x00\x12\x35\n\x0bgetMessages\x12\x0f.raft.ChatInput\x1a\x11.raft.ChatMessage\"\x00\x30\x01\x12\x42\n\x0bRequestVote\x12\x18.raft.RequestVoteRequest\x1a\x19.raft.RequestVoteResponse\x12H\n\rAppendEntries\x12\x1a.raft.AppendEntriesRequest\x1a\x1b.raft.AppendEntriesResponse\x12\x45\n\x0c\x43lientAppend\x12\x19.raft.ClientAppendRequest\x1a\x1a.raft.ClientAppendResponse\x12W\n\x12\x43lientRequestIndex\x12\x1f.raft.ClientRequestIndexRequest\x1a .raft.ClientRequestIndexResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CHATINPUT._serialized_start=20
  _CHATINPUT._serialized_end=132
  _CHATOUTPUT._serialized_start=134
  _CHATOUTPUT._serialized_end=213
  _CHATMESSAGE._serialized_start=215
  _CHATMESSAGE._serialized_end=294
  _EMPTY._serialized_start=296
  _EMPTY._serialized_end=303
  _REQUESTVOTEREQUEST._serialized_start=305
  _REQUESTVOTEREQUEST._serialized_end=402
  _REQUESTVOTERESPONSE._serialized_start=404
  _REQUESTVOTERESPONSE._serialized_end=460
  _APPENDENTRIESREQUEST._serialized_start=463
  _APPENDENTRIESREQUEST._serialized_end=610
  _APPENDENTRIESRESPONSE._serialized_start=612
  _APPENDENTRIESRESPONSE._serialized_end=666
  _ENTRY._serialized_start=668
  _ENTRY._serialized_end=720
  _CLIENTAPPENDREQUEST._serialized_start=722
  _CLIENTAPPENDREQUEST._serialized_end=759
  _CLIENTAPPENDRESPONSE._serialized_start=761
  _CLIENTAPPENDRESPONSE._serialized_end=826
  _CLIENTREQUESTINDEXREQUEST._serialized_start=828
  _CLIENTREQUESTINDEXREQUEST._serialized_end=870
  _CLIENTREQUESTINDEXRESPONSE._serialized_start=872
  _CLIENTREQUESTINDEXRESPONSE._serialized_end=959
  _RAFTSERVER._serialized_start=962
  _RAFTSERVER._serialized_end=1384
# @@protoc_insertion_point(module_scope)
