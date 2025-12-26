from datetime import date, time

from eridanus.repository import CrunchesRepository


def _delete_test_entities(repo, username):
    items = list(repo.fetch_by_username(username))
    for item in items:
        repo.delete(item.key.id)


def test_crunches_repository_crud(datastore_emulator):
    repo = CrunchesRepository()
    username = "__pytest__"
    _delete_test_entities(repo, username)

    record = {
        "usernickname": username,
        "activity_date": date(2025, 1, 1),
        "activity_time": time(7, 45),
        "duration": 10,
        "calories": 50,
        "count": 25,
        "notes": "test",
    }
    repo.create(record)

    items = list(repo.fetch_by_username(username))
    assert items, "Expected at least one Crunch record for the test user"
    created = items[0]
    assert created["count"] == 25
    assert created["calories"] == 50
    assert created["activity_date"].date() == date(2025, 1, 1)

    updated = repo.update({"id": created.key.id, "count": 30})
    assert updated is not None
    refreshed = repo.read(created.key.id)
    assert refreshed["count"] == 30

    repo.delete(created.key.id)
    remaining = list(repo.fetch_by_username(username))
    assert not remaining
