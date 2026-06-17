"""Model Card Generator — YAML/dict spec → Markdown + HTML."""

from .generator import ModelCardSpec, load_spec, to_html, to_markdown

__all__ = ["ModelCardSpec", "load_spec", "to_html", "to_markdown"]
