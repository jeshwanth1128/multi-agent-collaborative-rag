import sqlite3
from pathlib import Path

DB_PATH = Path("data/sample.db")


def run_database_agent(query: str) -> dict:
    query_lower = query.lower()

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if "highest" in query_lower or "top" in query_lower:
        cursor.execute("""
            SELECT product, quarter, revenue
            FROM sales
            ORDER BY revenue DESC
            LIMIT 3
        """)
    elif "q3" in query_lower:
        cursor.execute("""
            SELECT product, quarter, revenue
            FROM sales
            WHERE quarter = 'Q3'
            ORDER BY revenue DESC
        """)
    else:
        cursor.execute("""
            SELECT product, quarter, revenue
            FROM sales
            ORDER BY revenue DESC
        """)

    rows = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return {
        "agent": "database",
        "query": query,
        "results": rows,
    }
