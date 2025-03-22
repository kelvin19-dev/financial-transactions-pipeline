import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalSFTPClient:
    def __init__(self, local_dir):
        """Emulate an SFTP server using a local directory."""
        self.local_dir = os.path.abspath(local_dir)
        os.makedirs(self.local_dir, exist_ok=True)  # Ensure the directory exists
        logger.info(f"Using local directory as SFTP: {self.local_dir}")

    def list_files(self, extensions=None):
        """List files in the local 'SFTP' directory, filtering by extensions if provided."""
        try:
            files = os.listdir(self.local_dir)
            if extensions:
                files = [f for f in files if any(f.endswith(ext) for ext in extensions)]
            logger.info(f"Found {len(files)} files in local directory")
            return files
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            return []

    def download_file(self, file_name, local_dir):
        """Copy a file from the local 'SFTP' directory to another local directory."""
        src_path = os.path.join(self.local_dir, file_name)
        dest_path = os.path.join(local_dir, file_name)

        if not os.path.exists(src_path):
            logger.error(f"File not found: {src_path}")
            return None

        os.makedirs(local_dir, exist_ok=True)  # Ensure destination exists
        try:
            with open(src_path, "rb") as src, open(dest_path, "wb") as dest:
                dest.write(src.read())
            logger.info(f"Copied {file_name} to {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to copy {file_name}: {str(e)}")
            return None

    def download_all_files(self, local_dir, extensions=None):
        """Copy all files from the local 'SFTP' directory to another local directory."""
        files = self.list_files(extensions)
        downloaded_files = []

        for file in files:
            local_path = self.download_file(file, local_dir)
            if local_path:
                downloaded_files.append(local_path)

        return downloaded_files
    def close(self):
        """Dummy close method for LocalSFTPClient."""
        logger.info("LocalSFTPClient: No connection to close.")
# Usage Example
def get_mock_sftp_client():
    """Create a mock SFTP client that uses a local directory."""
    return LocalSFTPClient(local_dir="./data")
