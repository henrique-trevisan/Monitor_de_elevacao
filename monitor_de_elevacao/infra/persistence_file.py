from typing import Dict, Any
from pathlib import Path
import json

class PersistenceFile:
    """
    Responsible for handle persistence file:
        - Checking directory
        - Checking file existence
        - Saving file
        - Loading file
    """

    def __init__(self) -> None:
        """
        Initialize the folder and file name to save the persistence data
        """
        
        self.APP_DIR_NAME = "CircuitBreakerMonitor"
        self.CONFIG_FILE_NAME = "config.json"
        self.persistence_dir = None
        self.persistence_file = None

        # Get the persistence directory and file path
        self.get_persistence_dir()
        self.get_persistence_file()
    
    def _get_documents_dir(self) -> Path:
        """
        Try to find the user 'Documents' folder, independent of Windows language.
        Fallback to home if nothing matches.
        """

        # Default home path
        home = Path.home()

        # Candidates for the documents folder
        candidates = [
            home / "Documents",
            home / "My documents",
            home / "Documentos",
            home / "Meus documentos"
        ]

        # If a candidate exists, return that path
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        # If there is no candidate, return the default
        return home
    
    def get_persistence_dir(self) -> Path:
        """
        Directory where the app will store its persistent data.
        """

        documents_dir = self._get_documents_dir()
        self.persistence_dir = documents_dir / self.APP_DIR_NAME
        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        return self.persistence_dir

    def get_persistence_file(self) -> Path:
        """
        Full path to the JSON config file
        """

        self.persistence_file = self.persistence_dir / self.CONFIG_FILE_NAME
        return self.persistence_file
    
    def save_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """
        Save the snapshot to disk as a JSON file.
        """

        with self.persistence_file.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

    def load_snapshot(self) -> Dict[str, Any] | None:
        """
        Load snapshot from disk (if exists).
        Return None if file doesn't exist or is invalid
        """
        
        # If the file does not exists, return None
        if not self.persistence_file.exists():
            return None
        
        # Try to open the file
        try:

            # Reads the file as a JSON file
            with self.persistence_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Checks if the data is a dictionary
            if isinstance(data, dict):
                return data
            return None

        # In case the file is a corrupted JSON
        except json.JSONDecodeError:
            return None