from enum import Enum
from dataclasses import dataclass
from typing import List


class ConstellationId(Enum):
    GPS: str = 'G'
    GALILEO: str = 'E'
    GLONASS: str = 'R'
    BEIDOU: str = 'C'
    QZSS: str = 'J'
    IRNSS: str = 'I'
    SBAS: str = 'S'

    @staticmethod
    def from_string(constellation_char: str) -> 'ConstellationId':
        """
        Returns the corresponding ConstellationId from input character

        >>> ConstellationId.from_string('E')
        <ConstellationId.GALILEO: 'E'>
        """
        try:
            return ConstellationId(constellation_char)
        except ValueError:
            raise ValueError(f"Invalid constellation character: {constellation_char}")

    def to_char(self):
        """
        Constellation representation as character

        >>> c = ConstellationId.GPS
        >>> c.to_char()
        'G'
        """

        return self.value

    def __lt__(self, other):
        """
        Less operator for the ConstellationId class

        >>> c1 = ConstellationId.GPS
        >>> c2 = ConstellationId.IRNSS
        >>> c1 < c2
        True
        >>> c2 < c1
        False
        >>> c2 < 0
        Traceback (most recent call last):
        ...
        TypeError: '<' not supported between instances of 'ConstellationId' and 'int'
        """

        if isinstance(other, ConstellationId):
            return self.value < other.value
        return NotImplemented


class Band:
    """
    Namespace to define the supported bands (center frequency in Hz)
    """

    L1 = 1575420000
    L2 = 1227600000
    L5 = 1176450000
    L6 = 1278750000
    G1 = 1602000000
    G1a = 1600995000
    G2 = 1246000000
    G2a = 1248060000
    G3 = 1202025000
    E1 = 1575420000
    E5a = 1176450000
    E5b = 1207140000
    E5 = 1191795000
    E6 = 1278750000
    B1_2 = 1561098000
    B1 = 1575420000
    B2a = 1176450000
    B2b = 1207140000
    B2 = 1191795000
    B3 = 1268520000
    S = 2492028000

    def __init__(self):
        """
        Init the class (does nothing)
        """
        pass


@dataclass
class TrackingChannel(object):
    band: int
    attribute: str

    @staticmethod
    def from_observable_type(observable_type: str) -> 'TrackingChannel':
        band = int(observable_type[1])
        attribute = observable_type[2]
        return TrackingChannel(band, attribute)

    def __eq__(self, other: 'TrackingChannel') -> bool:
        return self.band == other.band and self.attribute == other.attribute

    def __lt__(self, other: 'TrackingChannel') -> bool:
        return self.attribute < other.attribute if self.band == other.band else self.band < other.band

    def __repr__(self):
        return f'{self.band:1d}{self.attribute:1s}'

    def __hash__(self) -> int:
        return hash((self.band, self.attribute))


INVALID_TRACKING_CHANNEL = TrackingChannel(0, '0')


class ChannelCode(Enum):
    c_1C: str = "1C"
    c_5Q: str = "5Q"


@dataclass
class Satellite:
    constellation: ConstellationId
    prn: int

    @staticmethod
    def from_string(satellite: str) -> 'Satellite':
        constellation = ConstellationId.from_string(satellite[0])
        prn = int(satellite[1:3])
        return Satellite(constellation, prn)

    def __lt__(self, other: 'Satellite') -> bool:
        return self.prn < other.prn if self.constellation == other.constellation else self.constellation < other.constellation

    def __eq__(self, other: 'Satellite') -> bool:
        return self.constellation == other.constellation and self.prn == other.prn

    def __hash__(self):
        return hash(self.constellation) + self.prn

    def __repr__(self) -> str:
        return f"{self.constellation.value:1s}{self.prn:02d}"


@dataclass
class Signal:
    satellite: Satellite
    channel: ChannelCode

    def __repr__(self) -> str:
        return f"{self.satellite}{self.channel.value}"


class GnssSystem:
    constellation_id: ConstellationId
    number_satellites: int
    channels: List[ChannelCode]
    signals: List[Signal]

    def __init__(self, constellation_id: ConstellationId, number_satellites: int, channels: List[ChannelCode]):
        self.constellation_id = constellation_id
        self.number_satellites = number_satellites
        self.channels = channels
        self.signals = self.get_signals()

    def get_signals(self) -> List[Signal]:
        signals = []
        for index in range(1, self.number_satellites + 1):
            for channel in self.channels:
                signals.append(Signal(Satellite(self.constellation_id, index), channel))

        return signals


@dataclass
class GnssSystems:
    gnss_systems: List[GnssSystem]

    def get_constellations(self) -> List[str]:
        return [system.constellation_id.value for system in self.gnss_systems]

    def get_signals(self) -> List[Signal]:
        signals = []
        for system in self.gnss_systems:
            signals.extend(system.get_signals())
        return signals
