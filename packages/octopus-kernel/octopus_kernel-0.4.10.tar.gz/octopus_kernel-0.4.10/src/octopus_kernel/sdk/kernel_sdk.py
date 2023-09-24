# vim:fenc=utf-8
#
# Copyright (C) 2023 dbpunk.com Author imotai <codego.me@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" """

import logging
import grpc
from grpc import aio
from octopus_proto import kernel_server_pb2
from octopus_proto import common_pb2
from octopus_proto.kernel_server_pb2_grpc import KernelServerNodeStub
from typing import AsyncIterable

logger = logging.getLogger(__name__)


class KernelSDK:

    def __init__(self, endpoint, api_key):
        self.endpoint = endpoint
        self.stub = None
        self.metadata = aio.Metadata(
            ("api_key", api_key),
        )

    def connect(self):
        """
        Connect the remote kernel instance
        """
        channel = aio.insecure_channel(self.endpoint)
        self.channel = channel
        self.stub = KernelServerNodeStub(channel)

    async def stop(self, kernel_name=None):
        """
        Stop the kernel
        """
        request = kernel_server_pb2.StopKernelRequest(kernel_name=kernel_name)
        response = await self.stub.stop(request, metadata=self.metadata)
        return response

    async def is_alive(self, kernel_name=None):
        request = kernel_server_pb2.GetStatusRequest(kernel_name=kernel_name)
        response = await self.stub.get_status(request, metadata=self.metadata)
        return response.is_alive

    async def download_file(self, filename):
        request = common_pb2.DownloadRequest(filename=filename)
        async for chunk in self.stub.download(request, metadata=self.metadata):
            yield chunk

    async def upload_binary(self, chunks: AsyncIterable[common_pb2.FileChunk]):
        try:
            return await self.stub.upload(chunks, metadata=self.metadata)
        except Exception as ex:
            logger.error("upload file ex %s" % ex)

    async def start(self, kernel_name=None):
        """
        Start the kernel
        """
        request = kernel_server_pb2.StartKernelRequest(kernel_name=kernel_name)
        response = await self.stub.start(request, metadata=self.metadata)
        return response

    async def execute(self, code, kernel_name=None):
        """
        Execute the python code
        """
        request = kernel_server_pb2.ExecuteRequest(code=code, kernel_name=kernel_name)
        async for respond in self.stub.execute(request, metadata=self.metadata):
            yield respond

    async def close(self):
        if self.channel:
            self.channel.close()
            self.channel = None
