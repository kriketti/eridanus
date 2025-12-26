from datetime import date, time

from eridanus.repository import JumpRopeRepository, PushUpsRepository, RunRepository, WeightRepository


def _delete_test_entities(repo, username):
    items = list(repo.fetch_by_username(username))
    for item in items:
        repo.delete(item.key.id)


def test_run_repository_crud(datastore_emulator):
    repo = RunRepository()
    username = "__pytest_run__"
    _delete_test_entities(repo, username)

    record = {
        "usernickname": username,
        "activity_date": date(2025, 1, 2),
        "activity_time": time(6, 30),
        "duration": 30,
        "distance": 5.0,
        "calories": 200,
        "speed": 10.0,
        "notes": "test",
    }
    repo.create(record)

    items = list(repo.fetch_by_username(username))
    assert items
    created = items[0]
    assert created["activity_date"].date() == date(2025, 1, 2)
    assert created["distance"] == 5.0

    updated = repo.update({"id": created.key.id, "distance": 6.5})
    assert updated is not None
    refreshed = repo.read(created.key.id)
    assert refreshed["distance"] == 6.5

    repo.delete(created.key.id)
    assert not list(repo.fetch_by_username(username))


def test_pushups_repository_crud(datastore_emulator):
    repo = PushUpsRepository()
    username = "__pytest_pushups__"
    _delete_test_entities(repo, username)

    record = {
        "usernickname": username,
        "activity_date": date(2025, 1, 3),
        "activity_time": time(8, 15),
        "duration": 5,
        "calories": 20,
        "count": 30,
        "notes": "test",
    }
    repo.create(record)

    items = list(repo.fetch_by_username(username))
    assert items
    created = items[0]
    assert created["count"] == 30

    updated = repo.update({"id": created.key.id, "count": 35})
    assert updated is not None
    refreshed = repo.read(created.key.id)
    assert refreshed["count"] == 35

    repo.delete(created.key.id)
    assert not list(repo.fetch_by_username(username))


def test_jump_rope_repository_crud(datastore_emulator):
    repo = JumpRopeRepository()
    username = "__pytest_jump__"
    _delete_test_entities(repo, username)

    record = {
        "usernickname": username,
        "activity_date": date(2025, 1, 4),
        "activity_time": time(9, 0),
        "duration": 12,
        "calories": 80,
        "count": 120,
        "notes": "test",
    }
    repo.create(record)

    items = list(repo.fetch_by_username(username))
    assert items
    created = items[0]
    assert created["count"] == 120

    updated = repo.update({"id": created.key.id, "count": 140})
    assert updated is not None
    refreshed = repo.read(created.key.id)
    assert refreshed["count"] == 140

    repo.delete(created.key.id)
    assert not list(repo.fetch_by_username(username))


def test_weight_repository_crud(datastore_emulator):
    repo = WeightRepository()
    username = "__pytest_weight__"
    _delete_test_entities(repo, username)

    record = {
        "usernickname": username,
        "weight": 82.5,
        "weighing_date": date(2025, 1, 5),
    }
    repo.create(record)

    items = list(repo.fetch_by_username(username))
    assert items
    created = items[0]
    assert created["weight"] == 82.5
    assert created["weighing_date"].date() == date(2025, 1, 5)

    updated = repo.update({"id": created.key.id, "weight": 81.0})
    assert updated is not None
    refreshed = repo.read(created.key.id)
    assert refreshed["weight"] == 81.0

    repo.delete(created.key.id)
    assert not list(repo.fetch_by_username(username))
