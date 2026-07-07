"""Tool-specific prompt snippets for Signal agent chains."""

from typing import NamedTuple


class ToolPromptKey(NamedTuple):
    """Identify a prompt snippet by chain and tool name."""

    chain: str
    tool_name: str


GEOCODING_PROMPT = """
<tools>
- **geocode_property_address**:
Use this only when the baseline address or market context is missing, ambiguous,
or worth verifying before drafting. Do not use it to change score, tier, or gate
status.
</tools>
"""

CENSUS_PROMPT = """
<tools>
- **fetch_census_market_demographics**:
Use this for renter share, median rent, or household count evidence about the
lead's market when the baseline context is thin. Cite returned source facts only.
</tools>
"""

DATAUSA_PROMPT = """
<tools>
- **fetch_datausa_household_growth**:
Use this for household-growth context at the lead's state level when it would
improve personalization. Cite returned source facts only.
</tools>
"""

FRED_PROMPT = """
<tools>
- **fetch_fred_market_economics**:
Use this for rent-growth or unemployment context when available. If the tool says
economic data is unavailable, continue from baseline facts.
</tools>
"""

NEWS_PROMPT = """
<tools>
- **lookup_news_company_trigger**:
Use this to look for one recent company trigger before mentioning urgency or
momentum. If no trigger is found, do not imply one.
</tools>
"""

WIKIPEDIA_PROMPT = """
<tools>
- **lookup_wikipedia_company_background**:
Use this for concise company background evidence. Do not overstate Wikipedia
summaries as qualification proof.
</tools>
"""

DOMAIN_PROMPT = """
<tools>
- **validate_email_domain_mx**:
Use this only to verify whether the lead email domain has MX records. Do not ask
for or expose full email addresses.
</tools>
"""

TOOL_PROMPT_REGISTRY: dict[ToolPromptKey, str] = {
    ToolPromptKey("outreach_draft", "geocode_property_address"): GEOCODING_PROMPT,
    ToolPromptKey(
        "outreach_draft",
        "fetch_census_market_demographics",
    ): CENSUS_PROMPT,
    ToolPromptKey(
        "outreach_draft",
        "fetch_datausa_household_growth",
    ): DATAUSA_PROMPT,
    ToolPromptKey("outreach_draft", "fetch_fred_market_economics"): FRED_PROMPT,
    ToolPromptKey("outreach_draft", "lookup_news_company_trigger"): NEWS_PROMPT,
    ToolPromptKey(
        "outreach_draft",
        "lookup_wikipedia_company_background",
    ): WIKIPEDIA_PROMPT,
    ToolPromptKey("outreach_draft", "validate_email_domain_mx"): DOMAIN_PROMPT,
}
