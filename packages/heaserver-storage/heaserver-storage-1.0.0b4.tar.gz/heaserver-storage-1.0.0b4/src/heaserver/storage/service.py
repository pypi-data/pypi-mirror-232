"""
The HEA Server storage Microservice provides ...
"""

from heaserver.service import response
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import aws, awsservicelib
from heaserver.service.wstl import builder_factory, action
from heaserver.service.appproperty import HEA_DB
from heaserver.service.sources import AWS_S3
from heaobject.bucket import AWSBucket
from heaobject.storage import AWSStorage
from botocore.exceptions import ClientError
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass
import logging
import asyncio

MONGODB_STORAGE_COLLECTION = 'storage'


@routes.get('/volumes/{volume_id}/storage')
@routes.get('/volumes/{volume_id}/storage/')
@action(name='heaserver-storage-storage-get-properties', rel='hea-properties')
async def get_all_storage(request: web.Request) -> web.Response:
    """
    Gets all the storage of the volume id that associate with the AWS account.
    :param request: the HTTP request.
    :return: A list of the account's storage or an empty array if there's no any objects data under the AWS account.
    ---
    summary: get all storage for a hea-volume associate with account.
    tags:
        - heaserver-storage-storage-get-account-storage
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
    """
    return await _get_all_storages(request)


@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok(None)


def main() -> None:
    config = init_cmd_line(description='a service for managing storage and their data within the cloud',
                           default_port=8080)
    start(package_name='heaserver-storage', db=aws.S3Manager, wstl_builder_factory=builder_factory(__package__), config=config)


@dataclass
class _StorageMetadata:
    total_size: int = 0
    object_count: int = 0
    first_modified: datetime | None = None
    last_modified: datetime | None = None


async def _get_all_storages(request: web.Request) -> web.Response:
    """
    List available storage classes by name

    :param request: the aiohttp Request (required).
    :return: (list) list of available storage classes
    """

    logger = logging.getLogger(__name__)
    volume_id = request.match_info.get("volume_id", None)
    bucket_id = request.match_info.get('id', None)
    bucket_name = request.match_info.get('bucket_name', None)
    if not volume_id:
        return web.HTTPBadRequest(body="volume_id is required")
    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    loop_ = asyncio.get_running_loop()
    try:
        groups: dict[str, _StorageMetadata] = defaultdict(_StorageMetadata)
        coro_list = []
        for bucket in (await loop_.run_in_executor(None, s3_client.list_buckets))['Buckets']:
            if (bucket_id is None and bucket_name is None) or (bucket['Name'] in (bucket_id, bucket_name)):
                async def get_objects_for_bucket(bucket_name: str):
                    async for obj in awsservicelib.list_objects(s3_client, bucket_name, loop=loop_):
                        metadata = groups[obj['StorageClass']]
                        metadata.object_count += 1
                        metadata.total_size += obj['Size']
                        metadata.first_modified = obj['LastModified'] if metadata.first_modified is None or obj['LastModified'] < metadata.first_modified else metadata.first_modified
                        metadata.last_modified = obj['LastModified'] if metadata.last_modified is None or obj['LastModified'] > metadata.last_modified else metadata.last_modified
                coro_list.append(get_objects_for_bucket(bucket['Name']))
        await asyncio.gather(*coro_list)

        storage_class_list = []
        for item_key, item_values in groups.items():
            storage_class = _get_storage_class(volume_id=volume_id, item_key=item_key, item_values=item_values)
            storage_class_list.append(storage_class)
    except ClientError as e:
        logging.exception('Error calculating storage classes')
        return response.status_bad_request()

    storage_class_dict_list = [storage.to_dict() for storage in storage_class_list if storage is not None]
    return await response.get_all(request, storage_class_dict_list)


def _get_storage_class(volume_id: str, item_key: str, item_values: _StorageMetadata) -> AWSStorage:
    """
    :param item_key: the item_key
    :param item_values:  item_values
    :return: Returns the AWSStorage
    """
    logger = logging.getLogger(__name__)

    assert volume_id is not None, "volume_id is required"
    assert item_key is not None, "item_key is required"
    assert item_values is not None, "item_values is required"

    s = AWSStorage()
    s.name = item_key
    s.id = item_key
    s.display_name = item_key
    s.object_init_modified = item_values.first_modified
    s.object_last_modified = item_values.last_modified
    s.storage_bytes = item_values.total_size
    s.object_count = item_values.object_count
    s.created = datetime.now()
    s.modified = datetime.now()
    s.volume_id = volume_id
    s.set_storage_class_from_str(item_key)
    s.source = AWS_S3
    return s
