"""Static assertions for the Windows release assets in the release workflow.

These tests read ``.github/workflows/release.yml`` and ``pyproject.toml`` as text
to assert that the Windows binary build, deterministic asset naming, archive
layout validation, release attachment, and PyInstaller build dependency are
present without running the real release.
"""

from __future__ import annotations

from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/release.yml")
PYPROJECT_PATH = Path("pyproject.toml")
UVLOCK_PATH = Path("uv.lock")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Task 1.2: build-windows job and matrix
# ---------------------------------------------------------------------------


def test_workflow_has_build_windows_job() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "build-windows:" in workflow


def test_build_windows_depends_on_validate() -> None:
    workflow = _read(WORKFLOW_PATH)
    # The build-windows job needs to come after validate.
    validate_idx = workflow.index("  validate:")
    build_idx = workflow.index("build-windows:")
    assert build_idx > validate_idx


def test_build_windows_matrix_includes_amd64_and_arm64() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "amd64" in workflow
    assert "arm64" in workflow


def test_build_windows_uses_native_windows_runners() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "windows-2022" in workflow
    assert "windows-11-arm" in workflow


def test_build_windows_uses_python_arch_matrix() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "x64" in workflow
    assert "arm64" in workflow


# ---------------------------------------------------------------------------
# Task 1.2: PyInstaller build invocation
# ---------------------------------------------------------------------------


def test_build_windows_invokes_pyinstaller() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "pyinstaller" in workflow.lower()


def test_build_windows_uses_copy_metadata_agh() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "--copy-metadata agh" in workflow


def test_build_windows_sets_setuptools_scm_pretend_version() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_AGH" in workflow


# ---------------------------------------------------------------------------
# Task 1.2: deterministic asset names and zip layout
# ---------------------------------------------------------------------------


def test_build_windows_uses_deterministic_amd64_zip_name() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "agh-" in workflow
    assert "windows-amd64.zip" in workflow


def test_build_windows_uses_deterministic_arm64_zip_name() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "windows-arm64.zip" in workflow


def test_build_windows_validates_root_agh_exe_in_zip() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "agh.exe" in workflow


def test_build_windows_checks_frozen_version() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "--version" in workflow


def test_build_windows_uploads_artifact() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "upload-artifact" in workflow


# ---------------------------------------------------------------------------
# Task 1.8: publication depends on build-windows, release attaches assets
# ---------------------------------------------------------------------------


def test_publish_pypi_depends_on_build_windows() -> None:
    workflow = _read(WORKFLOW_PATH)
    # Find publish-pypi job block and check its needs includes build-windows.
    pypi_idx = workflow.index("  publish-pypi:")
    needs_block = workflow[pypi_idx : pypi_idx + 200]
    assert "build-windows" in needs_block


def test_publish_ghcr_depends_on_build_windows() -> None:
    workflow = _read(WORKFLOW_PATH)
    ghcr_idx = workflow.index("  publish-ghcr:")
    needs_block = workflow[ghcr_idx : ghcr_idx + 200]
    assert "build-windows" in needs_block


def test_github_release_downloads_windows_artifacts() -> None:
    workflow = _read(WORKFLOW_PATH)
    release_idx = workflow.index("  github-release:")
    release_block = workflow[release_idx : release_idx + 600]
    assert "download-artifact" in release_block


def test_github_release_defines_version_env() -> None:
    workflow = _read(WORKFLOW_PATH)
    release_idx = workflow.index("  github-release:")
    release_block = workflow[release_idx : release_idx + 400]
    assert "VERSION: ${{ needs.validate.outputs.version }}" in release_block


def test_github_release_attaches_both_windows_assets() -> None:
    workflow = _read(WORKFLOW_PATH)
    release_idx = workflow.index("  github-release:")
    release_block = workflow[release_idx : release_idx + 1200]
    assert "windows-assets/agh-${{ env.VERSION }}-windows-amd64.zip" in release_block
    assert "windows-assets/agh-${{ env.VERSION }}-windows-arm64.zip" in release_block


def test_github_release_depends_on_build_windows() -> None:
    workflow = _read(WORKFLOW_PATH)
    release_idx = workflow.index("  github-release:")
    needs_block = workflow[release_idx : release_idx + 200]
    assert "build-windows" in needs_block


# ---------------------------------------------------------------------------
# Task 1.9 (triangulate): reject partial Windows delivery
# ---------------------------------------------------------------------------


def test_build_windows_matrix_fail_fast_false() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "fail-fast: false" in workflow


def test_build_windows_if_no_files_found_error() -> None:
    workflow = _read(WORKFLOW_PATH)
    assert "if-no-files-found: error" in workflow


# ---------------------------------------------------------------------------
# Task 1.3: PyInstaller build dependency group
# ---------------------------------------------------------------------------


def test_pyproject_has_release_dependency_group_with_pyinstaller() -> None:
    pyproject = _read(PYPROJECT_PATH)
    assert "[dependency-groups]" in pyproject
    assert "release" in pyproject
    assert "pyinstaller" in pyproject.lower()


def test_pyinstaller_not_in_runtime_dependencies() -> None:
    pyproject = _read(PYPROJECT_PATH)
    # Find [project] dependencies line and confirm pyinstaller is NOT there.
    deps_idx = pyproject.index("dependencies = [")
    deps_end = pyproject.index("]", deps_idx)
    deps_block = pyproject[deps_idx:deps_end]
    assert "pyinstaller" not in deps_block.lower()


def test_uv_lock_records_pyinstaller() -> None:
    lockfile = _read(UVLOCK_PATH)
    assert "pyinstaller" in lockfile.lower()
