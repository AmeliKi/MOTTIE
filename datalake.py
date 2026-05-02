"""Azure Data Lake (Gen2) upload helper."""

import logging
import os

from azure.storage.filedatalake import DataLakeServiceClient

from config import STORAGE_ACCOUNT_KEY, STORAGE_ACCOUNT_NAME

logger = logging.getLogger(__name__)


class DataLake:
    """Thin wrapper around `DataLakeServiceClient` for single-file uploads."""

    def __init__(self) -> None:
        account_url = f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net"
        self.service_client = DataLakeServiceClient(
            account_url=account_url, credential=STORAGE_ACCOUNT_KEY
        )

    def upload_file_to_directory(self, container: str, directory: str, filename: str) -> None:
        """Upload `filename` (a local path) to `<container>/<directory>/<basename>`."""
        try:
            file_system_client = self.service_client.get_file_system_client(file_system=container)
            directory_client = file_system_client.get_directory_client(directory)
            file_client = directory_client.create_file(os.path.basename(filename))
            with open(filename, "rb") as local_file:
                file_contents = local_file.read()
            file_client.append_data(data=file_contents, offset=0, length=len(file_contents))
            file_client.flush_data(len(file_contents))
        except Exception:
            logger.exception("Failed to upload %s to %s/%s", filename, container, directory)
