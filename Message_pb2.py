# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Message.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rMessage.proto\"\x06\n\x04Null\"3\n\x08GuiInput\x12\'\n\x0e\x65numpreference\x18\x01 \x01(\x0e\x32\x0f.EnumPreference\"\x1f\n\x0ePreferenceFlag\x12\r\n\x05PFlag\x18\x01 \x01(\x08\"\x90\x01\n\x0e\x43ontrollerPing\x12\x18\n\x10\x61nkle_angle_LEFT\x18\x01 \x03(\x02\x12#\n\x1b\x61nkle_angular_velocity_LEFT\x18\x02 \x03(\x02\x12\x19\n\x11\x61nkle_angle_RIGHT\x18\x03 \x03(\x02\x12$\n\x1c\x61nkle_angular_velocity_RIGHT\x18\x04 \x03(\x02\".\n\rSendingAction\x12\x1d\n\x15\x61\x63tion_torque_profile\x18\x01 \x03(\x02*:\n\x0e\x45numPreference\x12\x08\n\x04SKIP\x10\x00\x12\x08\n\x04LIKE\x10\x01\x12\x14\n\x07\x44ISLIKE\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x32/\n\x0cGuiAlgorithm\x12\x1f\n\tUserInput\x12\t.GuiInput\x1a\x05.Null\"\x00\x32G\n\x13\x41skingforPreference\x12\x30\n\x14PreferenceUpdateStep\x12\x0f.PreferenceFlag\x1a\x05.Null\"\x00\x32\x44\n\x13\x43ontrollerAlgorithm\x12-\n\x11\x43ontrollerMessage\x12\x0f.ControllerPing\x1a\x05.Null\"\x00\x32\x37\n\x0b\x41\x63tionState\x12(\n\rActionMessage\x12\x0e.SendingAction\x1a\x05.Null\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Message_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ENUMPREFERENCE._serialized_start=306
  _ENUMPREFERENCE._serialized_end=364
  _NULL._serialized_start=17
  _NULL._serialized_end=23
  _GUIINPUT._serialized_start=25
  _GUIINPUT._serialized_end=76
  _PREFERENCEFLAG._serialized_start=78
  _PREFERENCEFLAG._serialized_end=109
  _CONTROLLERPING._serialized_start=112
  _CONTROLLERPING._serialized_end=256
  _SENDINGACTION._serialized_start=258
  _SENDINGACTION._serialized_end=304
  _GUIALGORITHM._serialized_start=366
  _GUIALGORITHM._serialized_end=413
  _ASKINGFORPREFERENCE._serialized_start=415
  _ASKINGFORPREFERENCE._serialized_end=486
  _CONTROLLERALGORITHM._serialized_start=488
  _CONTROLLERALGORITHM._serialized_end=556
  _ACTIONSTATE._serialized_start=558
  _ACTIONSTATE._serialized_end=613
# @@protoc_insertion_point(module_scope)