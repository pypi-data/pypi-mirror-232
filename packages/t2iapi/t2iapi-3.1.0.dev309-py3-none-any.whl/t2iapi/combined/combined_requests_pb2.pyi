from t2iapi.context import types_pb2 as _types_pb2
from t2iapi.operation import types_pb2 as _types_pb2_1
from t2iapi.activation_state import types_pb2 as _types_pb2_1_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateContextStateWithAssociationAndSetOperatingModeRequest(_message.Message):
    __slots__ = ["context_descriptor_handle", "context_association", "operation_descriptor_handle", "operating_mode"]
    CONTEXT_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    context_descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    operation_descriptor_handle: str
    operating_mode: _types_pb2_1.OperatingMode
    def __init__(self, context_descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ..., operation_descriptor_handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2_1.OperatingMode, str]] = ...) -> None: ...

class SetComponentActivationAndSetOperatingModeRequest(_message.Message):
    __slots__ = ["component_metric_descriptor_handle", "component_activation", "operation_descriptor_handle", "operating_mode"]
    COMPONENT_METRIC_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    component_metric_descriptor_handle: str
    component_activation: _types_pb2_1_1.ComponentActivation
    operation_descriptor_handle: str
    operating_mode: _types_pb2_1.OperatingMode
    def __init__(self, component_metric_descriptor_handle: _Optional[str] = ..., component_activation: _Optional[_Union[_types_pb2_1_1.ComponentActivation, str]] = ..., operation_descriptor_handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2_1.OperatingMode, str]] = ...) -> None: ...

class SetAlertActivationAndSetOperatingModeRequest(_message.Message):
    __slots__ = ["alert_descriptor_handle", "alert_activation", "operation_descriptor_handle", "operating_mode"]
    ALERT_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    ALERT_ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    alert_descriptor_handle: str
    alert_activation: _types_pb2_1_1.AlertActivation
    operation_descriptor_handle: str
    operating_mode: _types_pb2_1.OperatingMode
    def __init__(self, alert_descriptor_handle: _Optional[str] = ..., alert_activation: _Optional[_Union[_types_pb2_1_1.AlertActivation, str]] = ..., operation_descriptor_handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2_1.OperatingMode, str]] = ...) -> None: ...
