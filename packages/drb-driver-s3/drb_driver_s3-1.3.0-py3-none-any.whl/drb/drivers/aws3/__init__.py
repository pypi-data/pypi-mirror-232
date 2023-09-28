from .aws3 import (
    DrbS3Service, DrbS3Bucket, DrbS3Object, S3NodeFactory, Auth, Requests
)
from . import _version

__version__ = _version.get_versions()['version']

__all__ = [
    'S3NodeFactory',
    'DrbS3Object',
    'DrbS3Bucket',
    'DrbS3Service',
    'Auth',
    'Requests'
]
