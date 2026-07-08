from app.schemas.lead import DraftEmail, LeadResponse


def test_lead_response_schema_describes_use_case_outputs() -> None:
    schema = LeadResponse.model_json_schema()
    properties = schema["properties"]

    assert "Lead scoring output" in properties["score"]["description"]
    assert "Sales insights" in properties["talking_points"]["description"]
    assert "Public API enrichment" in properties["enrichment"]["description"]
    assert "Review-ready outreach draft" in properties["draft"]["description"]
    assert "Related inbound context" in properties["related_leads"]["description"]
    assert "Graph context" in properties["knowledge_graph"]["description"]


def test_draft_schema_describes_cited_personalization_sources() -> None:
    schema = DraftEmail.model_json_schema()

    assert "Review-ready inbound outreach body" in (
        schema["properties"]["body"]["description"]
    )
    assert "Source facts that support draft personalization claims" in (
        schema["properties"]["sources"]["description"]
    )
