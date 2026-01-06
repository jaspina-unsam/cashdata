from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    """
    Domain entity representing an expense category.

    Invariants:
    - name must not be empty or only whitespace
    - name length must be between 1-50 characters
    - id can be None (before persistence)
    """

    id: int | None
    name: str
    color: str | None = None
    icon: str | None = None

    def __post_init__(self):
        """Validate invariants after initialization"""
        # Validate name is not empty
        if not self.name or not self.name.strip():
            raise ValueError("Category name cannot be empty")

        # Normalize whitespace
        stripped_name = self.name.strip()
        if stripped_name != self.name:
            object.__setattr__(self, "name", stripped_name)

        # Validate name length
        if len(self.name) > 50:
            raise ValueError("Category name cannot exceed 50 characters")

    def __eq__(self, other):
        """Categories are equal if they have the same ID"""
        if not isinstance(other, Category):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self):
        """Allow Category to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
