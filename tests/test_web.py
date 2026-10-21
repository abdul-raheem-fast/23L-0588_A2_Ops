from io import BytesIO

from app.web import create_app


class FakeInference:
    def predict(self, _image_bytes):
        return "Real", 0.91


class FakeStore:
    def __init__(self):
        self.items = []

    def add_prediction(self, *args):
        self.items.append(args)

    def recent(self):
        return []


def test_health_and_prediction(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'history.db'}")
    app = create_app(FakeInference(), FakeStore())
    client = app.test_client()
    assert client.get("/health").json["status"] == "ok"
    response = client.post(
        "/predict",
        data={"image": (BytesIO(b"not-an-image"), "photo.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Real" in response.data


def test_rejects_extension(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'history.db'}")
    app = create_app(FakeInference(), FakeStore())
    response = app.test_client().post(
        "/predict",
        data={"image": (BytesIO(b"data"), "payload.exe")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 302
