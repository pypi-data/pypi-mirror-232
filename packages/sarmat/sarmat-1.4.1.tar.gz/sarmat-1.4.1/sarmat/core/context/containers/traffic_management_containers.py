"""
Sarmat.

Описание сущностей.

Контейнеры для описания объектов маршрутной сети.
"""
import datetime
from typing import List, Optional

from pydantic import field_serializer, field_validator, ConfigDict

from sarmat.core.constants import (
    DATE_FORMAT,
    JourneyType,
    RoadType,
    RouteType,
    StationType,
)

from .geo_containers import (
    DestinationPointContainer,
    DirectionContainer,
    RoadNameContainer,
)
from .sarmat_containers import BaseIdSarmatContainer


class StationContainer(BaseIdSarmatContainer):
    """Станции (пункты посадки-высадки пассажиров)"""

    station_type: StationType               # тип станции
    name: str                               # наименование
    point: DestinationPointContainer        # ближайший населенный пункт
    address: str = ""                       # почтовый адрес


class RoadContainer(BaseIdSarmatContainer):
    """Дороги"""

    start_point: DestinationPointContainer          # начало дороги
    end_point: DestinationPointContainer            # конец дороги
    direct_travel_time_min: int                     # время прохождения в прямом направлении
    reverse_travel_time_min: int                    # время прохождения в обратном направлении
    direct_len_km: float                            # расстояние в прямом направлении
    reverse_len_km: float                           # расстояние в обратном направлении
    road_type: RoadType                             # тип дорожного покрытия
    road_name: Optional[RoadNameContainer] = None   # классификация дороги


class RouteItemContainer(BaseIdSarmatContainer):
    """Состав маршрута"""

    length_from_last_km: float                              # расстояние от предыдущего пункта
    travel_time_min: int                                    # время движения от предыдущего пункта в минутах
    road: Optional[RoadContainer] = None                    # дорога
    order: int = 1                                          # порядок следования
    station: Optional[StationContainer] = None              # станция
    point: Optional[DestinationPointContainer] = None       # ближайший населенный пункт
    stop_time_min: Optional[int] = None                     # время стоянки в минутах


class RouteContainer(BaseIdSarmatContainer):
    """Описание маршрута"""

    route_type: RouteType                                       # тип маршрута
    name: str                                                   # наименование
    first_station: StationContainer                             # станция отправления
    structure: List[RouteItemContainer]                         # состав маршрута
    direction: Optional[List[DirectionContainer]] = None        # направления
    comments: Optional[str] = None                              # комментарий к маршруту
    number: Optional[int] = None                                # номер маршрута
    literal: str = ""                                           # литера
    is_active: bool = True                                      # признак активности маршрута


class JourneyContainer(RouteContainer):
    """Атрибуты рейса"""

    journey_type: JourneyType                       # тип рейса
    route_type: RouteType                           # тип маршрута
    departure_time: datetime.time                   # время отправления
    is_chartered: bool = False                      # признак заказного рейса
    need_control: bool = False                      # признак именной продажи и мониторинга
    season_begin: Optional[datetime.date] = None    # начало сезона
    season_end: Optional[datetime.date] = None      # окончание сезона

    @field_validator('season_begin', mode="before")
    @classmethod
    def parse_season_begin(cls, val):
        if val and isinstance(val, str):
            return cls._parse_date(val)
        return val

    @field_validator('season_end', mode="before")
    @classmethod
    def parse_season_end(cls, val):
        if val and isinstance(val, str):
            return cls._parse_date(val)
        return val

    @field_serializer('season_begin')
    def serialize_season_begin(self, season_begin: Optional[datetime.date], _info):
        if season_begin:
            return season_begin.strftime(DATE_FORMAT)

        return None

    @field_serializer('season_end')
    def serialize_season_end(self, season_end: Optional[datetime.date], _info):
        if season_end:
            return season_end.strftime(DATE_FORMAT)

        return None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class JourneyBunchItemContainer(BaseIdSarmatContainer):
    """Атрибуты элемента из связки рейсов"""

    journey: JourneyContainer       # рейс
    stop_interval: int              # время простоя в часах


class JourneyBunchContainer(BaseIdSarmatContainer):
    """Атрибуты связки рейсов"""

    journeys: List[JourneyBunchItemContainer]     # элементы связки
    name: Optional[str] = None                    # наименование связки
