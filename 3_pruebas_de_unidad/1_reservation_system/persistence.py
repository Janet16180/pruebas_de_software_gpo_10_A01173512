"""Base class for JSON-persisted entities."""

import dataclasses
import json
import logging
from pathlib import Path
from typing import Any, ClassVar, Optional

logger = logging.getLogger(__name__)


class PersistentEntity:
    """Base for entities persisted as JSON files.

    Subclasses must be decorated with ``@dataclass`` and
    define ``_prefix`` and ``_id_attr`` class variables.
    """

    _prefix: ClassVar[str]
    _id_attr: ClassVar[str]
    _storage_dir: Path = Path(".")

    def _filepath(self) -> Path:
        """Return the JSON file path for this entity.

        Returns
        -------
        Path
            Path to the entity's JSON file.
        """
        entity_id = getattr(self, self._id_attr)
        return self._storage_dir / f"{self._prefix}_{entity_id}.json"

    def to_dict(self) -> dict[str, Any]:
        """Serialize entity to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the entity.
        """
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        storage_dir: Optional[Path] = None,
    ) -> "PersistentEntity":
        """Deserialize an entity from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary with entity attributes.
        storage_dir : Path, optional
            Directory for JSON file persistence.

        Returns
        -------
        PersistentEntity
            Reconstructed entity instance.
        """
        init_fields = {f.name for f in dataclasses.fields(cls) if f.init}
        init_data = {k: v for k, v in data.items() if k in init_fields}
        instance = cls(**init_data)
        for dc_field in dataclasses.fields(cls):
            if not dc_field.init and dc_field.name in data:
                setattr(
                    instance,
                    dc_field.name,
                    data[dc_field.name],
                )
        instance._storage_dir = storage_dir or Path(".")
        return instance

    def save(self) -> bool:
        """Persist entity data to a JSON file.

        Returns
        -------
        bool
            True if saved successfully, False otherwise.
        """
        try:
            with open(
                self._filepath(),
                "w",
                encoding="utf-8",
            ) as fh:
                json.dump(self.to_dict(), fh, indent=2)
            return True
        except OSError as exc:
            logger.error(
                "Failed to save %s %d: %s",
                self._prefix,
                getattr(self, self._id_attr),
                exc,
            )
            return False

    @classmethod
    def load(
        cls,
        entity_id: int,
        *,
        storage_dir: Optional[Path] = None,
    ) -> Optional["PersistentEntity"]:
        """Load an entity from its JSON file.

        Parameters
        ----------
        entity_id : int
            The entity ID to load.
        storage_dir : Path, optional
            Directory where the JSON file is stored.

        Returns
        -------
        PersistentEntity or None
            The loaded entity, or None if loading failed.
        """
        sdir = storage_dir or Path(".")
        filepath = sdir / f"{cls._prefix}_{entity_id}.json"
        try:
            with open(
                filepath,
                "r",
                encoding="utf-8",
            ) as fh:
                data = json.load(fh)
            return cls.from_dict(data, storage_dir=sdir)
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
        ) as exc:
            logger.error(
                "Failed to load %s %d: %s",
                cls._prefix,
                entity_id,
                exc,
            )
            return None

    def delete(self) -> bool:
        """Delete the entity's JSON file from disk.

        Returns
        -------
        bool
            True if deleted successfully, False otherwise.
        """
        try:
            self._filepath().unlink()
            return True
        except OSError as exc:
            logger.error(
                "Failed to delete %s %d: %s",
                self._prefix,
                getattr(self, self._id_attr),
                exc,
            )
            return False
