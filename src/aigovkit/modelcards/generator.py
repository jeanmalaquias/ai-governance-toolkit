"""Model card generator.

A typed ``ModelCardSpec`` renders to Markdown and standalone HTML. Satisfies the
transparency controls (EU AI Act Art. 13, ISO/IEC 42001 A.8.2).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from jinja2 import Template
from pydantic import BaseModel, Field

RiskClass = str  # prohibited | high | limited | minimal


class ModelCardSpec(BaseModel):
    """The input spec for a model card."""

    name: str
    version: str
    owner: str
    risk_classification: RiskClass = "limited"
    base_models: list[str] = Field(default_factory=list)
    intended_use: str = ""
    out_of_scope: list[str] = Field(default_factory=list)
    training_data: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    contact: str = ""


_MARKDOWN = Template(
    """# Model Card — {{ s.name }} ({{ s.version }})

- **Owner:** {{ s.owner }}
- **Risk classification:** {{ s.risk_classification }}
- **Base models:** {{ s.base_models | join(", ") or "n/a" }}
- **Contact:** {{ s.contact or "n/a" }}

## Intended use
{{ s.intended_use or "_not specified_" }}

### Out of scope
{% for x in s.out_of_scope %}- {{ x }}
{% else %}_none specified_
{% endfor %}
## Training data
{% for x in s.training_data %}- {{ x }}
{% else %}_not specified_
{% endfor %}
## Evaluation
{% for k, v in s.metrics.items() %}- **{{ k }}:** {{ "%.3f" | format(v) }}
{% else %}_no metrics reported_
{% endfor %}
## Limitations
{% for x in s.limitations %}- {{ x }}
{% else %}_none specified_
{% endfor %}
## Mitigations
{% for x in s.mitigations %}- {{ x }}
{% else %}_none specified_
{% endfor %}"""
)

_HTML = Template(
    """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Model Card — {{ s.name }}</title>
<style>
 body{font-family:system-ui,sans-serif;margin:2rem;max-width:820px}
 h1{margin-bottom:0}.meta{color:#555}
 code{background:#f4f4f4;padding:.1rem .3rem}
</style>
</head><body>
<h1>{{ s.name }} <small class="meta">{{ s.version }}</small></h1>
<p class="meta">
 Owner: {{ s.owner }} · Risk: <code>{{ s.risk_classification }}</code>
</p>
<h2>Intended use</h2><p>{{ s.intended_use or "not specified" }}</p>
<h2>Out of scope</h2>
<ul>{% for x in s.out_of_scope %}<li>{{ x }}</li>{% endfor %}</ul>
<h2>Evaluation</h2>
<ul>
{% for k, v in s.metrics.items() %}<li>{{ k }}: {{ "%.3f" | format(v) }}</li>
{% endfor %}</ul>
<h2>Limitations</h2>
<ul>{% for x in s.limitations %}<li>{{ x }}</li>{% endfor %}</ul>
<h2>Mitigations</h2>
<ul>{% for x in s.mitigations %}<li>{{ x }}</li>{% endfor %}</ul>
</body></html>"""
)


def load_spec(path: str | Path) -> ModelCardSpec:
    """Load a model card spec from YAML."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return ModelCardSpec.model_validate(data)


def to_markdown(spec: ModelCardSpec) -> str:
    """Render the model card as Markdown."""
    return _MARKDOWN.render(s=spec)


def to_html(spec: ModelCardSpec) -> str:
    """Render the model card as standalone HTML."""
    return _HTML.render(s=spec)
