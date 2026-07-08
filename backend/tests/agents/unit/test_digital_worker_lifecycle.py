from app.agents.context.digital_worker_lifecycle import load_default_lifecycle_spec


def test_default_digital_worker_lifecycle_spec_is_valid() -> None:
    spec = load_default_lifecycle_spec()

    assert spec.version == "qualify_to_meeting.v1"
    assert spec.initial_phase == "initial_outreach"
    assert spec.phase("initial_outreach").goals[0].key == "send_existing_draft"
    assert spec.next_phase_key("initial_outreach") == "reply_qualification"
