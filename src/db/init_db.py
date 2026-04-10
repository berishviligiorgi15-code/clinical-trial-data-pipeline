from pathlib import Path

from src.db.connection import get_connection


def run_schema():
    schema_path = Path(__file__).resolve().parent / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(schema_sql)
        conn.commit()
        print("Database schema created successfully.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run_schema()