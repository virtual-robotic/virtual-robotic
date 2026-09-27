# Version: 2026-09-27 18:37 -- descarga de las plantillas Word de configuracion
"""Plantillas Word (/plantillas): solo las dos de la lista, nunca otro fichero del repo."""
import pytest

from app.main import PLANTILLAS


@pytest.mark.parametrize("nombre", sorted(PLANTILLAS))
def test_plantilla_se_descarga_igual_que_en_el_repo(client, nombre):
    r = client.get(f"/plantillas/{nombre}")
    assert r.status_code == 200
    assert "attachment" in r.headers["content-disposition"]
    assert r.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert r.content == PLANTILLAS[nombre].read_bytes()


@pytest.mark.parametrize("nombre", ["generar_plantillas.py", "..%2F..%2FLICENSE", "otra.docx"])
def test_fuera_de_la_lista_no_se_sirve(client, nombre):
    assert client.get(f"/plantillas/{nombre}").status_code == 404
