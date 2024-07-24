import os
import json
import uuid
import time
import requests
import pyarrow as pa
import pyarrow.ipc as pi
from IPython.core.magic import register_cell_magic


def run_arros_stream(endpoint, target, queries, token: None):
    headers = {}
    headers["Content-Type"] = "application/json"
    request = {}
    request["name"] = target
    request["type"] = "stream"
    request["queries"] = queries

    if token is not None:
        headers["Authorization"] = "Basic {}".format(token)

    response = requests.delete(
        os.path.join(endpoint, "pipelines", target),
        headers=headers,
    )

    response = requests.post(
        os.path.join(endpoint, "pipelines"),
        data=json.dumps(request),
        headers=headers,
    )
    if response.status_code != 200:
        print(f"{response.content}")
        raise response.raise_for_status()
    else:
        response = requests.post(
            os.path.join(endpoint, "pipelines", target, "execute"),
            data=json.dumps(request),
            headers=headers,
        )
        if response.status_code != 200:
            print(f"{response.content}")
            raise response.raise_for_status()


def check_arros_stream(endpoint, target, token: None):
    headers = {}
    headers["Content-Type"] = "application/json"

    if token is not None:
        headers["Authorization"] = "Basic {}".format(token)

    response = requests.get(
        os.path.join(endpoint, "pipelines", target, "inspect"),
        headers=headers,
    )
    status = response.json()
    return status["state"]


def run_arros_query(endpoint, queries, token: None):
    headers = {}
    headers["Content-Type"] = "application/json"

    if token is not None:
        headers["Authorization"] = "Basic {}".format(token)

    response = requests.post(
        os.path.join(endpoint, "sql"), data=queries, headers=headers
    )
    if response.status_code != 200:
        print(f"{response.content}")
        raise response.raise_for_status()
    else:
        with pi.open_stream(response.content) as reader:
            table = pa.Table.from_batches(reader)
            return table


@register_cell_magic
def arros(line, cell):
    endpoint = os.getenv("ARROS_ENDPOINT_URL", "http://localhost:8886")
    token = os.getenv("ARROS_ENDPOINT_TOKEN")
    pipeline = str(uuid.uuid4())
    run_arros_stream(endpoint, pipeline, cell, token)
    while check_arros_stream(endpoint, pipeline, token) == "running":
        print(f"{pipeline}: running")
        time.sleep(1)
    print(f"{pipeline}: done")


@register_cell_magic
def asquery(line, cell):
    endpoint = os.getenv("ARROS_ENDPOINT_URL", "http://localhost:8886")
    token = os.getenv("ARROS_ENDPOINT_TOKEN")
    table = run_arros_query(endpoint, cell, token)
    print(table.to_pandas())


def load_ipython_extension(ipython):
    ipython.register_magic_function(arros, "cell")
    ipython.register_magic_function(asquery, "cell")
