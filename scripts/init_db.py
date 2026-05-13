from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.init_db import initialize_database


def main() -> None:
    initialize_database()
    print("Database tables are ready.")


if __name__ == "__main__":
    main()