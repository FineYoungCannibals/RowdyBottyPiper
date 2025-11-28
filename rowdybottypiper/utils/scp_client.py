import paramiko
from pathlib import Path
from typing import Optional
from rowdybottypiper.logging.structured_logger import StructuredLogger


class SCPClient:
    """
    A class to handle file transfers via SCP to remote servers.
    
    Usage:
        from rowdybottypiper.logging.structured_logger import StructuredLogger
        
        logger = StructuredLogger("SCPClient")
        scp_client = SCPClient(
            logger=logger,
            hostname='example.com',
            username='user',
            password='password',  # or use key_filename
            port=22
        )
        scp_client.upload_file('local_file.txt', '/remote/path/file.txt')
    """
    
    def __init__(
        self,
        logger: StructuredLogger,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22
    ):
        """
        Initialize the SCP client.
        
        Args:
            logger: StructuredLogger instance for logging
            hostname: Remote server hostname or IP
            username: SSH username
            password: SSH password (optional if using key_filename)
            key_filename: Path to SSH private key file (optional if using password)
            port: SSH port (default: 22)
        """
        self.logger = logger
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        
        self.logger.info(
            f"SCPClient initialized for {username}@{hostname}:{port}",
            auth_method="key" if key_filename else "password"
        )
    
    def _create_ssh_client(self) -> paramiko.SSHClient:
        """Create and configure SSH client"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if self.key_filename:
                self.logger.debug(f"Connecting with key file: {self.key_filename}")
                ssh.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_filename
                )
            else:
                self.logger.debug("Connecting with password")
                ssh.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            
            self.logger.debug(f"SSH connection established to {self.hostname}")
            return ssh
            
        except paramiko.AuthenticationException:
            self.logger.error("Authentication failed")
            raise
        except paramiko.SSHException as e:
            self.logger.error(f"SSH connection error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during SSH connection: {str(e)}")
            raise
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        create_remote_dirs: bool = True
    ) -> bool:
        """
        Upload a file to the remote server via SCP.
        
        Args:
            local_path: Path to the local file
            remote_path: Destination path on remote server
            create_remote_dirs: Create remote directories if they don't exist
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        ssh = None
        sftp = None
        
        try:
            # Verify local file exists
            local_file = Path(local_path)
            if not local_file.exists():
                self.logger.error(f"Local file not found: {local_path}")
                return False
            
            self.logger.info(
                f"Uploading {local_path} to {self.username}@{self.hostname}:{remote_path}"
            )
            
            # Create SSH connection
            ssh = self._create_ssh_client()
            sftp = ssh.open_sftp()
            
            # Create remote directories if needed
            if create_remote_dirs:
                remote_dir = str(Path(remote_path).parent)
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    self.logger.debug(f"Creating remote directory: {remote_dir}")
                    self._create_remote_directory(ssh, remote_dir)
            
            # Upload the file
            sftp.put(str(local_file), remote_path)
            
            self.logger.info(
                f"Upload successful: {local_path} -> {self.hostname}:{remote_path}"
            )
            return True
            
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission denied: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Upload failed: {str(e)}")
            return False
        
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
                self.logger.debug("SSH connection closed")
    
    def _create_remote_directory(self, ssh: paramiko.SSHClient, remote_path: str):
        """Create remote directory recursively"""
        try:
            stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {remote_path}')
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status != 0:
                error = stderr.read().decode()
                self.logger.error(f"Failed to create remote directory: {error}")
                raise Exception(f"Failed to create directory: {error}")
                
        except Exception as e:
            self.logger.error(f"Error creating remote directory: {str(e)}")
            raise
    
    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> bool:
        """
        Download a file from the remote server via SCP.
        
        Args:
            remote_path: Path to file on remote server
            local_path: Destination path on local machine
            
        Returns:
            bool: True if download successful, False otherwise
        """
        ssh = None
        sftp = None
        
        try:
            self.logger.info(
                f"Downloading {self.hostname}:{remote_path} to {local_path}"
            )
            
            # Create SSH connection
            ssh = self._create_ssh_client()
            sftp = ssh.open_sftp()
            
            # Create local directory if needed
            local_dir = Path(local_path).parent
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            sftp.get(remote_path, local_path)
            
            self.logger.info(
                f"Download successful: {self.hostname}:{remote_path} -> {local_path}"
            )
            return True
            
        except FileNotFoundError as e:
            self.logger.error(f"Remote file not found: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission denied: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}")
            return False
        
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
                self.logger.debug("SSH connection closed")
    
    def test_connection(self) -> bool:
        """Test the SSH connection to the remote server"""
        ssh = None
        try:
            self.logger.info(f"Testing connection to {self.hostname}")
            ssh = self._create_ssh_client()
            self.logger.info("Connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
        finally:
            if ssh:
                ssh.close()