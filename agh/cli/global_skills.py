"""Global skill install, cache, lock, and removal for AGH CLI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote
import urllib.request

from agh.cli.agent_integrations import global_skill_dir
from agh.cli.config import load_config
from agh.common.validation import parse_package_ref


class GlobalSkillError(RuntimeError):
    """Raised for global skill install/remove failures."""

    def __init__(self, message: str, *, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects so Bearer tokens are never forwarded."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirectHandler)


@dataclass(frozen=True)
class InstallResult:
    target_path: Path
    changed: bool


def _agh_state_dir() -> Path:
    xdg = _env_path("XDG_STATE_HOME")
    if xdg is not None:
        return xdg / "agh"
    return Path.home() / ".local" / "state" / "agh"


def _env_path(name: str) -> Path | None:
    value = __import__("os").environ.get(name, "").strip()
    if value:
        return Path(value).expanduser()
    return None


def global_skill_cache_dir() -> Path:
    """Return the AGH global skill cache directory."""
    return _agh_state_dir() / "global-skills" / "cache"


def global_skill_lock_path() -> Path:
    """Return the AGH global skill lock file path."""
    return _agh_state_dir() / "global-skills" / "lock.toml"


def global_skill_defaults_path() -> Path:
    """Return the AGH global skill defaults file path."""
    return _agh_state_dir() / "global-skills" / "defaults.toml"


def _target_path(agent: str, skill_name: str) -> Path:
    return global_skill_dir(agent) / skill_name / "SKILL.md"


def _cache_path(package_ref: str, skill_name: str) -> Path:
    parsed = parse_package_ref(package_ref, allow_latest=False)
    return (
        global_skill_cache_dir()
        / parsed.domain
        / parsed.name
        / parsed.version
        / "skills"
        / skill_name
        / "SKILL.md"
    )


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_lock() -> list[dict[str, Any]]:
    """Read the global skill lock file."""
    path = global_skill_lock_path()
    if not path.exists():
        return []
    try:
        data = __import__("tomllib").loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GlobalSkillError(f"failed to read lock file: {exc}") from exc
    if not isinstance(data, dict):
        return []
    skills = data.get("skills")
    if not isinstance(skills, list):
        return []
    return [dict(entry) for entry in skills if isinstance(entry, dict)]


def _write_lock(entries: list[dict[str, Any]]) -> None:
    path = global_skill_lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for entry in entries:
        lines.append("[[skills]]")
        for key, value in entry.items():
            if isinstance(value, str):
                lines.append(f'{key} = "{_escape_toml(value)}"')
            elif isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, int):
                lines.append(f"{key} = {value}")
            else:
                lines.append(f'{key} = "{_escape_toml(str(value))}"')
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _escape_toml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _find_entry(
    entries: list[dict[str, Any]], agent: str, skill_name: str
) -> dict[str, Any] | None:
    for entry in entries:
        if entry.get("agent") == agent and entry.get("name") == skill_name:
            return entry
    return None


def configure_api_request(api_request: Any) -> None:
    """Bind the CLI's API requester so global skill flows can reach the server."""
    global _api_request
    _api_request = api_request


def resolve_skill(
    api_request: Any, package_ref: str, skill_name: str
) -> dict[str, Any]:
    """Resolve a collection skill to concrete package version metadata."""
    query = (
        f"/skills:resolve?package_ref={quote(package_ref, safe='')}&"
        f"skill_name={quote(skill_name, safe='')}"
    )
    return api_request("GET", query)


def download_skill(api_request: Any, resolved: dict[str, Any]) -> str:
    """Download SKILL.md content for a resolved skill."""
    config = load_config()
    download_url = str(resolved.get("download_url", ""))
    if not download_url:
        raise GlobalSkillError("resolved skill missing download_url")
    full_url = f"{config.instance_url}{download_url}"
    request = urllib.request.Request(
        full_url,
        headers={
            "Authorization": f"Bearer {config.token}",
            "Accept": "text/plain",
        },
        method="GET",
    )
    try:
        with _NO_REDIRECT_OPENER.open(request, timeout=10) as response:  # noqa: S310 - configured AGH URL
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise GlobalSkillError(f"download failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise GlobalSkillError(f"download failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise GlobalSkillError(f"download failed: {exc}") from exc


def install_skill_global(
    agent: str,
    package_ref: str,
    skill_name: str,
    *,
    force: bool = False,
) -> InstallResult:
    """Install a collection skill into the selected agent's native global path."""
    resolved = resolve_skill(_api_request, package_ref, skill_name)
    return _install_resolved(agent, package_ref, resolved, skill_name, force=force)


def _api_request(method: str, path: str, **kwargs: Any) -> Any:
    """Placeholder requester; replaced by the CLI's real requester at runtime."""
    raise GlobalSkillError("global skills API requester not configured")


def _install_resolved(
    agent: str,
    package_ref_requested: str,
    resolved: dict[str, Any],
    skill_name: str,
    *,
    force: bool,
) -> InstallResult:
    package_ref_resolved = str(resolved.get("package_ref", ""))
    package_version_id = str(resolved.get("package_version_id", ""))
    checksum = str(resolved.get("checksum", ""))
    if not package_ref_resolved or not package_version_id or not checksum:
        raise GlobalSkillError("resolved skill missing required metadata")

    target = _target_path(agent, skill_name)
    entries = read_lock()
    existing = _find_entry(entries, agent, skill_name)

    if existing is not None:
        if existing.get("checksum") == checksum:
            return InstallResult(target_path=target, changed=False)
        if existing.get("package_ref_resolved") != package_ref_resolved:
            raise GlobalSkillError(
                f"skill {skill_name} is already installed from "
                f"{existing.get('package_ref_resolved')}; remove it first"
            )
    elif target.exists():
        if not force:
            raise GlobalSkillError(
                f"target {target} already exists and is not tracked by AGH; "
                "use --force to overwrite"
            )

    content = download_skill(_api_request, resolved)
    _write_skill_file(target, content)
    _write_cache_file(package_ref_resolved, skill_name, content)

    new_entry = {
        "name": skill_name,
        "agent": agent,
        "package_ref_requested": package_ref_requested,
        "package_ref_resolved": package_ref_resolved,
        "package_version_id": package_version_id,
        "checksum": checksum,
        "target_path": str(target),
        "installed_at": _now_iso(),
    }
    if existing is not None:
        existing.update(new_entry)
    else:
        entries.append(new_entry)
    _write_lock(entries)
    return InstallResult(target_path=target, changed=True)


def _write_skill_file(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _write_cache_file(package_ref: str, skill_name: str, content: str) -> None:
    cache = _cache_path(package_ref, skill_name)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(content, encoding="utf-8")


def remove_skill_global(agent: str, skill_name: str) -> Path:
    """Remove a globally installed skill from the agent path and lock."""
    entries = read_lock()
    existing = _find_entry(entries, agent, skill_name)
    if existing is None:
        raise GlobalSkillError(f"skill {skill_name} is not installed for {agent}")

    target = Path(str(existing.get("target_path", _target_path(agent, skill_name))))
    if target.exists():
        target.unlink()
        if target.parent.is_dir() and not any(target.parent.iterdir()):
            target.parent.rmdir()

    entries.remove(existing)
    _write_lock(entries)
    return target


def list_installed_skills(agent: str) -> list[dict[str, Any]]:
    """Return lock entries for the given agent."""
    return [entry for entry in read_lock() if entry.get("agent") == agent]
