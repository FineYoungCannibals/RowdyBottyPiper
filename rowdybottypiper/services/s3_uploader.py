import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path
from typing import Optional


class S3Uploader:
    """
    A class to handle file uploads to Digital Ocean Spaces (or AWS S3).
    
    Usage:
        from rowdybottypiper.logging.structured_logger import StructuredLogger
        
        logger = StructuredLogger("S3Uploader")
        uploader = S3Uploader(
            bucket_name='your-bucket',
            region_name='atl1',
            endpoint_url='https://atl1.digitaloceanspaces.com',
            access_key='your-spaces-access-key',
            secret_key='your-spaces-secret-key'
        )
        uploader.upload_file('local_file.txt', 'folder/subfolder')
    """
    
    def __init__(
        self, 
        bucket_name: str, 
        region_name: str = 'us-east-1',
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        """
        Initialize the uploader for Digital Ocean Spaces or AWS S3.
        
        Args:
            logger: StructuredLogger instance for logging
            bucket_name: Name of the Space/bucket (e.g., 'the-rusty-bucket')
            region_name: Region (e.g., 'atl1' for Digital Ocean, 'us-east-1' for AWS)
            endpoint_url: Endpoint URL (e.g., 'https://atl1.digitaloceanspaces.com')
            access_key: Spaces/AWS access key
            secret_key: Spaces/AWS secret key
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        
        # Configure client
        client_config = {'region_name': region_name}
        
        if endpoint_url:
            client_config['endpoint_url'] = endpoint_url
        
        if access_key and secret_key:
            client_config['aws_access_key_id'] = access_key
            client_config['aws_secret_access_key'] = secret_key
        
        self.s3_client = boto3.client('s3', **client_config)
    
    def upload_file(
        self, 
        file_path: str, 
        s3_folder: str = '', 
        s3_filename: Optional[str] = None,
        make_public: bool = False
    ) -> bool:
        """
        Upload a file to S3 in a specific folder.
        
        Args:
            file_path: Path to the local file to upload
            s3_folder: Folder path in S3 (e.g., 'documents/reports')
            s3_filename: Optional custom filename in S3 (uses original name if not provided)
            make_public: Whether to make the file publicly accessible
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Get the filename
            local_file = Path(file_path)
            if not local_file.exists():
                return False
            
            # Determine S3 key (full path in bucket)
            filename = s3_filename or local_file.name
            
            # Construct the full S3 key with folder
            if s3_folder:
                # Remove leading/trailing slashes and ensure proper format
                s3_folder = s3_folder.strip('/')
                s3_key = f"{s3_folder}/{filename}"
            else:
                s3_key = filename
            
            # Prepare upload arguments
            extra_args = {}
            if make_public:
                extra_args['ACL'] = 'public-read'
            
            # Upload the file
            self.s3_client.upload_file(
                str(local_file),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args if extra_args else None
            )
            
            return True
            
        except NoCredentialsError:
            return False
        except ClientError as e:
            return False
        except Exception as e:
            return False
    
    def get_file_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a pre-signed URL for a file in S3.
        
        Args:
            s3_key: The full S3 key (path) of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Pre-signed URL or None if error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            return None
    
    def list_files(self, folder: str = '') -> list:
        """
        List all files in a specific folder.
        
        Args:
            folder: S3 folder path
            
        Returns:
            list: List of file keys in the folder
        """
        try:
            prefix = f"{folder.strip('/')}/" if folder else ''
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
            
        except ClientError as e:
            return []