from enum import StrEnum, auto


class BudgetStatus(StrEnum):
    ACTIVE = auto()      # En edición
    CLOSED = auto()      # Cerrado, no se puede editar
    ARCHIVED = auto()    # Archivado, solo consulta