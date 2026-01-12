from enum import StrEnum, auto


class SplitType(StrEnum):
    EQUAL = auto()              # 50/50 (o partes iguales si >2 personas)
    PROPORTIONAL = auto()       # Según ingresos mensuales
    CUSTOM = auto()             # Porcentajes personalizados
    FULL_SINGLE = auto()        # 100% una persona, 0% las demás