# Version: 2026-09-19 11:17 -- calculo de importes (base, IVA por tipo, total) compartido por albaranes y facturas
"""Importes en CENTIMOS enteros (nunca float). Una sola regla para albaranes y
facturas, para que un albaran y la factura que lo recoge cuadren al centimo.

El IVA se calcula por TIPO: se suman las bases de todas las lineas del mismo
porcentaje y se redondea UNA vez la cuota de ese grupo -- como se hace en una
factura espanola (base imponible por tipo), no linea a linea. El redondeo es
medio centimo hacia arriba en valor absoluto, y simetrico: una rectificativa
(cantidades negativas) da exactamente el negativo de la factura original.
(round() de Python redondea 12,5 a 12: no vale para una factura.)"""
from dataclasses import dataclass


def cuota_iva(base_centimos: int, iva_porcentaje: int) -> int:
    signo = -1 if base_centimos < 0 else 1
    return signo * ((abs(base_centimos) * iva_porcentaje + 50) // 100)


@dataclass
class Importes:
    base: int
    iva: int
    total: int
    desglose: list[dict]  # [{iva_porcentaje, base_centimos, iva_centimos}], por tipo ascendente


def calcular(lineas) -> Importes:
    """'lineas': objetos con cantidad, precio_unitario_centimos, iva_porcentaje."""
    bases: dict[int, int] = {}
    for linea in lineas:
        bases[linea.iva_porcentaje] = bases.get(linea.iva_porcentaje, 0) + (
            linea.cantidad * linea.precio_unitario_centimos
        )
    desglose = [
        {"iva_porcentaje": pct, "base_centimos": base, "iva_centimos": cuota_iva(base, pct)}
        for pct, base in sorted(bases.items())
    ]
    base_total = sum(d["base_centimos"] for d in desglose)
    iva_total = sum(d["iva_centimos"] for d in desglose)
    return Importes(base_total, iva_total, base_total + iva_total, desglose)
