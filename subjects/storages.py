from storages.backends.s3boto3 import S3Boto3Storage


class UABStorage(S3Boto3Storage):
    """
    Custom storage class for files associated with Universidad Autónoma de Barcelona (UAB) stored on Amazon S3.
    """
    location = 'UAB'
    file_overwrite = False


class UAMStorage(S3Boto3Storage):
    """
    Custom storage class for files associated with Universidad Autónoma de Madrid (UAM) stored on Amazon S3.
    """
    location = 'UAM'
    file_overwrite = False


class UC3MStorage(S3Boto3Storage):
    """
    Custom storage class for files associated with Universidad Carlos III de Madrid (UC3M) stored on Amazon S3.
    """
    location = 'UC3M'
    file_overwrite = False