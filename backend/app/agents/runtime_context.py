from dataclasses import dataclass

from app.core.config import Settings
from app.infrastructure.public_data import PublicDataClient


@dataclass(frozen=True, slots=True)
class SignalRuntimeContext:
    settings: Settings
    public_data_client: PublicDataClient
