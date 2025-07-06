import os
import subprocess
import sys
import time
from dataclasses import dataclass
from importlib.metadata import version
from packaging.version import Version, parse as parse_version

from rich.console import Console
from bugscanx.utils.common import get_confirm


@dataclass
class VersionInfo:
    current_version: str
    latest_stable: str = None
    latest_prerelease: str = None
    prerelease_is_newer: bool = False


class VersionManager:
    def __init__(self, package_name="bugscan-x"):
        self.package_name = package_name
        self.console = Console()

    def _is_prerelease(self, version_str):
        try:
            return Version(version_str).is_prerelease
        except Exception:
            return False

    def _parse_pip_output(self, output):
        lines = output.splitlines()
        versions = {}
        available_versions = []

        for line in lines:
            line = line.strip()
            if line.startswith('Available versions:'):
                available_versions = [
                    v.strip(' ,') 
                    for v in line.split(':', 1)[1].split()
                ]
            elif line.startswith('INSTALLED:'):
                versions['installed'] = line.split(':')[1].strip()
            elif line.startswith('LATEST:'):
                versions['latest'] = line.split(':')[1].strip()

        return versions, available_versions

    def check_updates(self):
        try:
            with self.console.status(
                "[yellow]Checking for updates...",
                spinner="dots"
            ):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "index",
                        "versions",
                        self.package_name,
                        "--pre",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=15,
                )

                versions_info, all_versions = self._parse_pip_output(result.stdout)
                if not all_versions:
                    self.console.print("[red] No version information found")
                    return None

                current_version = versions_info.get('installed') or version(self.package_name)
                current_ver = parse_version(current_version)
                stable_versions = [v for v in all_versions if not self._is_prerelease(v)]

                latest_stable = stable_versions[0] if stable_versions else None
                latest_prerelease = all_versions[0] if all_versions else None

                if not latest_prerelease or current_ver >= parse_version(latest_prerelease):
                    self.console.print(f"[green] You're up to date: {current_version}")
                    return None

                if self._is_prerelease(latest_prerelease) and current_ver >= parse_version(latest_prerelease):
                    latest_prerelease = None

                if latest_stable and current_ver >= parse_version(latest_stable):
                    latest_stable = None

                if not latest_stable and not latest_prerelease:
                    self.console.print(f"[green] You're up to date: {current_version}")
                    return None

                return VersionInfo(
                    current_version=current_version,
                    latest_stable=latest_stable,
                    latest_prerelease=latest_prerelease,
                    prerelease_is_newer=(
                        latest_stable 
                        and latest_prerelease
                        and self._is_prerelease(latest_prerelease)
                        and parse_version(latest_prerelease) > parse_version(latest_stable)
                    )
                )

        except subprocess.TimeoutExpired:
            self.console.print("[red] Update check timed out. Please check your internet connection.")
        except subprocess.CalledProcessError:
            self.console.print("[red] Failed to check updates")
        except Exception:
            self.console.print("[red] Error checking updates")
        return None

    def install_update(self, install_prerelease=False):
        try:
            with self.console.status("[yellow]Installing update...", spinner="point"):
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    self.package_name,
                ]
                if install_prerelease:
                    cmd.insert(-1, "--pre")
                
                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60,
                )
                self.console.print("[green] Update successful!")
                return True
        except Exception as e:
            self.console.print(f"[red] Installation failed: {str(e)}")
            return False

    def restart_application(self):
        self.console.print("[yellow] Restarting application...")
        time.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)


def main():
    manager = VersionManager()
    try:
        version_info = manager.check_updates()
        if not version_info:
            return

        if version_info.prerelease_is_newer:
            manager.console.print(
                f"[yellow] Pre-release update available: {version_info.current_version} → {version_info.latest_prerelease}"
            )
            manager.console.print("[red] Warning: Pre-release versions may be unstable and contain bugs.")
            if not get_confirm(" I understand the risks, update anyway"):
                if version_info.latest_stable and parse_version(version_info.latest_stable) > parse_version(version_info.current_version):
                    if get_confirm(f" Update to stable version {version_info.latest_stable}"):
                        if manager.install_update(install_prerelease=False):
                            manager.restart_application()
                return
            else:
                if manager.install_update(install_prerelease=True):
                    manager.restart_application()
        else:
            manager.console.print(
                f"[yellow] Stable update available: {version_info.current_version} → {version_info.latest_stable}"
            )
            if not get_confirm(" Update now"):
                return
            if manager.install_update(install_prerelease=False):
                manager.restart_application()

    except KeyboardInterrupt:
        manager.console.print("[yellow] Update cancelled by user.")
    except Exception as e:
        manager.console.print(f"[red] Error during update process: {str(e)}")
