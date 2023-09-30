# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generated python gRPC interfaces."""



from google.protobuf import any_pb2
from google.protobuf import empty_pb2
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
from google.protobuf.message import Message
from pandora import host_pb2
from typing import Optional
from typing import Union
from typing_extensions import Literal
from typing_extensions import TypedDict

class CommandRejectReason(int, EnumTypeWrapper):
  pass

COMMAND_NOT_UNDERSTOOD: CommandRejectReason
SIGNAL_MTU_EXCEEDED: CommandRejectReason
INVALID_CID_IN_REQUEST: CommandRejectReason


class Channel(Message):
  cookie: any_pb2.Any

  def __init__(self, cookie: any_pb2.Any = any_pb2.Any()) -> None: ...

class ConnectionOrientedChannelRequest(Message):
  psm: int
  mtu: int

  def __init__(self, psm: int = 0, mtu: int = 0) -> None: ...

class CreditBasedChannelRequest(Message):
  spsm: int
  mtu: int
  mps: int
  initial_credit: int

  def __init__(self, spsm: int = 0, mtu: int = 0, mps: int = 0, initial_credit: int = 0) -> None: ...

class FixedChannelRequest(Message):
  cid: int

  def __init__(self, cid: int = 0) -> None: ...

class ConnectRequest(Message):
  connection: host_pb2.Connection
  fixed: Optional[FixedChannelRequest]
  basic: Optional[ConnectionOrientedChannelRequest]
  le_credit_based: Optional[CreditBasedChannelRequest]
  enhanced_credit_based: Optional[CreditBasedChannelRequest]

  def __init__(self, connection: host_pb2.Connection = host_pb2.Connection(), fixed: Optional[FixedChannelRequest] = None, basic: Optional[ConnectionOrientedChannelRequest] = None, le_credit_based: Optional[CreditBasedChannelRequest] = None, enhanced_credit_based: Optional[CreditBasedChannelRequest] = None) -> None: ...

  @property
  def type(self) -> Union[CreditBasedChannelRequest, FixedChannelRequest, ConnectionOrientedChannelRequest, None]: ...
  def type_variant(self) -> Union[Literal['fixed'], Literal['basic'], Literal['le_credit_based'], Literal['enhanced_credit_based'], None]: ...
  def type_asdict(self) -> ConnectRequest_type_dict: ...

class ConnectRequest_type_dict(TypedDict, total=False):
  fixed: FixedChannelRequest
  basic: ConnectionOrientedChannelRequest
  le_credit_based: CreditBasedChannelRequest
  enhanced_credit_based: CreditBasedChannelRequest

class ConnectResponse(Message):
  error: Optional[CommandRejectReason]
  channel: Optional[Channel]

  def __init__(self, error: Optional[CommandRejectReason] = None, channel: Optional[Channel] = None) -> None: ...

  @property
  def result(self) -> Union[Channel, None, CommandRejectReason]: ...
  def result_variant(self) -> Union[Literal['error'], Literal['channel'], None]: ...
  def result_asdict(self) -> ConnectResponse_result_dict: ...

class ConnectResponse_result_dict(TypedDict, total=False):
  error: CommandRejectReason
  channel: Channel

class OnConnectionRequest(Message):
  connection: host_pb2.Connection
  fixed: Optional[FixedChannelRequest]
  basic: Optional[ConnectionOrientedChannelRequest]
  le_credit_based: Optional[CreditBasedChannelRequest]
  enhanced_credit_based: Optional[CreditBasedChannelRequest]

  def __init__(self, connection: host_pb2.Connection = host_pb2.Connection(), fixed: Optional[FixedChannelRequest] = None, basic: Optional[ConnectionOrientedChannelRequest] = None, le_credit_based: Optional[CreditBasedChannelRequest] = None, enhanced_credit_based: Optional[CreditBasedChannelRequest] = None) -> None: ...

  @property
  def type(self) -> Union[CreditBasedChannelRequest, FixedChannelRequest, ConnectionOrientedChannelRequest, None]: ...
  def type_variant(self) -> Union[Literal['fixed'], Literal['basic'], Literal['le_credit_based'], Literal['enhanced_credit_based'], None]: ...
  def type_asdict(self) -> OnConnectionRequest_type_dict: ...

class OnConnectionRequest_type_dict(TypedDict, total=False):
  fixed: FixedChannelRequest
  basic: ConnectionOrientedChannelRequest
  le_credit_based: CreditBasedChannelRequest
  enhanced_credit_based: CreditBasedChannelRequest

class OnConnectionResponse(Message):
  error: Optional[CommandRejectReason]
  channel: Optional[Channel]

  def __init__(self, error: Optional[CommandRejectReason] = None, channel: Optional[Channel] = None) -> None: ...

  @property
  def result(self) -> Union[Channel, None, CommandRejectReason]: ...
  def result_variant(self) -> Union[Literal['error'], Literal['channel'], None]: ...
  def result_asdict(self) -> OnConnectionResponse_result_dict: ...

class OnConnectionResponse_result_dict(TypedDict, total=False):
  error: CommandRejectReason
  channel: Channel

class DisconnectRequest(Message):
  channel: Channel

  def __init__(self, channel: Channel = Channel()) -> None: ...

class DisconnectResponse(Message):
  error: Optional[CommandRejectReason]
  success: Optional[empty_pb2.Empty]

  def __init__(self, error: Optional[CommandRejectReason] = None, success: Optional[empty_pb2.Empty] = None) -> None: ...

  @property
  def result(self) -> Union[empty_pb2.Empty, None, CommandRejectReason]: ...
  def result_variant(self) -> Union[Literal['error'], Literal['success'], None]: ...
  def result_asdict(self) -> DisconnectResponse_result_dict: ...

class DisconnectResponse_result_dict(TypedDict, total=False):
  error: CommandRejectReason
  success: empty_pb2.Empty

class WaitDisconnectionRequest(Message):
  channel: Channel

  def __init__(self, channel: Channel = Channel()) -> None: ...

class WaitDisconnectionResponse(Message):
  error: Optional[CommandRejectReason]
  success: Optional[empty_pb2.Empty]

  def __init__(self, error: Optional[CommandRejectReason] = None, success: Optional[empty_pb2.Empty] = None) -> None: ...

  @property
  def result(self) -> Union[empty_pb2.Empty, None, CommandRejectReason]: ...
  def result_variant(self) -> Union[Literal['error'], Literal['success'], None]: ...
  def result_asdict(self) -> WaitDisconnectionResponse_result_dict: ...

class WaitDisconnectionResponse_result_dict(TypedDict, total=False):
  error: CommandRejectReason
  success: empty_pb2.Empty

class ReceiveRequest(Message):
  channel: Channel

  def __init__(self, channel: Channel = Channel()) -> None: ...

class ReceiveResponse(Message):
  data: bytes

  def __init__(self, data: bytes = b'') -> None: ...

class SendRequest(Message):
  channel: Channel
  data: bytes

  def __init__(self, channel: Channel = Channel(), data: bytes = b'') -> None: ...

class SendResponse(Message):
  error: Optional[CommandRejectReason]
  success: Optional[empty_pb2.Empty]

  def __init__(self, error: Optional[CommandRejectReason] = None, success: Optional[empty_pb2.Empty] = None) -> None: ...

  @property
  def result(self) -> Union[empty_pb2.Empty, None, CommandRejectReason]: ...
  def result_variant(self) -> Union[Literal['error'], Literal['success'], None]: ...
  def result_asdict(self) -> SendResponse_result_dict: ...

class SendResponse_result_dict(TypedDict, total=False):
  error: CommandRejectReason
  success: empty_pb2.Empty

