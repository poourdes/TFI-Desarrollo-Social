import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_alembic_upgrade_downgrade_and_upgrade_again(tmp_path: Path) -> None:
    database_url = f"sqlite+pysqlite:///{(tmp_path / 'migration.db').as_posix()}"
    environment = dict(
        os.environ,
        DATABASE_URL=database_url,
        FERNET_KEY="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
    )

    def run_alembic(*arguments: str) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", *arguments],
            cwd=BACKEND_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    run_alembic("upgrade", "a148dfeb064b")
    run_alembic("upgrade", "head")
    run_alembic("downgrade", "a148dfeb064b")
    run_alembic("upgrade", "head")
