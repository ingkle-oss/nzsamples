import os
import json
import requests
import pyarrow as pa
import pyarrow.ipc as pi
from IPython.core.magic import register_cell_magic


def run_nazaredb_query(endpoint, queries, token: None):
    headers = {}
    headers["Content-Type"] = "application/json"
    request = {}
    request["sql"] = queries

    if token is not None:
        headers["Authorization"] = "Basic {}".format(token)

    response = requests.post(
        os.path.join(endpoint, "sql", "arrow", "stream"),
        data=json.dumps(request),
        headers=headers,
    )
    if response.status_code != 200:
        print(f"{response.content}")
        raise response.raise_for_status()
    else:
        with pi.open_stream(response.content) as reader:
            table = pa.Table.from_batches(reader)
            return table


@register_cell_magic
def nazaredb(line, cell):
    endpoint = os.getenv("NAZAREDB_ENDPOINT_URL", "http://localhost:8888")
    token = os.getenv("NAZAREDB_ENDPOINT_TOKEN")
    table = run_nazaredb_query(endpoint, cell, token)
    print(table.to_pandas())


def load_ipython_extension(ipython):
    ipython.register_magic_function(nazaredb, "cell")
