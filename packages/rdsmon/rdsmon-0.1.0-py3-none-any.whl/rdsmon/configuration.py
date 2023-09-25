from dataclasses import dataclass


@dataclass
class Configuration:
    """Encapsulation of the runtime configuration."""

    region: str
    period: int
