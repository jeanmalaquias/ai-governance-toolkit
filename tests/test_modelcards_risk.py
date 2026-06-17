from aigovkit.modelcards import ModelCardSpec, load_spec, to_html, to_markdown
from aigovkit.risk import assess, load_answers


def test_model_card_renders_md_and_html():
    spec = ModelCardSpec(
        name="Bot", version="1.0", owner="me", risk_classification="limited",
        intended_use="help", metrics={"faithfulness": 0.9},
        limitations=["stale"], mitigations=["guardrails"],
    )
    md = to_markdown(spec)
    assert "# Model Card — Bot (1.0)" in md
    assert "faithfulness" in md
    html = to_html(spec)
    assert "<title>Model Card — Bot</title>" in html
    assert "0.900" in html


def test_model_card_handles_empty_sections():
    md = to_markdown(ModelCardSpec(name="X", version="0", owner="o"))
    assert "_no metrics reported_" in md
    assert "_none specified_" in md


def test_load_spec(tmp_path):
    p = tmp_path / "s.yaml"
    p.write_text("name: A\nversion: '1'\nowner: o\n")
    assert load_spec(p).name == "A"


def test_risk_green_amber_red():
    base = {q: True for q in [
        "enc_at_rest", "retention", "human_oversight", "input_moderation",
        "output_moderation", "audit_logging", "pii_handling",
    ]}
    assert assess(base).verdict == "green"

    amber = dict(base, human_oversight=False)
    r = assess(amber)
    assert r.verdict == "amber"
    assert r.gaps[0].control == "AIGOV-005"
    assert not r.critical_gaps

    red = dict(base, enc_at_rest=False)
    rr = assess(red)
    assert rr.verdict == "red"
    assert rr.critical_gaps[0].id == "enc_at_rest"


def test_risk_empty_answers_is_red():
    r = assess({})
    assert r.verdict == "red"
    assert r.satisfied == 0
    assert r.total == 7


def test_load_answers(tmp_path):
    p = tmp_path / "a.yaml"
    p.write_text("enc_at_rest: true\n")
    assert load_answers(p) == {"enc_at_rest": True}
    empty = tmp_path / "e.yaml"
    empty.write_text("")
    assert load_answers(empty) == {}
