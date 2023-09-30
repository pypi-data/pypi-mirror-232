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



from ._utils import AioStream as Stream
from pandora import host_pb2
from pandora import l2cap_pb2
from typing import AsyncGenerator
from typing import Awaitable
from typing import Optional
import grpc
import grpc.aio

class L2CAP:
    channel: grpc.aio.Channel

    def __init__(self, channel: grpc.aio.Channel) -> None:
        self.channel = channel

    def Connect(self, connection: host_pb2.Connection = host_pb2.Connection(), fixed: Optional[l2cap_pb2.FixedChannelRequest] = None, basic: Optional[l2cap_pb2.ConnectionOrientedChannelRequest] = None, le_credit_based: Optional[l2cap_pb2.CreditBasedChannelRequest] = None, enhanced_credit_based: Optional[l2cap_pb2.CreditBasedChannelRequest] = None, wait_for_ready: Optional[bool] = None, timeout: Optional[float] = None) -> Awaitable[l2cap_pb2.ConnectResponse]:
        return self.channel.unary_unary(  # type: ignore
            '/pandora.l2cap.L2CAP/Connect',
            request_serializer=l2cap_pb2.ConnectRequest.SerializeToString,  # type: ignore
            response_deserializer=l2cap_pb2.ConnectResponse.FromString  # type: ignore
        )(l2cap_pb2.ConnectRequest(connection=connection, fixed=fixed, basic=basic, le_credit_based=le_credit_based, enhanced_credit_based=enhanced_credit_based), wait_for_ready=wait_for_ready, timeout=timeout)  # type: ignore

    def OnConnection(self, connection: host_pb2.Connection = host_pb2.Connection(), fixed: Optional[l2cap_pb2.FixedChannelRequest] = None, basic: Optional[l2cap_pb2.ConnectionOrientedChannelRequest] = None, le_credit_based: Optional[l2cap_pb2.CreditBasedChannelRequest] = None, enhanced_credit_based: Optional[l2cap_pb2.CreditBasedChannelRequest] = None, wait_for_ready: Optional[bool] = None, timeout: Optional[float] = None) -> Stream[l2cap_pb2.OnConnectionResponse]:
        return self.channel.unary_stream(  # type: ignore
            '/pandora.l2cap.L2CAP/OnConnection',
            request_serializer=l2cap_pb2.OnConnectionRequest.SerializeToString,  # type: ignore
            response_deserializer=l2cap_pb2.OnConnectionResponse.FromString  # type: ignore
        )(l2cap_pb2.OnConnectionRequest(connection=connection, fixed=fixed, basic=basic, le_credit_based=le_credit_based, enhanced_credit_based=enhanced_credit_based), wait_for_ready=wait_for_ready, timeout=timeout)  # type: ignore

    def Disconnect(self, channel: l2cap_pb2.Channel = l2cap_pb2.Channel(), wait_for_ready: Optional[bool] = None, timeout: Optional[float] = None) -> Awaitable[l2cap_pb2.DisconnectResponse]:
        return self.channel.unary_unary(  # type: ignore
            '/pandora.l2cap.L2CAP/Disconnect',
            request_serializer=l2cap_pb2.DisconnectRequest.SerializeToString,  # type: ignore
            response_deserializer=l2cap_pb2.DisconnectResponse.FromString  # type: ignore
        )(l2cap_pb2.DisconnectRequest(channel=channel), wait_for_ready=wait_for_ready, timeout=timeout)  # type: ignore

    def WaitDisconnection(self, channel: l2cap_pb2.Channel = l2cap_pb2.Channel(), wait_for_ready: Optional[bool] = None, timeout: Optional[float] = None) -> Awaitable[l2cap_pb2.WaitDisconnectionResponse]:
        return self.channel.unary_unary(  # type: ignore
            '/pandora.l2cap.L2CAP/WaitDisconnection',
            request_serializer=l2cap_pb2.WaitDisconnectionRequest.SerializeToString,  # type: ignore
            response_deserializer=l2cap_pb2.WaitDisconnectionResponse.FromString  # type: ignore
        )(l2cap_pb2.WaitDisconnectionRequest(channel=channel), wait_for_ready=wait_for_ready, timeout=timeout)  # type: ignore

    def Receive(self, channel: l2cap_pb2.Channel = l2cap_pb2.Channel(), wait_for_ready: Optional[bool] = None, timeout: Optional[float] = None) -> Stream[l2cap_pb2.ReceiveResponse]:
        return self.channel.unary_stream(  # type: ignore
            '/pandora.l2cap.L2CAP/Receive',
            request_serializer=l2cap_pb2.ReceiveRequest.SerializeToString,  # type: ignore
            response_deserializer=l2cap_pb2.ReceiveResponse.FromString  # type: ignore
        )(l2cap_pb2.ReceiveRequest(channel=channel), wait_for_ready=wait_for_ready, timeout=timeout)  # type: ignore

    def Send(self, channel: l2cap_pb2.Channel = l2cap_pb2.Channel(), data: bytes = b'', wait_for_ready: Optional[bool] = None, timeout: Optional[float] = None) -> Awaitable[l2cap_pb2.SendResponse]:
        return self.channel.unary_unary(  # type: ignore
            '/pandora.l2cap.L2CAP/Send',
            request_serializer=l2cap_pb2.SendRequest.SerializeToString,  # type: ignore
            response_deserializer=l2cap_pb2.SendResponse.FromString  # type: ignore
        )(l2cap_pb2.SendRequest(channel=channel, data=data), wait_for_ready=wait_for_ready, timeout=timeout)  # type: ignore


class L2CAPServicer:
    async def Connect(self, request: l2cap_pb2.ConnectRequest, context: grpc.ServicerContext) -> l2cap_pb2.ConnectResponse:
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)  # type: ignore
        context.set_details("Method not implemented!")  # type: ignore
        raise NotImplementedError("Method not implemented!")

    async def OnConnection(self, request: l2cap_pb2.OnConnectionRequest, context: grpc.ServicerContext) -> AsyncGenerator[l2cap_pb2.OnConnectionResponse, None]:
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)  # type: ignore
        context.set_details("Method not implemented!")  # type: ignore
        raise NotImplementedError("Method not implemented!")
        yield l2cap_pb2.OnConnectionResponse()  # no-op: to make the linter happy

    async def Disconnect(self, request: l2cap_pb2.DisconnectRequest, context: grpc.ServicerContext) -> l2cap_pb2.DisconnectResponse:
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)  # type: ignore
        context.set_details("Method not implemented!")  # type: ignore
        raise NotImplementedError("Method not implemented!")

    async def WaitDisconnection(self, request: l2cap_pb2.WaitDisconnectionRequest, context: grpc.ServicerContext) -> l2cap_pb2.WaitDisconnectionResponse:
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)  # type: ignore
        context.set_details("Method not implemented!")  # type: ignore
        raise NotImplementedError("Method not implemented!")

    async def Receive(self, request: l2cap_pb2.ReceiveRequest, context: grpc.ServicerContext) -> AsyncGenerator[l2cap_pb2.ReceiveResponse, None]:
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)  # type: ignore
        context.set_details("Method not implemented!")  # type: ignore
        raise NotImplementedError("Method not implemented!")
        yield l2cap_pb2.ReceiveResponse()  # no-op: to make the linter happy

    async def Send(self, request: l2cap_pb2.SendRequest, context: grpc.ServicerContext) -> l2cap_pb2.SendResponse:
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)  # type: ignore
        context.set_details("Method not implemented!")  # type: ignore
        raise NotImplementedError("Method not implemented!")


def add_L2CAPServicer_to_server(servicer: L2CAPServicer, server: grpc.aio.Server) -> None:
    rpc_method_handlers = {
        'Connect': grpc.unary_unary_rpc_method_handler(  # type: ignore
            servicer.Connect,
            request_deserializer=l2cap_pb2.ConnectRequest.FromString,  # type: ignore
            response_serializer=l2cap_pb2.ConnectResponse.SerializeToString,  # type: ignore
        ),
        'OnConnection': grpc.unary_stream_rpc_method_handler(  # type: ignore
            servicer.OnConnection,
            request_deserializer=l2cap_pb2.OnConnectionRequest.FromString,  # type: ignore
            response_serializer=l2cap_pb2.OnConnectionResponse.SerializeToString,  # type: ignore
        ),
        'Disconnect': grpc.unary_unary_rpc_method_handler(  # type: ignore
            servicer.Disconnect,
            request_deserializer=l2cap_pb2.DisconnectRequest.FromString,  # type: ignore
            response_serializer=l2cap_pb2.DisconnectResponse.SerializeToString,  # type: ignore
        ),
        'WaitDisconnection': grpc.unary_unary_rpc_method_handler(  # type: ignore
            servicer.WaitDisconnection,
            request_deserializer=l2cap_pb2.WaitDisconnectionRequest.FromString,  # type: ignore
            response_serializer=l2cap_pb2.WaitDisconnectionResponse.SerializeToString,  # type: ignore
        ),
        'Receive': grpc.unary_stream_rpc_method_handler(  # type: ignore
            servicer.Receive,
            request_deserializer=l2cap_pb2.ReceiveRequest.FromString,  # type: ignore
            response_serializer=l2cap_pb2.ReceiveResponse.SerializeToString,  # type: ignore
        ),
        'Send': grpc.unary_unary_rpc_method_handler(  # type: ignore
            servicer.Send,
            request_deserializer=l2cap_pb2.SendRequest.FromString,  # type: ignore
            response_serializer=l2cap_pb2.SendResponse.SerializeToString,  # type: ignore
        ),
    
    }
    generic_handler = grpc.method_handlers_generic_handler(  # type: ignore
        'pandora.l2cap.L2CAP', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))  # type: ignore
