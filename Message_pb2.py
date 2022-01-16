# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Message.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Message.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\rMessage.proto\"\x06\n\x04Null\")\n\x0fGuiInputRequest\x12\x16\n\x0eUserPreference\x18\x01 \x01(\x05\"\'\n\tCPRequest\x12\x1a\n\x12\x63ontrol_parameters\x18\x01 \x03(\x02\"\"\n\x08URequest\x12\x16\n\x0eupdate_request\x18\x01 \x01(\t26\n\x0cGuiOptimizer\x12&\n\tUserInput\x12\x10.GuiInputRequest\x1a\x05.Null\"\x00\x32K\n\x19GenerateControlParameters\x12.\n\x17\x43ontrolParameterRequest\x12\n.CPRequest\x1a\x05.Null\"\x00\x32\x39\n\x12UpdateCmaesRequest\x12#\n\rUpdateRequest\x12\t.URequest\x1a\x05.Null\"\x00\x62\x06proto3'
)




_NULL = _descriptor.Descriptor(
  name='Null',
  full_name='Null',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=17,
  serialized_end=23,
)


_GUIINPUTREQUEST = _descriptor.Descriptor(
  name='GuiInputRequest',
  full_name='GuiInputRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='UserPreference', full_name='GuiInputRequest.UserPreference', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=25,
  serialized_end=66,
)


_CPREQUEST = _descriptor.Descriptor(
  name='CPRequest',
  full_name='CPRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='control_parameters', full_name='CPRequest.control_parameters', index=0,
      number=1, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=68,
  serialized_end=107,
)


_UREQUEST = _descriptor.Descriptor(
  name='URequest',
  full_name='URequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='update_request', full_name='URequest.update_request', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=109,
  serialized_end=143,
)

DESCRIPTOR.message_types_by_name['Null'] = _NULL
DESCRIPTOR.message_types_by_name['GuiInputRequest'] = _GUIINPUTREQUEST
DESCRIPTOR.message_types_by_name['CPRequest'] = _CPREQUEST
DESCRIPTOR.message_types_by_name['URequest'] = _UREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Null = _reflection.GeneratedProtocolMessageType('Null', (_message.Message,), {
  'DESCRIPTOR' : _NULL,
  '__module__' : 'Message_pb2'
  # @@protoc_insertion_point(class_scope:Null)
  })
_sym_db.RegisterMessage(Null)

GuiInputRequest = _reflection.GeneratedProtocolMessageType('GuiInputRequest', (_message.Message,), {
  'DESCRIPTOR' : _GUIINPUTREQUEST,
  '__module__' : 'Message_pb2'
  # @@protoc_insertion_point(class_scope:GuiInputRequest)
  })
_sym_db.RegisterMessage(GuiInputRequest)

CPRequest = _reflection.GeneratedProtocolMessageType('CPRequest', (_message.Message,), {
  'DESCRIPTOR' : _CPREQUEST,
  '__module__' : 'Message_pb2'
  # @@protoc_insertion_point(class_scope:CPRequest)
  })
_sym_db.RegisterMessage(CPRequest)

URequest = _reflection.GeneratedProtocolMessageType('URequest', (_message.Message,), {
  'DESCRIPTOR' : _UREQUEST,
  '__module__' : 'Message_pb2'
  # @@protoc_insertion_point(class_scope:URequest)
  })
_sym_db.RegisterMessage(URequest)



_GUIOPTIMIZER = _descriptor.ServiceDescriptor(
  name='GuiOptimizer',
  full_name='GuiOptimizer',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=145,
  serialized_end=199,
  methods=[
  _descriptor.MethodDescriptor(
    name='UserInput',
    full_name='GuiOptimizer.UserInput',
    index=0,
    containing_service=None,
    input_type=_GUIINPUTREQUEST,
    output_type=_NULL,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_GUIOPTIMIZER)

DESCRIPTOR.services_by_name['GuiOptimizer'] = _GUIOPTIMIZER


_GENERATECONTROLPARAMETERS = _descriptor.ServiceDescriptor(
  name='GenerateControlParameters',
  full_name='GenerateControlParameters',
  file=DESCRIPTOR,
  index=1,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=201,
  serialized_end=276,
  methods=[
  _descriptor.MethodDescriptor(
    name='ControlParameterRequest',
    full_name='GenerateControlParameters.ControlParameterRequest',
    index=0,
    containing_service=None,
    input_type=_CPREQUEST,
    output_type=_NULL,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_GENERATECONTROLPARAMETERS)

DESCRIPTOR.services_by_name['GenerateControlParameters'] = _GENERATECONTROLPARAMETERS


_UPDATECMAESREQUEST = _descriptor.ServiceDescriptor(
  name='UpdateCmaesRequest',
  full_name='UpdateCmaesRequest',
  file=DESCRIPTOR,
  index=2,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=278,
  serialized_end=335,
  methods=[
  _descriptor.MethodDescriptor(
    name='UpdateRequest',
    full_name='UpdateCmaesRequest.UpdateRequest',
    index=0,
    containing_service=None,
    input_type=_UREQUEST,
    output_type=_NULL,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_UPDATECMAESREQUEST)

DESCRIPTOR.services_by_name['UpdateCmaesRequest'] = _UPDATECMAESREQUEST

# @@protoc_insertion_point(module_scope)
