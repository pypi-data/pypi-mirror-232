"""Nox configuration."""

import nox

nox.options.sessions = ["tests"]


@nox.session(python=["3.9", "3.10", "3.11", "3.12"])
def tests(session: nox.Session) -> None:
    """Run pytest across multiple python versions."""
    session.install('.[test]')
    session.run('pytest')


@nox.session(python=["3.9", "3.12"])
@nox.parametrize("database", ['mysql', 'sqlite'])
def debug(session: nox.Session, database: str) -> None:
    """Trying to figure out what all the properties are."""
    session.debug(f"{session.name=}")
    session.debug(f"{session.bin=}")
    session.debug(f"{session.bin_paths=}")
    session.debug(f"{session.interactive=}")
    session.debug(f"{session.invoked_from=}")
    session.debug(f"{session.posargs=}")
    session.debug(f"{session.python=}")
    session.debug(f"{session.virtualenv=}")
    session.debug(f"{database=}")

    import os
    session.debug(f"{os.name=}")

    import sys
    session.debug(f"{sys.api_version=}")
    session.debug(f"{sys.platform=}")
