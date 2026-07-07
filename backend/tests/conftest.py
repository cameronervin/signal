from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def mock_litellm_completion(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_acompletion(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=(
                            "Hi Sarah,\n\n"
                            "Public market data points to a strong leasing "
                            "opportunity. Worth comparing your inbound response "
                            "motion this week?"
                        )
                    )
                )
            ]
        )

    monkeypatch.setattr("litellm.acompletion", fake_acompletion)
