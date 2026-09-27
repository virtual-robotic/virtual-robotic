"""Videos de la portada servidos por trozos (Range), que es lo que exige Safari."""
from app.main import BASE_DIR

VIDEO = "/static/img/celda_trabajando_1.mp4"
TOTAL = (BASE_DIR / "static" / "img" / "celda_trabajando_1.mp4").stat().st_size


def test_video_sin_range_entero_y_anuncia_bytes(client):
    r = client.get(VIDEO)
    assert r.status_code == 200
    assert r.headers["accept-ranges"] == "bytes"
    assert r.headers["content-type"] == "video/mp4"
    assert len(r.content) == TOTAL


def test_video_primera_sonda_de_safari(client):
    # Safari empieza siempre pidiendo "bytes=0-1" y sin un 206 se rinde.
    r = client.get(VIDEO, headers={"Range": "bytes=0-1"})
    assert r.status_code == 206
    assert r.headers["content-range"] == f"bytes 0-1/{TOTAL}"
    assert len(r.content) == 2


def test_video_trozo_abierto_y_sufijo(client):
    r = client.get(VIDEO, headers={"Range": "bytes=100-"})
    assert r.status_code == 206 and len(r.content) == TOTAL - 100
    r = client.get(VIDEO, headers={"Range": "bytes=-50"})
    assert r.status_code == 206 and r.headers["content-range"] == f"bytes {TOTAL - 50}-{TOTAL - 1}/{TOTAL}"


def test_video_fuera_de_rango_y_que_no_existe(client):
    assert client.get(VIDEO, headers={"Range": f"bytes={TOTAL}-"}).status_code == 416
    assert client.get("/static/img/no_existe.mp4").status_code == 404
    # el resto de /static sigue saliendo por StaticFiles
    assert client.get("/static/img/celda_trabajando_1.jpg").status_code == 200
