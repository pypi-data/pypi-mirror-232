# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import common_pb2 as common__pb2
from . import kernel_server_pb2 as kernel__server__pb2


class KernelServerNodeStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.start = channel.unary_unary(
                '/octopus_kernel_proto.KernelServerNode/start',
                request_serializer=kernel__server__pb2.StartKernelRequest.SerializeToString,
                response_deserializer=kernel__server__pb2.StartKernelResponse.FromString,
                )
        self.stop = channel.unary_unary(
                '/octopus_kernel_proto.KernelServerNode/stop',
                request_serializer=kernel__server__pb2.StopKernelRequest.SerializeToString,
                response_deserializer=kernel__server__pb2.StopKernelResponse.FromString,
                )
        self.execute = channel.unary_stream(
                '/octopus_kernel_proto.KernelServerNode/execute',
                request_serializer=kernel__server__pb2.ExecuteRequest.SerializeToString,
                response_deserializer=kernel__server__pb2.ExecuteResponse.FromString,
                )
        self.get_status = channel.unary_unary(
                '/octopus_kernel_proto.KernelServerNode/get_status',
                request_serializer=kernel__server__pb2.GetStatusRequest.SerializeToString,
                response_deserializer=kernel__server__pb2.GetStatusResponse.FromString,
                )
        self.upload = channel.stream_unary(
                '/octopus_kernel_proto.KernelServerNode/upload',
                request_serializer=common__pb2.FileChunk.SerializeToString,
                response_deserializer=common__pb2.FileUploaded.FromString,
                )
        self.download = channel.unary_stream(
                '/octopus_kernel_proto.KernelServerNode/download',
                request_serializer=common__pb2.DownloadRequest.SerializeToString,
                response_deserializer=common__pb2.FileChunk.FromString,
                )


class KernelServerNodeServicer(object):
    """Missing associated documentation comment in .proto file."""

    def start(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def stop(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def execute(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_status(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def upload(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def download(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_KernelServerNodeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'start': grpc.unary_unary_rpc_method_handler(
                    servicer.start,
                    request_deserializer=kernel__server__pb2.StartKernelRequest.FromString,
                    response_serializer=kernel__server__pb2.StartKernelResponse.SerializeToString,
            ),
            'stop': grpc.unary_unary_rpc_method_handler(
                    servicer.stop,
                    request_deserializer=kernel__server__pb2.StopKernelRequest.FromString,
                    response_serializer=kernel__server__pb2.StopKernelResponse.SerializeToString,
            ),
            'execute': grpc.unary_stream_rpc_method_handler(
                    servicer.execute,
                    request_deserializer=kernel__server__pb2.ExecuteRequest.FromString,
                    response_serializer=kernel__server__pb2.ExecuteResponse.SerializeToString,
            ),
            'get_status': grpc.unary_unary_rpc_method_handler(
                    servicer.get_status,
                    request_deserializer=kernel__server__pb2.GetStatusRequest.FromString,
                    response_serializer=kernel__server__pb2.GetStatusResponse.SerializeToString,
            ),
            'upload': grpc.stream_unary_rpc_method_handler(
                    servicer.upload,
                    request_deserializer=common__pb2.FileChunk.FromString,
                    response_serializer=common__pb2.FileUploaded.SerializeToString,
            ),
            'download': grpc.unary_stream_rpc_method_handler(
                    servicer.download,
                    request_deserializer=common__pb2.DownloadRequest.FromString,
                    response_serializer=common__pb2.FileChunk.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'octopus_kernel_proto.KernelServerNode', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class KernelServerNode(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def start(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/octopus_kernel_proto.KernelServerNode/start',
            kernel__server__pb2.StartKernelRequest.SerializeToString,
            kernel__server__pb2.StartKernelResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def stop(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/octopus_kernel_proto.KernelServerNode/stop',
            kernel__server__pb2.StopKernelRequest.SerializeToString,
            kernel__server__pb2.StopKernelResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def execute(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/octopus_kernel_proto.KernelServerNode/execute',
            kernel__server__pb2.ExecuteRequest.SerializeToString,
            kernel__server__pb2.ExecuteResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def get_status(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/octopus_kernel_proto.KernelServerNode/get_status',
            kernel__server__pb2.GetStatusRequest.SerializeToString,
            kernel__server__pb2.GetStatusResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def upload(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/octopus_kernel_proto.KernelServerNode/upload',
            common__pb2.FileChunk.SerializeToString,
            common__pb2.FileUploaded.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def download(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/octopus_kernel_proto.KernelServerNode/download',
            common__pb2.DownloadRequest.SerializeToString,
            common__pb2.FileChunk.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
