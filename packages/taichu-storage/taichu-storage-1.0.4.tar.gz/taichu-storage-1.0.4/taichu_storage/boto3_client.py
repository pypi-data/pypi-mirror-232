import logging
import boto3
import botocore.exceptions
from botocore.config import Config
from taichu_storage import StorageInterface
import os
from urllib.parse import urlparse


class StorageBoto3(StorageInterface):
    def __init__(self, cfgs=None):
        if cfgs is None:
            cfgs = {}
        bucket = cfgs.get('bucket')
        ak = cfgs.get('ak')
        sk = cfgs.get('sk')
        region_name = cfgs.get('region_name', 'default')
        endpoint_url = cfgs.get('endpoint_url')
        prefix = cfgs.get('prefix')
        parsed_url = urlparse(endpoint_url)
        host_port = parsed_url.netloc.split(':')
        self._host = host_port[0]
        self._port = None
        if len(host_port) > 1:
            self._port = host_port[1]
        if prefix and not prefix.endswith('/'):
            prefix = prefix + '/'
        self._prefix = prefix
        self._bucket = bucket
        self._client = boto3.client(
            's3',
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            use_ssl=True,
            region_name=region_name,
            endpoint_url=endpoint_url,
            config=Config(s3={"addressing_style": "path", "signature_version": 's3v4'}))

    def list_objects(self, key, delimiter=''):
        key = f'{self._prefix}{key}'
        result = []
        try:
            response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=key, Delimiter=delimiter)
            if 'CommonPrefixes' in response:
                folders = []
                for item in response['CommonPrefixes']:
                    folders.append({
                        'name': item['Prefix'].replace(self._prefix, '', 1),
                        'is_dir': True,
                        'size': 0,
                        'last_modified': None,
                    })
                result.extend(folders)
            if 'Contents' in response:
                objects = []
                for item in response['Contents']:
                    if item['Key'].endswith('/'):
                        continue
                    objects.append({
                        'name': item['Key'].replace(self._prefix, '', 1),
                        'is_dir': False,
                        'size': item['Size'],
                        'last_modified': item['LastModified'].strftime("%Y-%m-%d %H:%M:%S"),
                    })
                result.extend(objects)
            return result
        except Exception as e:
            logging.error("list_objects error:", e)
            return []

    def put_object(self, key, content):
        key = f'{self._prefix}{key}'
        try:
            self._client.put_object(Body=content, Bucket=self._bucket, Key=key)
        except Exception as e:
            logging.error("put_object error", e)

    def upload_file(self, local_filename, key):
        key = f'{self._prefix}{key}'
        try:
            self._client.upload_file(local_filename, self._bucket, key)
        except Exception as e:
            logging.error("upload_file error", e)

    def upload_dir(self, local_dir, key):
        local_dir = local_dir.rstrip('/')
        key = key.rstrip('/')
        for item in os.scandir(local_dir):
            remote_key = item.path.replace(local_dir, key)
            if item.is_file():
                self.upload_file(item.path, remote_key)
            elif item.is_dir():
                self.upload_dir(item.path, remote_key)

    def download_file(self, key, local_filename):
        key = f'{self._prefix}{key}'
        try:
            self._client.download_file(self._bucket, key, local_filename)
        except Exception as e:
            logging.error("download_file error", e)

    def download_dir(self, key, local_dir):
        key = f'{self._prefix}{key}'
        response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=key)
        m = {}
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('/'):
                continue
            s3_key = obj['Key']
            local_file_path = f'{local_dir}{s3_key.replace(key, "")}'
            dirname = os.path.dirname(local_file_path)
            try:
                if not m.get(dirname, False):
                    os.makedirs(dirname, exist_ok=True)
                    m[dirname] = True
                self._client.download_file(self._bucket, s3_key, local_file_path)
            except Exception as e:
                logging.error(e)

    def copy_object(self, source_key, target_key):
        source_key = f'{self._prefix}{source_key}'
        target_key = f'{self._prefix}{target_key}'
        try:
            self._client.copy_object(Bucket=self._bucket, Key=target_key,
                                     CopySource={'Bucket': self._bucket, 'Key': source_key})
        except Exception as e:
            logging.error("copy_object error:", e)
            return None

    def copy_dir(self, source_dir, dest_dir):
        source_dir = f'{self._prefix}{source_dir}'
        dest_dir = f'{self._prefix}{dest_dir}'
        objects = self._client.list_objects_v2(Bucket=self._bucket, Prefix=source_dir)
        if 'Contents' not in objects:
            logging.info("No files found in the source folder.")
            return
        m = {}
        for obj in objects['Contents']:
            if obj['Key'].endswith('/'):
                continue
            copy_source = {'Bucket': self._bucket, 'Key': obj['Key']}
            dest_key = obj['Key'].replace(source_dir, dest_dir, 1)
            dirname = os.path.dirname(dest_key)
            if not m.get(dirname):
                self._client.put_object(Bucket=self._bucket, Key=dirname + '/')
                m[dirname] = True
            self._client.copy_object(CopySource=copy_source, Bucket=self._bucket, Key=dest_key)

    def create_dir(self, dirname):
        key = f'{self._prefix}{dirname}'
        if not key.endswith('/'):
            key = key + '/'
        try:
            self._client.put_object(Bucket=self._bucket, Key=key)
        except Exception as e:
            logging.error("create_dir error:", e)
            return None

    def generate_signed_url(self, key, expiration=3600, host_url=None):
        key = f'{self._prefix}{key}'
        try:
            url = self._client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket, 'Key': key},
                ExpiresIn=expiration,
            )
            if not host_url:
                return url
            host = urlparse(host_url).netloc.split(':')[0]
            return url.replace(self._host, host)
        except botocore.exceptions.ClientError as e:
            logging.error("generate_signed_url error:", e)
            return None

    def generate_upload_credentials(self, key, expiration=3600, host_url=None):
        key = f'{self._prefix}{key}'
        try:
            response = self._client.generate_presigned_post(self._bucket, key, ExpiresIn=expiration)
        except botocore.exceptions.ClientError as e:
            logging.error("generate_upload_credentials error:", e)
            return None

        return response
