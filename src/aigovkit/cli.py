"""aigov CLI: modelcard / risk / redteam."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .modelcards import load_spec, to_html, to_markdown
from .redteam import guarded_target, run_redteam, vulnerable_target
from .risk import assess, load_answers


def _modelcard(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    md, html = to_markdown(spec), to_html(spec)
    Path(f"{args.out}.md").write_text(md, encoding="utf-8")
    Path(f"{args.out}.html").write_text(html, encoding="utf-8")
    print(f"Wrote {args.out}.md and {args.out}.html")
    return 0


def _risk(args: argparse.Namespace) -> int:
    report = assess(load_answers(args.answers))
    print(json.dumps(report.model_dump(), indent=2))
    print(f"\nVERDICT: {report.verdict.upper()} "
          f"({report.satisfied}/{report.total} controls satisfied)")
    return 0 if report.verdict == "green" else 1


def _redteam(args: argparse.Namespace) -> int:
    target = guarded_target() if args.target == "guarded" else vulnerable_target
    report = run_redteam(target)
    for r in report.results:
        status = "BLOCKED" if r.blocked else ("LEAKED" if r.succeeded else "safe")
        print(f"  [{r.category}] {r.id}: {status}")
    print(f"\npass_rate={report.pass_rate} "
          f"({report.total - report.succeeded}/{report.total} withstood)")
    return 0 if report.succeeded == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aigov")
    sub = parser.add_subparsers(dest="command", required=True)

    mc = sub.add_parser("modelcard", help="Generate a model card from a YAML spec.")
    mc.add_argument("spec")
    mc.add_argument("--out", default="card")
    mc.set_defaults(func=_modelcard)

    rk = sub.add_parser("risk", help="Run a risk assessment from a YAML answers file.")
    rk.add_argument("answers")
    rk.set_defaults(func=_risk)

    rt = sub.add_parser("redteam", help="Run the OWASP LLM red-team suite.")
    rt.add_argument("--target", choices=["vulnerable", "guarded"], default="guarded")
    rt.set_defaults(func=_redteam)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
