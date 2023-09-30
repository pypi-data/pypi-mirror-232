"""
Sarmat.

Описание сущностей.

Объекты для расчета стоимости.
"""
from typing import Any, Dict

from dataclasses import asdict, dataclass, field
from decimal import Decimal

from sarmat.core.behavior import BhRoute


@dataclass
class FareContainer:
    base_passenger_price: Decimal
    base_baggage_price: Decimal
    permanent_passenger_price: Decimal = Decimal(0)
    volatile_passenger_price: Decimal = Decimal(0)
    permanent_baggage_price: Decimal = Decimal(0)
    volatile_baggage_price: Decimal = Decimal(0)
    custom_passenger_price: Dict[Any, Any] = field(default_factory=dict)
    custom_baggage_price: Dict[Any, Any] = field(default_factory=dict)

    def _check_attribute(self, item, item_type):
        if item is not None:
            if not isinstance(item, item_type):
                item = item_type(item)

        return item

    def __post_init__(self):
        self.base_passenger_price = self._check_attribute(self.base_passenger_price, Decimal)
        self.base_baggage_price = self._check_attribute(self.base_baggage_price, Decimal)
        self.permanent_passenger_price = self._check_attribute(self.permanent_passenger_price, Decimal)
        self.volatile_passenger_price = self._check_attribute(self.volatile_passenger_price, Decimal)
        self.permanent_baggage_price = self._check_attribute(self.permanent_baggage_price, Decimal)
        self.volatile_baggage_price = self._check_attribute(self.volatile_baggage_price, Decimal)


@dataclass
class FareArguments:
    route: BhRoute
    point_from: int
    point_to: int
    other_arguments: dict
    base_pas_price: Decimal = field(default_factory=Decimal)
    base_bag_price: Decimal = field(default_factory=Decimal)
    prm_pas_price: Decimal = field(default_factory=Decimal)
    prm_bag_price: Decimal = field(default_factory=Decimal)
    vlt_pas_price: Decimal = field(default_factory=Decimal)
    vlt_bag_price: Decimal = field(default_factory=Decimal)
    customer_pas_price: Dict[Any, Any] = field(default_factory=dict)
    customer_bag_price: Dict[Any, Any] = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)
