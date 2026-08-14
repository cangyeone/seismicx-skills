#!/usr/bin/env python3
"""Locate or explicitly install the child skills used by seismicx-skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Dependency:
    route: str
    skill_name: str
    repo_dir: str
    repository: str


DEPENDENCIES = (
    Dependency(
        route="paper",
        skill_name="seismicx-paper-skill",
        repo_dir="seismicx-paper-skill",
        repository="https://github.com/cangyeone/seismicx-paper-skill.git",
    ),
    Dependency(
        route="catalog",
        skill_name="seismicx-catalog",
        repo_dir="seismicx-catalog-skill",
        repository="https://github.com/cangyeone/seismicx-catalog-skill.git",
    ),
    Dependency(
        route="fine-tuning",
        skill_name="seismicx-fine-tuning",
        repo_dir="seismicx-fine-tuning-skill",
        repository="https://github.com/cangyeone/seismicx-fine-tuning-skill.git",
    ),
    Dependency(
        route="dataset",
        skill_name="seismicx-dataset",
        repo_dir="seismicx-dataset-skill",
        repository="https://github.com/cangyeone/seismicx-dataset-skill.git",
    ),
)


def aliases() -> dict[str, Dependency]:
    result: dict[str, Dependency] = {}
    for dep in DEPENDENCIES:
        values = {
            dep.route,
            dep.skill_name,
            dep.repo_dir,
            dep.route.replace("-", "_"),
        }
        for value in values:
            result[value.lower()] = dep
    result["finetuning"] = next(d for d in DEPENDENCIES if d.route == "fine-tuning")
    result["fine_tuning"] = next(d for d in DEPENDENCIES if d.route == "fine-tuning")
    return result


def select_dependencies(value: str) -> tuple[Dependency, ...]:
    if value.lower() == "all":
        return DEPENDENCIES
    dep = aliases().get(value.lower())
    if dep is None:
        choices = ", ".join([d.route for d in DEPENDENCIES] + ["all"])
        raise ValueError(f"unknown skill route {value!r}; choose one of: {choices}")
    return (dep,)


def frontmatter_name(skill_file: Path) -> str | None:
    try:
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", text[:4096])
    return match.group(1).strip() if match else None


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        expanded = path.expanduser().resolve()
        key = os.fspath(expanded)
        if key not in seen:
            seen.add(key)
            result.append(expanded)
    return result


def project_search_roots(start: Path | None = None) -> list[Path]:
    """Return portable Agent Skills sources from CWD up to the Git root."""
    current = (start or Path.cwd()).expanduser().resolve()
    roots: list[Path] = []
    for directory in (current, *current.parents):
        roots.extend(
            [
                directory / ".agents" / "skills",
                directory / ".opencode" / "skills",
                directory / ".claude" / "skills",
            ]
        )
        if (directory / ".git").exists():
            break
    return unique_paths(roots)


def default_search_roots() -> list[Path]:
    router_dir = Path(__file__).resolve().parent.parent
    roots = [router_dir.parent, *project_search_roots()]
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        roots.append(Path(codex_home) / "skills")
    roots.extend(
        [
            Path.home() / ".agents" / "skills",
            Path.home() / ".config" / "opencode" / "skills",
            Path.home() / ".claude" / "skills",
            Path.home() / ".codex" / "skills",
            Path("/etc/codex/skills"),
            Path.home() / ".cache" / "seismicx-skills",
        ]
    )
    return unique_paths(roots)


def candidate_directories(root: Path, dep: Dependency) -> list[Path]:
    return unique_paths(
        [
            root,
            root / dep.repo_dir,
            root / dep.skill_name,
            root / dep.route,
        ]
    )


def locate_dependency(dep: Dependency, search_roots: Iterable[Path]) -> Path | None:
    for root in unique_paths(search_roots):
        for candidate in candidate_directories(root, dep):
            skill_file = candidate / "SKILL.md"
            if skill_file.is_file() and frontmatter_name(skill_file) == dep.skill_name:
                return skill_file.resolve()
    return None


def records(
    dependencies: Iterable[Dependency], search_roots: Iterable[Path]
) -> list[dict[str, str | None]]:
    output: list[dict[str, str | None]] = []
    for dep in dependencies:
        skill_file = locate_dependency(dep, search_roots)
        record = asdict(dep)
        record["status"] = "found" if skill_file else "missing"
        record["skill_file"] = os.fspath(skill_file) if skill_file else None
        output.append(record)
    return output


def emit_records(items: list[dict[str, str | None]], as_json: bool) -> None:
    if as_json:
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return
    for item in items:
        location = item["skill_file"] or "-"
        print(
            f"{item['route']}\t{item['status']}\t"
            f"{item['skill_name']}\t{location}\t{item['repository']}"
        )


def add_search_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--search-root",
        action="append",
        type=Path,
        default=[],
        help="Additional parent or skill directory to inspect; repeat as needed.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")


def command_status(args: argparse.Namespace) -> int:
    roots = unique_paths([*args.search_root, *default_search_roots()])
    items = records(DEPENDENCIES, roots)
    emit_records(items, args.json)
    return 0 if all(item["status"] == "found" for item in items) else 1


def command_locate(args: argparse.Namespace) -> int:
    dependencies = select_dependencies(args.skill)
    roots = unique_paths([*args.search_root, *default_search_roots()])
    items = records(dependencies, roots)
    emit_records(items, args.json)
    return 0 if all(item["status"] == "found" for item in items) else 1


def install_dependency(dep: Dependency, target: Path, ref: str) -> dict[str, str]:
    target = target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    destination = target / dep.skill_name
    if destination.exists():
        existing = destination / "SKILL.md"
        if existing.is_file() and frontmatter_name(existing) == dep.skill_name:
            return {
                "route": dep.route,
                "status": "already-present",
                "skill_file": os.fspath(existing.resolve()),
                "repository": dep.repository,
            }
        raise RuntimeError(
            f"refusing to overwrite existing path with unexpected contents: {destination}"
        )

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            ref,
            dep.repository,
            os.fspath(destination),
        ],
        check=True,
    )
    skill_file = destination / "SKILL.md"
    observed_name = frontmatter_name(skill_file)
    if observed_name != dep.skill_name:
        raise RuntimeError(
            f"installed {destination}, but SKILL.md name is {observed_name!r}; "
            f"expected {dep.skill_name!r}"
        )
    return {
        "route": dep.route,
        "status": "installed",
        "skill_file": os.fspath(skill_file.resolve()),
        "repository": dep.repository,
    }


def command_install(args: argparse.Namespace) -> int:
    dependencies = select_dependencies(args.skill)
    results = [
        install_dependency(dep, target=args.target, ref=args.ref)
        for dep in dependencies
    ]
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(
                f"{result['route']}\t{result['status']}\t"
                f"{result['skill_file']}\t{result['repository']}"
            )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Locate or explicitly install SeismicX child skills."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser(
        "status", help="Locate all child skills without changing the filesystem."
    )
    add_search_arguments(status_parser)
    status_parser.set_defaults(handler=command_status)

    locate_parser = subparsers.add_parser(
        "locate", help="Locate one child skill or all child skills."
    )
    locate_parser.add_argument(
        "--skill",
        required=True,
        help="paper, catalog, dataset, fine-tuning, a canonical skill name, or all",
    )
    add_search_arguments(locate_parser)
    locate_parser.set_defaults(handler=command_locate)

    install_parser = subparsers.add_parser(
        "install", help="Clone selected child skills into an explicit directory."
    )
    install_parser.add_argument(
        "--skill",
        required=True,
        help="paper, catalog, dataset, fine-tuning, a canonical skill name, or all",
    )
    install_parser.add_argument(
        "--target",
        required=True,
        type=Path,
        help="Explicit destination parent; existing directories are never overwritten.",
    )
    install_parser.add_argument(
        "--ref",
        default="main",
        help="Git branch or tag to clone (default: main).",
    )
    install_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    install_parser.set_defaults(handler=command_install)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.handler(args))
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
