"""
Sarmat.

Описание сущностей.

Контейнеры для описания объектов подвижного состава и экипажа.
"""
import datetime
from typing import List

from pydantic import field_serializer, field_validator

from sarmat.core.constants import (
    CrewType,
    DATE_FORMAT,
    PermitType,
    VehicleType,
)

from .sarmat_containers import (
    BaseIdSarmatContainer,
    BasePersonSarmatContainer,
    BaseUidSarmatContainer,
)


class VehicleContainer(BaseIdSarmatContainer):
    """Подвижной состав"""

    vehicle_type: VehicleType   # тип транспортного средства
    vehicle_name: str           # марка транспортного средства
    state_number: str           # гос. номер
    seats: int                  # количество мест для посадки
    stand: int = 0              # количество мест стоя
    capacity: int = 0           # вместимость багажного отделения


class CrewContainer(BasePersonSarmatContainer, BaseIdSarmatContainer):
    """Экипаж"""

    crew_type: CrewType     # тип члена экипажа
    is_main: bool = True    # признак главного члена экипажа


class PermitContainer(BaseUidSarmatContainer):
    """Путевой лист"""

    number: str                         # номер путевого листа
    permit_type: PermitType             # тип путевого листа
    depart_date: datetime.date          # дата выезда
    crew: List[CrewContainer]           # экипаж
    vehicle: List[VehicleContainer]     # подвижной состав

    @field_validator('depart_date', mode="before")
    @classmethod
    def parse_depart_date(cls, val):
        if val and isinstance(val, str):
            return cls._parse_date(val)
        return val

    @field_serializer('depart_date')
    def serialize_depart_date(self, depart_date: datetime.date, _info):
        return depart_date.strftime(DATE_FORMAT)

    @field_serializer('permit_type')
    def serialize_permit_type(self, permit_type: PermitType, _info):
        return permit_type.value
