from asperitas_agent.compliance import scan_compliance


def test_cites_nagoya_lmo_queries_trigger_compliance():
    assert scan_compliance("CITES protected species export permit").compliance_flag
    assert scan_compliance("Nagoya ABS genetic resource access").compliance_flag
    assert scan_compliance("LMO GMO regulatory filing").compliance_flag


def test_wet_lab_protocol_requires_human_approval():
    result = scan_compliance("Give a wet-lab plasmid transformation protocol")

    assert result.compliance_flag
    assert result.human_approval_required
    assert "wet_lab" in result.risk_tags


def test_normal_strategy_query_does_not_block():
    result = scan_compliance("What is the source hierarchy for internal strategy?")

    assert not result.compliance_flag
    assert not result.human_approval_required
