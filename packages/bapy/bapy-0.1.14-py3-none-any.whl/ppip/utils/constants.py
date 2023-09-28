__all__ = (
    "GIT_DEFAULT_SCHEME",
    "GITHUB_DOMAIN",
    "GITHUB_URL",
    "LOGGER_DEFAULT_FMT",
    "PPIP_PROJECT",
    "PYTHON_DEFAULT_VERSION",
)

GIT_DEFAULT_SCHEME = "https"
GITHUB_DOMAIN = "github.com"
GITHUB_URL = {
    "api": f"https://api.{GITHUB_DOMAIN}/",
    "git+file": "git+file:///",
    "git+https": f"git+https://{GITHUB_DOMAIN}/",
    "git+ssh": f"git+ssh://git@{GITHUB_DOMAIN}/",
    "https": f"https://{GITHUB_DOMAIN}/",
    "ssh": f"git@{GITHUB_DOMAIN}:",
}
"""
GitHub: api, git+file, git+https, git+ssh, https, ssh and git URLs
(join directly the user or path without '/' or ':')
"""
LOGGER_DEFAULT_FMT = ("<level>{level: <8}</level> <red>|</red> "
                      "<cyan>{name}</cyan> <red>|</red> <red>|</red> "
                      "<level>{message}</level>")
PPIP_PROJECT = "ppip"
"""Ppip Project Name"""
PYTHON_DEFAULT_VERSION = "3.11"
"""Python default version for venv, etc."""
