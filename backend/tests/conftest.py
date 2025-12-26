import os

import pytest

@pytest.fixture(scope="session")
def datastore_emulator():
    host = os.environ.get("DATASTORE_EMULATOR_HOST")
    if not host:
        pytest.skip("Set DATASTORE_EMULATOR_HOST to run Datastore emulator tests.")
    if not os.environ.get("DATASTORE_PROJECT_ID") and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        os.environ["DATASTORE_PROJECT_ID"] = "test"
    return host
