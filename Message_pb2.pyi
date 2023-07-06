from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
DISLIKE: EnumPreference
LIKE: EnumPreference
SKIP: EnumPreference

class ControllerPing(_message.Message):
    __slots__ = ["ankle_angle", "ankle_angular_velocity", "exo_side"]
    ANKLE_ANGLE_FIELD_NUMBER: _ClassVar[int]
    ANKLE_ANGULAR_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    EXO_SIDE_FIELD_NUMBER: _ClassVar[int]
    ankle_angle: _containers.RepeatedScalarFieldContainer[float]
    ankle_angular_velocity: _containers.RepeatedScalarFieldContainer[float]
    exo_side: float
    def __init__(self, ankle_angle: _Optional[_Iterable[float]] = ..., ankle_angular_velocity: _Optional[_Iterable[float]] = ..., exo_side: _Optional[float] = ...) -> None: ...

class GuiInput(_message.Message):
    __slots__ = ["enumpreference"]
    ENUMPREFERENCE_FIELD_NUMBER: _ClassVar[int]
    enumpreference: EnumPreference
    def __init__(self, enumpreference: _Optional[_Union[EnumPreference, str]] = ...) -> None: ...

class Null(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class PreferenceFlag(_message.Message):
    __slots__ = ["PFlag"]
    PFLAG_FIELD_NUMBER: _ClassVar[int]
    PFlag: bool
    def __init__(self, PFlag: bool = ...) -> None: ...

class SendingAction(_message.Message):
    __slots__ = ["action_torque_profile"]
    ACTION_TORQUE_PROFILE_FIELD_NUMBER: _ClassVar[int]
    action_torque_profile: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, action_torque_profile: _Optional[_Iterable[float]] = ...) -> None: ...

class EnumPreference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
