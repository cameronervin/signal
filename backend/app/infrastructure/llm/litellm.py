from app.core.config import Settings
from app.schemas.lead import DraftEmail, Enrichment, LeadCreate


class LiteLLMProvider:
    provider_name = "litellm"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def draft_outreach(
        self,
        *,
        lead: LeadCreate,
        enrichment: Enrichment,
        instructions: str,
    ) -> DraftEmail | None:
        import litellm

        response = await litellm.acompletion(
            model=self.settings.llm_model,
            api_base=self.settings.litellm_api_base,
            api_key=self.settings.litellm_api_key,
            messages=[
                {"role": "system", "content": instructions.strip()},
                {
                    "role": "user",
                    "content": (
                        "Draft a concise SDR-reviewed email for this lead using "
                        "only these facts.\n\n"
                        f"Lead: {lead.model_dump(mode='json')}\n"
                        f"Enrichment: {enrichment.model_dump(mode='json')}"
                    ),
                },
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        if not content:
            return None
        return DraftEmail(
            subject=f"Improving leasing response in {lead.city}",
            body=content,
            sources=enrichment.sources,
        )
