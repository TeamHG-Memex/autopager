from autopager.storage import Storage


def test_storage():
    storage = Storage()
    X, y = storage.get_Xy()
    assert len(X) == len(y)
