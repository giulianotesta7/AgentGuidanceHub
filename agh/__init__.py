"""Agent Guidance Hub."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agh")
except PackageNotFoundError:  # pragma: no cover - source tree before installation
    __version__ = "0.0.0"
