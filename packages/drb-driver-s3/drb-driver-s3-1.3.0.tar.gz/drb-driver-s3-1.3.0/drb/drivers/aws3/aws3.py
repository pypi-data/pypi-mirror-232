import io
from abc import ABC
from typing import Any, List

import boto3
from botocore.client import BaseClient
from deprecated.classic import deprecated
from drb.core import DrbNode, DrbFactory
from drb.drivers.http import DrbHttpNode
from drb.exceptions.core import DrbException
from drb.nodes.abstract_node import AbstractNode
from requests.auth import HTTPBasicAuth


class Auth:
    """
    This class give us all the requirement to connect to a swift service.

    Parameters:
        service_name: The name of a service, e.g. 's3' or 'ec2'.
            region_name: The name of the region associated with the client.
            A client is associated with a single region.

        api_version: The API version to use.  By default, this implementation
            use the latest API version. You only need to specify this parameter
            if you want to use a previous API version of the client.

        use_ssl: Whether to use SSL.  By default, SSL is used.
            Note that not all services support non-ssl connections.

        verify: Whether to verify SSL certificates. By default,
            SSL certificates are verified.  You can provide the following
            values:
            * False - do not validate SSL certificates.  SSL will still be
            used (unless use_ssl is False), but SSL certificates
            will not be verified.
            * path/to/cert/bundle.pem - A filename of the CA cert bundle to
            uses.

        endpoint_url: The complete URL to use for the constructed
            client. If this value is provided, then ``use_ssl`` is ignored.

        aws_access_key_id: The access key to use when creating
            the client.

        aws_secret_access_key: The secret key to use when creating
            the client.

        aws_session_token: The session token to use when creating
            the client.

        config: Advanced client configuration options. If region_name
            is specified in the client config, its value will take precedence
            over environment variables and configuration values, but not over
            a region_name value passed explicitly to the method.  If
            user_agent_extra is specified in the client config, it overrides
            the default user_agent_extra provided by the resource API.
      """

    def __init__(self,
                 **kwargs):
        self.service_name = "s3"
        self.region_name = kwargs.get("", None)
        self.api_version = kwargs.get("api_version", None)
        self.use_ssl = kwargs.get("use_ssl", True)
        self.verify = kwargs.get("verify", None)
        self.endpoint_url = kwargs.get("endpoint_url", None)
        self.aws_access_key_id = kwargs.get("aws_access_key_id", None)
        self.aws_secret_access_key = kwargs.get("aws_secret_access_key", None)
        self.aws_session_token = kwargs.get("aws_session_token", None)
        self.config = kwargs.get("config", None)

    def get_session(self):
        session = boto3.session.Session()

        return session.client(
            service_name=self.service_name,
            region_name=self.region_name,
            api_version=self.api_version,
            use_ssl=self.use_ssl,
            verify=self.verify,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            config=self.config
        )


class Connection:
    """
    This class use the singleton pattern to provide too
    much connection to the s3 server.

    Parameters:
        auth: An Auth object to provide all the information required
              to establish the connection with the server.
    """

    conn = None

    def __new__(cls, auth: Auth) -> BaseClient:
        if cls.conn is None:
            cls.conn = boto3.resource(
                service_name=auth.service_name,
                region_name=auth.region_name,
                api_version=auth.api_version,
                use_ssl=auth.use_ssl,
                verify=auth.verify,
                endpoint_url=auth.endpoint_url,
                aws_access_key_id=auth.aws_access_key_id,
                aws_secret_access_key=auth.aws_secret_access_key,
                aws_session_token=auth.aws_session_token,
                config=auth.config
            )
        return cls.conn


class Requests:
    def __init__(self, auth: Auth):
        self.conn = Connection(auth)
        self.auth = auth

    def list_buckets(self):
        return self.conn.buckets.all()

    def list_objects(self, name):
        return self.conn.Bucket(name).objects.all()

    def get_temp_url(self, bucket, name):
        s3_api = self.auth.get_session()
        return s3_api.generate_presigned_url(
            'get_object', Params={
                'Bucket': bucket,
                'Key': name
            },
            ExpiresIn=3600
        )

    def get_obj(self, bucket, name):
        return self.conn.Object(
            bucket_name=bucket,
            key=name
        )


def check_args(*args):
    return len(args) > 0 and isinstance(
        args[0],
        int
    ) and args[0] > 0


class Download(io.BytesIO):
    def __init__(self, s3_object, chunk_size: int, headers):
        self.s3_object = s3_object
        self._chunk_size = chunk_size
        self.__res = None
        self._iter = None
        self._headers = headers
        self._buff = bytearray(0)
        self._pos = 0
        self._seekable = True
        self.content_length = -1
        super().__init__()

    @property
    def size(self):
        return self.s3_object.content_length

    def seek(self, offset, whence=0):
        if not self._seekable:
            raise OSError
        if whence == 0:
            pos_seek = 0
        elif whence == 1:
            pos_seek = self._pos
        elif whence == 2:
            if self.content_length == -1:
                # reset position to find end of file
                # in case of we are at end of file...
                self._pos = 0
                self.__init_request()
            pos_seek = self.content_length

        pos_seek += offset
        if pos_seek < 0:
            raise OSError

        if pos_seek != self._pos:
            if pos_seek > self._pos and \
                    (pos_seek - self._pos) < (10 * self._chunk_size):
                read = 1
                to_read = pos_seek - self._pos
                while to_read > 0 and read > 0:
                    if to_read > self._chunk_size:
                        size_to_read = self._chunk_size
                    else:
                        size_to_read = to_read
                    buff = self.read(size_to_read)
                    read = len(buff)
                    to_read -= read

                return self._pos
            if self.__res is not None:
                self.__res.close()
                self.__res = None

            self._pos = pos_seek

        return self._pos

    def __init_request(self):
        pos_start = self._pos
        heads = None
        if self.__res is None or self._iter is None:
            if self._iter is not None:
                self._iter.close()
                self._iter = None
            self._buff = bytearray(0)

            if self._headers is not None:
                pos_start = pos_start + self._headers[0]
                if len(self._headers) > 1:
                    end = pos_start + self._headers[1]
                    heads = {
                        "range":
                            f"bytes={pos_start}"
                            f"-{end}"
                    }
                else:
                    heads = {"range": f"bytes={pos_start}-"}
            elif pos_start > 0:
                heads = {"range": f"bytes={pos_start}-"}
            if heads:
                self.__res = self.s3_object.get(Range=heads['range'])
            else:
                self.__res = self.s3_object.get()
            self.content_length = self.size

    def __init_generator(self):
        self.__init_request()
        if self._iter is None:
            self._iter = iter(
                lambda: self.__res['Body'].read(
                    self._chunk_size
                ).encode(), b'')

    def getvalue(self) -> bytes:
        self.__init_request()
        return self.__res['Body'].read()

    def read(self, *args, **kwargs):
        if not check_args(*args):
            if self.__res is None:
                self.__init_request()

                return self.__res['Body'].read()

            else:
                _buff = self._buff[:]
                self._buff = bytearray(0)
                try:
                    while True:
                        _buff.extend(bytearray(next(self._iter)))
                except StopIteration:
                    self._pos += len(_buff)
                return _buff

        self.__init_request()
        self.__init_generator()
        try:
            while len(self._buff) < args[0]:
                self._buff.extend(bytearray(next(self._iter)))

            res = self._buff[0:args[0]]
            del (self._buff[0:args[0]])
            self._pos = self._pos + len(res)
            return res.decode()
        except StopIteration:
            if len(self._buff) > 0:
                if args[0] < len(self._buff):
                    res = self._buff[0:args[0]]
                    del (self._buff[0:args[0]])
                    self._pos = self._pos + len(res)
                    return res.decode()
                else:
                    self._pos = self._pos + len(self._buff)
                    res = self._buff[:]
                    self._buff = bytearray(0)
                    return res.decode()
            else:
                return bytes(0).decode()

    def tell(self) -> int:
        return self._pos

    def seekable(self, *args, **kwargs):
        return self._seekable

    def close(self) -> None:
        super().close()
        # if self._req is not None:
        #     self._req.close()


class DrbS3Node(AbstractNode, ABC):
    """
    Common DrbS3Node interface
    """

    def __init__(self, auth: Auth):
        super(DrbS3Node, self).__init__()
        self._auth = auth
        self._conn = None

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def close(self) -> None:
        """
        Close The s3 connection
        """
        if self._conn is not None:
            self._conn.close()

    def get_auth(self) -> Auth:
        """
        Return the Auth object created to access the service.
        """
        return self._auth

    def __eq__(self, other):
        return isinstance(other, DrbS3Node) and \
            self._auth == other._auth

    def __hash__(self):
        return hash(self._auth)


class DrbS3Object(DrbS3Node):
    def __init__(self, obj, parent: DrbS3Node):
        super().__init__(auth=parent.get_auth())
        self.req = Requests(parent.get_auth())
        self._obj = obj
        self.name = obj.key
        self.parent = parent
        self.add_impl(io.BytesIO, self._get_stream)
        self._init_attrs()

    def _init_attrs(self):
        for e in self._obj.get_available_subresources():
            name = e
            value = self._obj.name
            self.__imatmul__((name, value))

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        return []

    @staticmethod
    def _get_stream(node: DrbNode, **kwargs):
        if not isinstance(node, DrbS3Object):
            raise TypeError(f'Invalid node type: {type(node)}')

        headers = None
        if 'start' in kwargs:
            if 'end' in kwargs:
                headers = (kwargs.get('start'), kwargs.get('end'))
            else:
                headers = (kwargs.get('start'),)

        if kwargs.get('temp_url', False):
            tmp_url = node.req.get_temp_url(node.parent.name, node.name)
            return DrbHttpNode(tmp_url).get_impl(io.BytesIO)
        else:
            return Download(
                node.req.get_obj(node.parent.name, node.name),
                kwargs.get('chunk_size', 4 * 1048576),
                headers=headers
            )


class DrbS3Bucket(DrbS3Node):

    def __init__(self, obj, parent: DrbS3Node):
        super().__init__(auth=parent.get_auth())
        self.req = Requests(parent.get_auth())
        self._bucket = obj
        self.name = obj.name
        self._children = None
        self.parent = parent
        self._init_attrs()

    def _init_attrs(self):
        for e in self._bucket.get_available_subresources():
            name = e
            value = self._bucket.name
            self.__imatmul__((name, value))

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        self._conn = Connection(self._auth)
        if self._children is None:
            objects = self.req.list_objects(self.name)
            self._children = [
                DrbS3Object(obj, self)
                for obj in objects
            ]
        return self._children


class DrbS3Service(DrbS3Node):
    def __init__(self, auth: Auth):
        super().__init__(auth=auth)
        self.req = Requests(auth)
        self._children = None
        self.name = self._auth.service_name

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        self._conn = Connection(self._auth)
        if self._children is None:
            buckets = self.req.list_buckets()
            self._children = [
                DrbS3Bucket(bucket, self)
                for bucket in buckets
            ]
        return self._children


class S3NodeFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbS3Node):
            return node
        if isinstance(node, DrbHttpNode):
            if isinstance(node.auth, HTTPBasicAuth):
                auth = Auth(service_name=node.path.original_path,
                            aws_access_key_id=node.auth.username,
                            aws_secret_access_key=node.auth.password)
            else:
                auth = Auth(service_name=node.path.original_path)
            return DrbS3Service(auth=auth)
        raise NotImplementedError("Call impl method")
