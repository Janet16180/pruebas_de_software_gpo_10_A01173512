"""Customer entity and manager."""

from dataclasses import dataclass
from typing import ClassVar, Optional

from persistence import EntityManager


@dataclass
class Customer:
    """Customer data.

    Parameters
    ----------
    customer_id : int
        Unique identifier for the customer.
    name : str
        Full name of the customer.
    email : str
        Email address of the customer.
    """

    customer_id: int
    name: str
    email: str


class CustomerManager(EntityManager):
    """Manager for Customer persistence and operations."""

    _prefix: ClassVar[str] = "customer"
    _id_attr: ClassVar[str] = "customer_id"
    _entity_cls: ClassVar[type] = Customer

    def create(
        self,
        customer_id: int,
        name: str,
        email: str,
    ) -> Optional[Customer]:
        """Create a new customer and persist to disk.

        Parameters
        ----------
        customer_id : int
            Unique identifier for the customer.
        name : str
            Full name of the customer.
        email : str
            Email address of the customer.

        Returns
        -------
        Customer or None
            The created customer, or None if failed.

        Raises
        ------
        ValueError
            If customer_id is not positive or
            name/email are empty.
        """
        if customer_id <= 0:
            raise ValueError(
                f"customer_id must be positive, got {customer_id}",
            )
        if not name:
            raise ValueError("name must not be empty")
        if not email:
            raise ValueError("email must not be empty")
        customer = Customer(customer_id, name, email)
        if self.save(customer):
            return customer
        return None

    def display_info(self, customer: Customer) -> str:
        """Return a human-readable summary.

        Parameters
        ----------
        customer : Customer
            Customer instance to display.

        Returns
        -------
        str
            Formatted customer information string.
        """
        return (
            f"Customer {customer.name}"
            f" (ID: {customer.customer_id})\n"
            f"  Email: {customer.email}"
        )

    def modify_info(
        self,
        customer: Customer,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        """Update customer attributes and persist changes.

        Parameters
        ----------
        customer : Customer
            Customer instance to modify.
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
            customer.name = name
        if email is not None:
            customer.email = email
        return self.save(customer)
