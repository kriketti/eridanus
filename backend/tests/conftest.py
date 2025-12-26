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


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("GAE_ENV", "local")
    monkeypatch.setenv("DEV_USER_EMAIL", "dev@example.com")
    monkeypatch.setenv("ALLOWED_USER_EMAIL", "dev@example.com")
    monkeypatch.setenv("SECRET_KEY", "test-secret")

    from importlib import reload
    import main as main_module

    reload(main_module)
    flask_app = main_module.app
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret",
    )
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()
