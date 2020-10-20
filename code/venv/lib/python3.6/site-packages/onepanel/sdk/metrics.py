import json
import os

from websocket import create_connection


class Metrics:
    def __init__(self, account_uid=None, project_uid=None, job_uid=None):
        host = os.getenv('HOST', 'c.onepanel.io')

        if account_uid is None:
            account_uid = os.getenv('ACCOUNT_UID')

        if project_uid is None:
            project_uid = os.getenv('PROJECT_UID')

        if job_uid is None:
            job_uid = os.getenv('JOB_UID')

        self._endpoint = 'wss://{}/{}/projects/{}/jobs/{}/metrics/:9999'.format(host, account_uid, project_uid, job_uid)

        attempt = 0
        while attempt < max_tries:
            attempt += 1
            try:
                self._ws = create_connection(self._endpoint)
                break
            except BaseException as exception:
                if attempt >= max_tries:
                    raise

                pass

    def close(self):
        self._ws.close()

    # TODO - add a with method
    # TODO - add a callback for tensorflow and the like.

    def add(self, x_name, x_value, y_name, y_value):
        self._ws.send(json.dumps({
            "x_axis": x_name,
            "x_value": x_value,
            "metric": y_name,
            "value": y_value
        }))


if __name__ == "__main__":
    m = Metrics("andreyonepanel", "edge-cases", "362")
    m.put("x", 1, "y", 1)
    m.put("a", 1, "b", 1)
    m.close()
