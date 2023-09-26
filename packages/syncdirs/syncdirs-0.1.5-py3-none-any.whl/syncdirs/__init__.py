import filecmp
import logging
import shutil
from datetime import datetime
from pathlib import Path


class SyncDir:
    def __init__(
        self,
        source: str,
        replica: str,
        log_file: str,
        last_sync: datetime | None = None,
    ):
        # setup logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] - %(name)s: %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
        )
        # init values
        self.source = Path(source)
        self.replica = Path(replica)
        self.last_sync = last_sync

        # resolve the absolute paths
        self.source = self.source.resolve()
        self.replica = self.replica.resolve()

        # check if replica is not a subdirectory
        if self.replica.parts[: len(self.source.parts)] == self.source.parts:
            raise ValueError("Replica cannot be a subdirectory!")

    def sync(self) -> None:
        """
        The `sync` function synchronizes the source and replica objects and
        updates the last_sync attribute with the current datetime.
        """
        self._sync(self.source, self.replica)
        self.last_sync = datetime.now()
        logging.debug(f"Set last sync time to {self.last_sync}")

    def _sync(self, source: Path, replica: Path) -> None:
        """
        The `_sync` function checks if directories have been modified since the
        last sync, and if so, it syncs them.

        Args:
            source (Path): The path to the source file or directory.
            replica (Path): The path to the replica file or directory.
        """
        # check if dirs were updated since last sync
        if not self.is_modified(source, replica):
            logging.debug(f"The {source} and {replica} were not modified")
            return
        # source path is file
        if source.is_file():
            if not (replica.is_file() and filecmp.cmp(source, replica)):
                self.copy(source, replica)
                logging.debug(f"File {source} is NOT same as {replica}")
            else:
                logging.debug(f"File {source} is same as {replica}")
        # source path is dir
        elif source.is_dir():
            if replica.is_dir():
                # sync items in dirs
                source_items = set(item.name for item in source.iterdir())
                replica_items = set(item.name for item in replica.iterdir())
                for item in source_items | replica_items:
                    self._sync(source / item, replica / item)
            else:
                logging.debug(f"Directory {source} is NOT same as {replica}")
                self.copy(source, replica)
        # source path does not exist
        else:
            logging.debug(f"The source path {source} does NOT exist")
            self.remove(replica)

    def is_modified(self, source: Path, replica: Path) -> bool:
        """
        The function checks if the source and replica files have been modified
        since the last synchronization.

        Args:
            source (Path): The path to the source file or directory.
            replica (Path): The path to the replica file or directory.

        Returns:
            a boolean value. If the conditions specified in the if statement
            are met, it will return False. Otherwise, it will return True.
        """
        if (
            self.last_sync
            and source.exists()
            and datetime.fromtimestamp(source.stat().st_mtime) < self.last_sync
            and replica.exists()
            and datetime.fromtimestamp(replica.stat().st_mtime)
            < self.last_sync
        ):
            return False
        return True

    def remove(self, path: Path) -> None:
        """
        The `remove` function removes a directory if the given path is a
        directory, or removes a file if the given path is a file, and logs the
        action.

        Args:
            path (Path): The `path` parameter is of type `Path` and represents
        the path to the file or directory that needs to be removed.
        """
        if path.is_dir():
            shutil.rmtree(path)
            logging.info(f"Removing directory: {path}")
        elif path.is_file():
            path.unlink()
            logging.info(f"Removing file: {path}")

    def copy(self, source: Path, destination: Path) -> None:
        """
        The function copies a file or directory from a source path to a
        destination path, logging the action.

        Args:
            source (Path): The `source` parameter is the path to the file or
        directory that you want to copy.
            destination (Path): The `destination` parameter is the path where
        the source file or directory will be copied to.
        """
        self.remove(destination)
        if source.is_dir():
            shutil.copytree(source, destination)
            logging.info(f"Copying directory: {source} to {destination}")
        elif source.is_file():
            shutil.copy2(source, destination)
            logging.info(f"Copying file: {source} to {destination}")
