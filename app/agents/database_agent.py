import re
import sqlite3
from contextlib import closing

from app.config import get_settings


def run_database_agent(query: str) -> dict:
    settings = get_settings()
    path = settings.resolve_path(settings.database_path)
    if not path.is_file():
        return {
            "agent": "database",
            "results": [],
            "error": "The sales database has not been configured.",
        }
    text = query.lower()
    quarters = list(dict.fromkeys(re.findall(r"\bq[1-4]\b", text)))
    where = ""
    params: list[str | int] = []
    if quarters:
        where = f" WHERE quarter IN ({','.join('?' for _ in quarters)})"
        params.extend(q.upper() for q in quarters)
    with closing(
        sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=5)
    ) as connection:
        connection.row_factory = sqlite3.Row
        products = [
            row[0] for row in connection.execute("SELECT DISTINCT product FROM sales")
        ]
        matched = [product for product in products if product.lower() in text]
        if matched:
            where += (
                " AND " if where else " WHERE "
            ) + f"product IN ({','.join('?' for _ in matched)})"
            params.extend(matched)
        aggregate = bool(re.search(r"\b(total|sum|combined)\b", text))
        columns = (
            "'All matching products' AS product, 'Selected period' AS quarter, SUM(revenue) AS revenue"
            if aggregate
            else "product, quarter, revenue"
        )
        limit = 100
        top = re.search(r"\btop\s+(\d+)\b", text)
        if top:
            limit = max(1, min(int(top.group(1)), 100))
        elif re.search(r"\b(highest|best|top)\b", text):
            limit = 1
        order = "ASC" if re.search(r"\b(lowest|least)\b", text) else "DESC"
        if order == "ASC":
            limit = 1
        rows = connection.execute(
            f"SELECT {columns} FROM sales{where} ORDER BY revenue {order}, product LIMIT ?",
            [*params, limit],
        ).fetchall()
    return {
        "agent": "database",
        "query": query,
        "selection": f"Filtered by requested quarter/product, ordered by revenue {order}, limited to {limit} rows. Revenue totals are aggregated when requested.",
        "results": [dict(row) for row in rows if row["revenue"] is not None],
    }
