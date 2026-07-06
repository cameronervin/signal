from dataclasses import dataclass


@dataclass(frozen=True)
class PublicDataClientConfig:
    use_fixtures: bool = True
    news_api_key: str | None = None
    fred_api_key: str | None = None


class PublicDataClient:
    """Placeholder boundary for live public API adapters.

    The initial scaffold uses deterministic fixtures in `app.agents.fixtures`.
    Live adapters should be added behind this class or split into focused
    geocoding, census, economics, news, and domain-validation clients.
    """

    def __init__(self, config: PublicDataClientConfig) -> None:
        self.config = config
