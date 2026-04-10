from pathlib import Path

from src.db.connection import get_connection


def run_analytics():
    sql_path = Path(__file__).resolve().parent / "analytics.sql"

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_text = f.read()

    queries = [q.strip() for q in sql_text.split(";") if q.strip()]

    conn = get_connection()
    cur = conn.cursor()

    try:
        for i, query in enumerate(queries, start=1):
            print(f"\nRunning analytics query {i}...\n")
            cur.execute(query)
            rows = cur.fetchmany(10)

            for row in rows:
                print(row)

        print("\nAnalytics run completed successfully.")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run_analytics()