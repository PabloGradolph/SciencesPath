from storages.backends.s3boto3 import S3Boto3Storage

class UABStorage(S3Boto3Storage):
    location = 'UAB'
    file_overwrite = False

class UAMStorage(S3Boto3Storage):
    location = 'UAM'
    file_overwrite = False

class UC3MStorage(S3Boto3Storage):
    location = 'UC3M'
    file_overwrite = False