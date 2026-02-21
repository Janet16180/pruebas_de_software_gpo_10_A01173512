"""Base manager for JSON-persisted dataclass entities."""

import dataclasses
import json
import logging
from pathlib import Path
from typing import Any, ClassVar, Optional

logger = logging.getLogger(__name__)


class EntityManager:
    """Base manager for dataclass entity persistence.

    Subclasses must define ``_prefix``, ``_id_attr``,
    and ``_entity_cls`` class variables.
    """

    _prefix: ClassVar[str]
    _id_attr: ClassVar[str]
    _entity_cls: ClassVar[type]

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
    ) -> None:
        self._storage_dir = storage_dir or Path(".")

    def _filepath(self, entity_id: int) -> Path:
        """Return the JSON file path for an entity.

        Parameters
        ----------
        entity_id : int
            The entity's unique identifier.

        Returns
        -------
        Path
            Path to the entity's JSON file.
        """
        return self._storage_dir / f"{self._prefix}_{entity_id}.json"

    def to_dict(self, entity: Any) -> dict[str, Any]:  # noqa: ANN401
        """Serialize an entity to a dictionary.

        Parameters
        ----------
        entity : Any
            Dataclass instance to serialize.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the entity.
        """
        return dataclasses.asdict(entity)

    def from_dict(
        self,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        """Deserialize an entity from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary with entity attributes.

        Returns
        -------
        Any
            Reconstructed dataclass instance.
        """
        init_fields = {
            f.name for f in dataclasses.fields(self._entity_cls) if f.init
        }
        init_data = {k: v for k, v in data.items() if k in init_fields}
        instance = self._entity_cls(**init_data)
        for dc_field in dataclasses.fields(
            self._entity_cls,
        ):
            if not dc_field.init and dc_field.name in data:
                setattr(
                    instance,
                    dc_field.name,
                    data[dc_field.name],
                )
        return instance

    def save(self, entity: Any) -> bool:  # noqa: ANN401
        """Persist an entity to a JSON file.

        Parameters
        ----------
        entity : Any
            Dataclass instance to save.

        Returns
        -------
        bool
            True if saved successfully, False otherwise.
        """
        entity_id = getattr(entity, self._id_attr)
        try:
            with open(
                self._filepath(entity_id),
                "w",
                encoding="utf-8",
            ) as fh:
                json.dump(
                    self.to_dict(entity),
                    fh,
                    indent=2,
                )
            return True
        except OSError as exc:
            logger.error(
                "Failed to save %s %d: %s",
                self._prefix,
                entity_id,
                exc,
            )
            return False

    def load(self, entity_id: int) -> Optional[Any]:  # noqa: ANN401
        """Load an entity from its JSON file.

        Parameters
        ----------
        entity_id : int
            The entity ID to load.

        Returns
        -------
        Any or None
            The loaded entity, or None if failed.
        """
        try:
            with open(
                self._filepath(entity_id),
                "r",
                encoding="utf-8",
            ) as fh:
                data = json.load(fh)
            return self.from_dict(data)
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
        ) as exc:
            logger.error(
                "Failed to load %s %d: %s",
                self._prefix,
                entity_id,
                exc,
            )
            return None

    def delete(self, entity: Any) -> bool:  # noqa: ANN401
        """Delete an entity's JSON file from disk.

        Parameters
        ----------
        entity : Any
            Dataclass instance to delete.

        Returns
        -------
        bool
            True if deleted successfully, False otherwise.
        """
        entity_id = getattr(entity, self._id_attr)
        try:
            self._filepath(entity_id).unlink()
            return True
        except OSError as exc:
            logger.error(
                "Failed to delete %s %d: %s",
                self._prefix,
                entity_id,
                exc,
            )
            return False
