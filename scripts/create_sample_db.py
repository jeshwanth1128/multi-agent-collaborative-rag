import sqlite3
from pathlib import Path

DB_PATH = Path("data/sample.db")


def main():
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
