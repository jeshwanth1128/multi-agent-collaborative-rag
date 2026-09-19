import sqlite3

from app.config import get_settings

DB_PATH = get_settings().resolve_path(get_settings().database_path)


def main():
    if DB_PATH.exists():
        print("Database already exists; leaving it unchanged.")
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product TEXT NOT NULL,
            quarter TEXT NOT NULL,
            revenue REAL NOT NULL
        )
    """)

    cursor.execute("DELETE FROM sales")

    rows = [
        ("AI Toolkit", "Q3", 125000),
        ("Analytics Pro", "Q3", 98000),
        ("Cloud Suite", "Q3", 143000),
        ("AI Toolkit", "Q2", 101000),
    ]

    cursor.executemany(
        "INSERT INTO sales(product, quarter, revenue) VALUES (?, ?, ?)",
        rows,
    )

    connection.commit()
    connection.close()

    print("DATABASE CREATED:", DB_PATH)


if __name__ == "__main__":
    main()
