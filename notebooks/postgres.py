import os
import psycopg2
from IPython.core.magic import register_cell_magic


def run_postgres_query(endpoint, queries):
    try:
        conn = psycopg2.connect(endpoint)
        cur = conn.cursor()
        cur.execute(queries)
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@register_cell_magic
def postgres(line, cell):
    endpoint = os.getenv(
        "POSTGRES_ENDPOINT_URL", "postgres://nzuser:nzpass@localhost:5432/postgres"
    )
    run_postgres_query(endpoint, cell)


def load_ipython_extension(ipython):
    ipython.register_magic_function(postgres, "cell")
