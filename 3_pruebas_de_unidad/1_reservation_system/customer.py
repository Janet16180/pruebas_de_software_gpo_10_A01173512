"""Customer entity with JSON file persistence."""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from persistence import PersistentEntity


@dataclass
class Customer(PersistentEntity):
    """Represent a hotel customer.

    Parameters
    ----------
    customer_id : int
        Unique identifier for the customer.
    name : str
        Full name of the customer.
    email : str
        Email address of the customer.
    """

    _prefix: ClassVar[str] = "customer"
    _id_attr: ClassVar[str] = "customer_id"

    customer_id: int
    name: str
    email: str

    @classmethod
    def create(
        cls,
        customer_id: int,
        name: str,
        email: str,
        *,
        storage_dir: Optional[Path] = None,
    ) -> Optional["Customer"]:
        """Create a new customer and persist to disk.

        Parameters
        ----------
        customer_id : int
            Unique identifier for the customer.
        name : str
            Full name of the customer.
        email : str
            Email address of the customer.
        storage_dir : Path, optional
            Directory for JSON file persistence.

        Returns
        -------
        Customer or None
            The created customer, or None if failed.
        """
        customer = cls(customer_id, name, email)
        customer._storage_dir = storage_dir or Path(".")
        if customer.save():
            return customer
        return None

    def display_info(self) -> str:
        """Return a human-readable summary of the customer.

        Returns
        -------
        str
            Formatted customer information string.
        """
        return (
            f"Customer {self.name}"
            f" (ID: {self.customer_id})\n"
            f"  Email: {self.email}"
        )

    def modify_info(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        """Update customer attributes and persist changes.

        Parameters
        ----------
        name : str, optional
            New name for the customer.
        email : str, optional
            New email for the customer.

        Returns
        -------
        bool
            True if modifications were saved.
        """
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        return self.save()
