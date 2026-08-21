"""Preflight checks for the billable SOP-Bench execution phase."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def resolve_api_key(runtime_dotenv: Path | None = None) -> str | None:
    """Resolve a DeepSeek key without emitting it to logs or evidence files."""
    environment_key = os.environ.get("DEEPSEEK_API_KEY")
    if environment_key:
        return environment_key
    if runtime_dotenv is None or not runtime_dotenv.is_file():
        return None
    for raw_line in runtime_dotenv.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() != "DEEPSEEK_API_KEY":
            continue
        return value.strip().strip('"').strip("'") or None
    return None


def resolve_configured_deepseek_key(runtime_config: Path | None = None) -> str | None:
    """Return only a dedicated key from a DeepSeek model client section."""
    if runtime_config is None or not runtime_config.is_file():
        return None

    def walk(value: object) -> str | None:
        if isinstance(value, dict):
            provider = str(value.get("client_provider", "")).lower()
            api_base = str(value.get("api_base", value.get("base_url", ""))).lower()
            api_key = value.get("api_key")
            if provider == "deepseek" and "api.deepseek.com" in api_base and isinstance(api_key, str):
                return api_key or None
            for child in value.values():
                found = walk(child)
                if found:
                    return found
        if isinstance(value, list):
            for child in value:
                found = walk(child)
                if found:
                    return found
        return None

    return walk(yaml.safe_load(runtime_config.read_text(encoding="utf-8")))


def resolve_runtime_deepseek_key(
    runtime_dotenv: Path | None = None, runtime_config: Path | None = None
) -> str | None:
    """Resolve the Jiuwen generic runtime key only for a DeepSeek endpoint."""
    explicit_key = resolve_api_key(runtime_dotenv)
    if explicit_key:
        return explicit_key
    configured_key = resolve_configured_deepseek_key(runtime_config)
    if configured_key:
        return configured_key
    if (
        runtime_dotenv is None
        or runtime_config is None
        or not runtime_dotenv.is_file()
        or not runtime_config.is_file()
        or "api.deepseek.com" not in runtime_config.read_text(encoding="utf-8").lower()
    ):
        return None
    for raw_line in runtime_dotenv.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "API_KEY":
            return value.strip().strip('"').strip("'") or None
    return None


def validate_real_run_environment(
    sopbench_root: Path,
    runtime_dotenv: Path | None = None,
    runtime_config: Path | None = None,
) -> list[str]:
    issues: list[str] = []
    if not resolve_runtime_deepseek_key(runtime_dotenv, runtime_config):
        issues.append("missing DEEPSEEK_API_KEY")
    if not (Path(sopbench_root) / "pyproject.toml").is_file():
        issues.append("missing SOP-Bench checkout marker: pyproject.toml")
    return issues
