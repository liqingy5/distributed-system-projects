# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: groupChat.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fgroupChat.proto\x12\tgroupChat\"*\n\tChatInput\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t\"F\n\nChatOutput\x12\x0e\n\x06status\x18\x01 \x01(\t\x12(\n\x08messages\x18\x02 \x03(\x0b\x32\x16.groupChat.ChatMessage\"A\n\x0b\x43hatMessage\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\x12\x15\n\rnumberOfLikes\x18\x03 \x01(\x05\x32O\n\nChatServer\x12\x41\n\x0c\x63hatFunction\x12\x14.groupChat.ChatInput\x1a\x15.groupChat.ChatOutput\"\x00(\x01\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'groupChat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CHATINPUT._serialized_start=30
  _CHATINPUT._serialized_end=72
  _CHATOUTPUT._serialized_start=74
  _CHATOUTPUT._serialized_end=144
  _CHATMESSAGE._serialized_start=146
  _CHATMESSAGE._serialized_end=211
  _CHATSERVER._serialized_start=213
  _CHATSERVER._serialized_end=292
# @@protoc_insertion_point(module_scope)