# Copyright 2020 Adap GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Servicer for FlowerService.

Relevant knowledge for reading this modules code:
    - https://github.com/grpc/grpc/blob/master/doc/statuscodes.md
"""
from contextlib import contextmanager
from typing import Callable, Iterator, Any, Dict, Tuple, Optional
import timeit
import grpc
from iterators import TimeoutIterator

from daisyfl.proto import transport_pb2_grpc
from daisyfl.proto.transport_pb2 import ClientMessage, ServerMessage
from daisyfl.server.client_manager import ClientManager
from daisyfl.server.grpc_server.grpc_bridge import GRPCBridge
from daisyfl.server.grpc_server.grpc_client_proxy import GrpcClientProxy
from daisyfl.common.logger import log
from logging import INFO, WARNING, DEBUG, ERROR
from daisyfl.common import (
    HANDOVER,
    ROOT_CERTIFICATES,
    ANCHOR,
    GRPC_MAX_MESSAGE_LENGTH,
    IS_ZONE,
    CREDENTIAL,
    serde,
    ClientStatus,
    ServerStatus,
    CLIENT_HANDLING,
    CLIENT_IDLING,
    SERVER_IDLING,
    SERVER_WAITING,
    metadata_to_dict,
    dict_to_metadata,
    CID,
    Code,
    ServerReceivedSignal,
    ClientRoamingSignal,
    Status,
    FitRes,
    Parameters,
)
from daisyfl.proto.transport_pb2_grpc import FlowerServiceStub
from threading import Condition, Event
from enum import Enum
from queue import Queue

def default_bridge_factory(client_idling: bool) -> GRPCBridge:
    """Return GRPCBridge instance."""
    return GRPCBridge(client_idling)


def default_grpc_client_factory(bridge: GRPCBridge, metadata_dict: Dict) -> GrpcClientProxy:
    """Return GrpcClientProxy instance."""
    return GrpcClientProxy(cid=metadata_dict[CID], bridge=bridge, metadata_dict=metadata_dict)


def register_client(
    client_manager: ClientManager,
    client: GrpcClientProxy,
    is_zone: bool,
    context: grpc.ServicerContext,
) -> bool:
    """Try registering GrpcClientProxy with ClientManager."""
    is_success = client_manager.register(client, is_zone)

    if is_success:

        def rpc_termination_callback() -> None:
            client.bridge.close()
            client_manager.unregister(client)

        context.add_callback(rpc_termination_callback)

    return is_success


def on_channel_state_change(channel_connectivity: str) -> None:
    """Log channel connectivity."""
    log(DEBUG, channel_connectivity)

class FlowerServiceServicer(transport_pb2_grpc.FlowerServiceServicer):
    """FlowerServiceServicer for bi-directional gRPC message stream."""

    def __init__(
        self,
        client_manager: ClientManager,
        server_address: str,
        grpc_bridge_factory: Callable[[bool], GRPCBridge] = default_bridge_factory,
        grpc_client_factory: Callable[
            [GRPCBridge, Dict], GrpcClientProxy
        ] = default_grpc_client_factory,
    ) -> None:
        self.client_manager: ClientManager = client_manager
        self.server_address: str = server_address
        self.grpc_bridge_factory = grpc_bridge_factory
        self.client_factory = grpc_client_factory
        # sentinel
        self.sentinel = ClientMessage(fit_res=serde.fit_res_to_proto(FitRes(
            status=Status(code=Code.OK, message="Success"),
            parameters=Parameters(tensors=[], tensor_type=""),
            config={},
        )))

    def Join(  # pylint: disable=invalid-name
        self,
        request_iterator: Iterator[ClientMessage],
        context: grpc.ServicerContext,
    ) -> Iterator[ServerMessage]:
        """Method will be invoked by each GrpcClientProxy which participates in
        the network.

        Protocol:
            ...
            - The Join method is (pretty much) protocol unaware
        """
        # process Iterator
        client_timeout_iterator = TimeoutIterator(iterator=request_iterator, reset_on_next=True)
        client_message, success = self.get_client_message(client_message_iterator=client_timeout_iterator, context=context, timeout=3)
        if not success:
            return
        field = client_message.WhichOneof("msg")
        if field == "client_status":
            # check handover
            metadata_dict = metadata_to_dict(context.invocation_metadata(), _check_reserved=False)
            if metadata_dict.__contains__(HANDOVER):
                yield from self.roaming_request(client_timeout_iterator=client_timeout_iterator, context=context)
            else:
                client_status: ClientStatus = serde.client_status_from_proto(client_message.client_status)
                yield from self.serve(client_timeout_iterator=client_timeout_iterator, context=context, client_status=client_status)
        elif field == "client_roaming_signal":
            # get roaming information from Anchor
            log(INFO, "Receive CRS")
            yield from self.roaming_info_request(client_timeout_iterator=client_timeout_iterator, context=context,)
        else:
            log(ERROR, "Receive unexpected message type.")
            return

    @contextmanager
    def grpc_connection(
        self,
        parent_address: str,
        metadata: Tuple,
        root_certificates: Optional[bytes] = None,
    ) -> Iterator[Tuple[Callable[[], ServerMessage], Callable[[ClientMessage], None]]]:
        # Possible options:
        # https://github.com/grpc/grpc/blob/v1.43.x/include/grpc/impl/codegen/grpc_types.h
        channel_options = [
            ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH),
        ]

        if root_certificates is not None:
            ssl_channel_credentials = grpc.ssl_channel_credentials(root_certificates)
            channel = grpc.secure_channel(
                parent_address, ssl_channel_credentials, options=channel_options
            )
            log(INFO, "Opened secure gRPC connection using certificates")
        else:
            channel = grpc.insecure_channel(parent_address, options=channel_options)
            log(INFO, "Opened insecure gRPC connection (no certificates were passed)")

        channel.subscribe(on_channel_state_change)
        
        stub = FlowerServiceStub(channel)
        queue: Queue[ClientMessage] = Queue(maxsize=1)
        time_iterator = TimeoutIterator(iterator=iter(queue.get, None), reset_on_next=True)

        server_message_iterator: Iterator[ServerMessage] = stub.Join(time_iterator, metadata=metadata)
        timeout_iterator = TimeoutIterator(iterator=server_message_iterator, reset_on_next=True)

        def receive_fn(timeout: Optional[int] = None) -> Tuple[ServerMessage, bool]:
            if timeout is not None:
                timeout_iterator.set_timeout(float(timeout))
            server_message = next(timeout_iterator)
            if server_message is timeout_iterator.get_sentinel():
                return server_message, False
            return server_message, True
        receive: Callable[[Optional[int]], Tuple[ServerMessage, bool]] = receive_fn
        send: Callable[[ClientMessage], None] = lambda msg: queue.put(msg, block=False)

        try:
            yield send, receive
        finally:
            # Release Iterator to avoid leaking memory
            time_iterator.interrupt()
            send(self.sentinel)
            # Make sure to have a final
            channel.close()
            log(DEBUG, "gRPC channel closed")

    def roaming_request(
        self,
        client_timeout_iterator: Iterator[ClientMessage],
        context: grpc.ServicerContext,
    ) -> Iterator[ServerMessage]:
        """Get roaming information from anchor."""
        log(DEBUG, "Client roaming detected")
        # get metadata
        metadata_dict = metadata_to_dict(context.invocation_metadata(), _check_reserved=False)
        ## parent address
        parent_address = metadata_dict[ANCHOR]
        ## root_certificates
        if metadata_dict.__contains__(ROOT_CERTIFICATES):
            root_certificates = metadata_dict[ROOT_CERTIFICATES]
        else:
            root_certificates = None
        
        # register
        is_zone = True if metadata_dict.__contains__(IS_ZONE) else False
        bridge = self.grpc_bridge_factory(False)
        client_proxy = self.client_factory(bridge, metadata_dict)
        registration_success = register_client(self.client_manager, client_proxy, is_zone, context)
        if not registration_success:
            return
        
        try:
            # Client Uploading Signal
            client_message, success = self.get_client_message(client_message_iterator=client_timeout_iterator, context=context, timeout=None)
            if not success:
                return
            field = client_message.WhichOneof("msg")
            if field != "client_uploading_signal":
                return
            log(DEBUG, "Receive CUS")
            
            # connect to anchor
            with self.grpc_connection(
                parent_address=parent_address,
                metadata=dict_to_metadata(metadata_dict),
                root_certificates=root_certificates
            ) as conn:
                send, receive = conn
                ## send CRS to anchor
                crs = ClientRoamingSignal(status=Status(code=Code.OK, message=""))
                crs_msg = ClientMessage(client_roaming_signal=serde.client_roaming_signal_to_proto(crs))
                send(crs_msg)
                log(DEBUG, "Send CRS")
                ## get server_status
                server_status_msg, success = receive()
                field = server_status_msg.WhichOneof("msg")
                if field != "server_status":
                    return
                server_status = serde.server_status_from_proto(server_status_msg.server_status)
                server_waiting = True if server_status.status == SERVER_WAITING else False
                ## send server_status to client
                yield server_status_msg
                log(DEBUG, "Send ServerStatus of the anchor")
                ## get the result from client
                client_message, success = self.get_client_message(client_message_iterator=client_timeout_iterator, context=context, timeout=None)
                if success:
                    ### Nofity anchor
                    client_msg_sentinel = ClientMessage(fit_res=serde.fit_res_to_proto(FitRes(
                        status=Status(code=Code.OK, message="Success"),
                        parameters=Parameters(tensors=[], tensor_type=""),
                        config={},
                    )))
                    send(client_msg_sentinel)
                    ### receive SRS from anchor
                    srs, srs_success = receive()
                    if not srs_success:
                        return
                    if srs.WhichOneof("msg") != "server_received_signal":
                        return
                    ### Proximal Transmission
                    if server_waiting:
                        client_proxy.bridge.set_client_message(client_message=client_message, roaming=True)
                        log(DEBUG, "Set ClientMessage")
                    ### send SRS
                    yield srs
                    log(DEBUG, "Send SRS")
            return
        except StopIteration:
            return            
    
    def roaming_info_request(
        self,
        client_timeout_iterator: Iterator[ClientMessage],
        context: grpc.ServicerContext,
    ) -> Iterator[ServerMessage]:
        log(DEBUG, "Anchor required for roaming information")
        # register
        metadata_dict = metadata_to_dict(context.invocation_metadata(), _check_reserved=False)
        bridge = self.grpc_bridge_factory(False)
        client_proxy = self.client_factory(bridge, metadata_dict)
        registration_success = register_client(self.client_manager, client_proxy, False, context)
        if not registration_success:
            return
        try:
            # send server_status
            server_waiting = bridge.check_waiting(client_proxy.cid)
            if not server_waiting:
                server_status = serde.server_status_to_proto(ServerStatus(status=SERVER_IDLING))
            else:
                server_status = serde.server_status_to_proto(ServerStatus(status=SERVER_WAITING))
            server_status_msg = ServerMessage(server_status=server_status)
            yield server_status_msg
            log(DEBUG, "Send ServerStatus")

            # receive sentinel
            client_message, success = self.get_client_message(client_message_iterator=client_timeout_iterator, context=context, timeout=None)
            if success:
                if server_waiting:
                    ## notify server that client roamed
                    client_proxy.bridge.client_roam(client_proxy.cid)
                # send SRS    
                srs = ServerReceivedSignal(status=Status(code=Code.OK, message=""))
                server_message = ServerMessage(server_received_signal=serde.server_received_signal_to_proto(srs))
                yield server_message
                log(DEBUG, "Send SRS")    
            return
        except StopIteration:
            return

    def serve(
        self,
        client_timeout_iterator: Iterator[ClientMessage],
        context: grpc.ServicerContext,
        client_status: ClientStatus,
    ) -> Iterator[ServerMessage]:
        # client status
        if client_status.status == CLIENT_IDLING:
            client_idling = True
        elif client_status.status == CLIENT_HANDLING:
            client_idling = False
        else:
            log(ERROR, "Receive undefined ClientStatus")

        # register
        metadata_dict = metadata_to_dict(context.invocation_metadata(), _check_reserved=False)
        is_zone = True if metadata_dict.__contains__(IS_ZONE) else False
        bridge = self.grpc_bridge_factory(client_idling)
        client_proxy = self.client_factory(bridge, metadata_dict)
        registration_success = register_client(self.client_manager, client_proxy, is_zone, context)
        if not registration_success:
            return

        # streaming
        # TODO: while True:
        if client_idling:
            try:
                yield from self.get_server_message(client_proxy)
                log(DEBUG, "Send ServerMessage")
                client_idling = False
            except StopIteration:
                return
        else:
            try:
                # Client Uploading Signal
                client_message, success = self.get_client_message(client_message_iterator=client_timeout_iterator, context=context, timeout=None)
                if not success:
                    return
                field = client_message.WhichOneof("msg")
                if field != "client_uploading_signal":
                    return
                log(DEBUG, "Receive CUS")
                # check server status
                server_waiting = bridge.check_waiting(client_proxy.cid)
                if not server_waiting:
                    server_status = serde.server_status_to_proto(ServerStatus(status=SERVER_IDLING))
                else:
                    server_status = serde.server_status_to_proto(ServerStatus(status=SERVER_WAITING))
                server_status_msg = ServerMessage(server_status=server_status)
                yield server_status_msg
                log(DEBUG, "Send ServerStatus")
                # get the result
                client_message, success = self.get_client_message(client_message_iterator=client_timeout_iterator, context=context, timeout=None)
                if success:
                    if server_waiting:
                        client_proxy.bridge.set_client_message(client_message=client_message)
                        log(DEBUG, "Set ClientMessage")
                    srs = ServerReceivedSignal(status=Status(code=Code.OK, message=""))
                    server_message = ServerMessage(server_received_signal=serde.server_received_signal_to_proto(srs))
                    yield server_message
                    log(DEBUG, "Send SRS")
                    client_idling = True
                    Event.wait(timeout=5)
            except StopIteration:
                return
        # return

    def get_server_message(self, client_proxy: GrpcClientProxy,) -> Iterator[ServerMessage]:
        log(DEBUG, "Try sending ServerMessage")
        _server_message_iterator = client_proxy.bridge.server_message_iterator()
        # Get server_message from bridge
        server_message: ServerMessage = next(_server_message_iterator)
        yield server_message

    def get_client_message(self, client_message_iterator: TimeoutIterator,  context: grpc.ServicerContext, timeout: Optional[int] = None,) -> Tuple[ClientMessage, bool]:
        log(DEBUG, "Try receiving ClientMessage")
        if timeout is not None:
            client_message_iterator.set_timeout(float(timeout))
        # Wait for client message
        client_message = next(client_message_iterator)
        if client_message is client_message_iterator.get_sentinel():
            # Important: calling `context.abort` in gRPC always
            # raises an exception so that all code after the call to
            # `context.abort` will not run. If subsequent code should
            # be executed, the `rpc_termination_callback` can be used
            # (as shown in the `register_client` function).
            details = f"Timeout of {timeout}sec was exceeded."
            context.abort(
                code=grpc.StatusCode.DEADLINE_EXCEEDED,
                details=details,
            )
            # This return statement is only for the linter so it understands
            # that client_message in subsequent lines is not None
            # It does not understand that `context.abort` will terminate
            # this execution context by raising an exception.
            return client_message, False

        return client_message, True


# TODO: FlowerService -> DaisyService