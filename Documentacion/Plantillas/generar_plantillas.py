# Version: 2026-09-26 20:32 -- URL de Taller_Administracion en el panel de cada cadena de otro ordenador. Antes: 2026-09-26 20:17 -- paso E: explica por que las cadenas de otro ordenador llevan la IP de la principal (nota del usuario). Antes: 2026-09-26 19:52 -- ejemplo = nuestra instalacion (cadenas 1-2 en VM principal, 3-4 en el clon) y como poner el nombre de la cadena en el panel. Antes: 2026-09-26 19:46 -- apartado 9 reordenado (descargar antes de arrancar) y el principal puede ser una VM. Antes: 2026-09-26 19:45 -- anade el apartado 9 "Puesta en marcha, paso a paso" (principal primero, VM clonada, errores vistos). Antes: 2026-09-26 19:04 -- anade Ordenadores y "Donde arranca cada cadena" (cadenas en otro PC/VM). Antes: 2026-09-26 18:50 -- genera las plantillas de configuracion del taller (ejemplo y vacia). Necesita python-docx: python3 generar_plantillas.py <carpeta>
"""Genera las dos plantillas de configuracion del taller (ejemplo y vacia) con el mismo diseno."""
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AZUL = RGBColor(0x1F, 0x3A, 0x5F)
GRIS = RGBColor(0x55, 0x5B, 0x66)
FONDO_CABECERA = "DCE6F1"
FONDO_AVISO = "FFF4D6"
FONDO_NOTA = "EEF3F8"
ANCHO = 17.4  # cm utiles en A4 con margenes de 1,8

SI, NO = "✔", "☐"


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def repetir_cabecera(fila):
    trPr = fila._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def no_partir(fila):
    trPr = fila._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def alto_minimo(fila, cm):
    trPr = fila._tr.get_or_add_trPr()
    h = OxmlElement("w:trHeight")
    h.set(qn("w:val"), str(int(cm * 567)))
    h.set(qn("w:hRule"), "atLeast")
    trPr.append(h)


def campo(parrafo, instruccion):
    """Campo de Word (numero de pagina, total de paginas)."""
    run = parrafo.add_run()
    for tipo, texto in (("begin", None), (None, instruccion), ("separate", None), (None, "1"), ("end", None)):
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        elif texto == instruccion:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = f" {instruccion} "
        else:
            el = OxmlElement("w:t")
            el.text = texto
        run._r.append(el)
    return run


def texto(doc, contenido, negrita=False, cursiva=False, color=None, tam=None, antes=0, despues=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(antes)
    p.paragraph_format.space_after = Pt(despues)
    r = p.add_run(contenido)
    r.bold, r.italic = negrita, cursiva
    if color:
        r.font.color.rgb = color
    if tam:
        r.font.size = Pt(tam)
    return p


def rico(doc, trozos, estilo=None, despues=3):
    """Parrafo con trozos (texto, negrita)."""
    p = doc.add_paragraph(style=estilo)
    p.paragraph_format.space_after = Pt(despues)
    for t, b in trozos:
        p.add_run(t).bold = b
    return p


def vineta(doc, *trozos):
    if len(trozos) == 1 and isinstance(trozos[0], str):
        trozos = ((trozos[0], False),)
    return rico(doc, trozos, estilo="List Bullet", despues=2)


def codigo(doc, lineas):
    """Ordenes para copiar, en letra de maquina sobre fondo gris."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    c.width = Cm(ANCHO - 1)
    sombrear(c, "F2F2F2")
    for i, linea in enumerate(lineas):
        q = c.paragraphs[0] if i == 0 else c.add_paragraph()
        q.paragraph_format.space_after = Pt(0)
        r = q.add_run(linea)
        r.font.name = "Consolas"
        r.font.size = Pt(9)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def paso(doc, numero, titulo, explicacion=None):
    p = rico(doc, ((f"{numero}. {titulo}", True),), despues=2)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.keep_with_next = True
    if explicacion:
        texto(doc, explicacion, despues=3).paragraph_format.keep_with_next = True


def recuadro(doc, titulo, lineas, fondo):
    """Recuadro de una celda para avisos y reglas."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    no_partir(t.rows[0])
    c = t.cell(0, 0)
    c.width = Cm(ANCHO)
    sombrear(c, fondo)
    p = c.paragraphs[0]
    r = p.add_run(titulo)
    r.bold = True
    r.font.color.rgb = AZUL
    for linea in lineas:
        q = c.add_paragraph(style="List Bullet")
        q.paragraph_format.space_after = Pt(1)
        trozos = ((linea, False),) if isinstance(linea, str) else linea
        for tx, b in trozos:
            q.add_run(tx).bold = b
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def tabla(doc, cabeceras, anchos, filas, filas_vacias=0, alto_vacia=0.75, centrar=(), a_mano=False):
    t = doc.add_table(rows=1, cols=len(cabeceras))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for col, w in zip(t.columns, anchos):
        col.width = Cm(w)
    cab = t.rows[0]
    repetir_cabecera(cab)
    for i, (h, w) in enumerate(zip(cabeceras, anchos)):
        c = cab.cells[i]
        c.width = Cm(w)
        sombrear(c, FONDO_CABECERA)
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = AZUL
    for fila in list(filas) + [[""] * len(cabeceras)] * filas_vacias:
        row = t.add_row()
        no_partir(row)
        if a_mano or (not any(str(v).strip() for v in fila[1:]) and filas_vacias):
            alto_minimo(row, alto_vacia)
        for i, (v, w) in enumerate(zip(fila, anchos)):
            c = row.cells[i]
            c.width = Cm(w)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = c.paragraphs[0]
            if i in centrar:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            lineas = v if isinstance(v, list) else [v]
            for j, linea in enumerate(lineas):
                if j:
                    p = c.add_paragraph()
                    if i in centrar:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(str(linea))
                r.font.size = Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def titulo_seccion(doc, numero, nombre, explicacion, donde):
    h = doc.add_heading(f"{numero}. {nombre}", level=1)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.keep_with_next = True
    texto(doc, explicacion, despues=2).paragraph_format.keep_with_next = True
    p = texto(doc, "", despues=6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run("Dónde se mete: ")
    r.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = GRIS
    r = p.add_run(donde)
    r.font.size = Pt(9)
    r.font.color.rgb = GRIS


# ---------------------------------------------------------------- datos de ejemplo
EJ = {
    "empresa": "Taller de ejemplo S.L.",
    "fecha": "26/09/2026",
    "autor": "Persona responsable del taller",
    "grupos": [
        ["60", "Tornillería", "Tornillos, Tuercas, Arandelas", "Cadenas 2, 3 y 4"],
        ["80", "Clavos", "Clavos", "Cadena 1"],
    ],
    "ordenadores": [
        ["VM-Principal", "Linux en VirtualBox", "192.168.1.10", "Sí", "1 y 2"],
        ["VM-Cadenas2 (vm-cadenas2)", "Linux en VirtualBox, clon de la principal", "192.168.1.11", "No", "3 y 4"],
    ],
    "donde": [
        ["Cadena 1", "VM-Principal", "1", "(la tiene al lado)", "./arrancar_todo.sh   (arranca también la web)"],
        ["Cadena 2", "VM-Principal", "3", "(la tiene al lado)", './crear_linea.sh 3 2 "" 60'],
        ["Cadena 3", "VM-Cadenas2", "3", "http://192.168.1.10:8000", "./crear_linea.sh 3 3 http://192.168.1.10:8000 60"],
        ["Cadena 4", "VM-Cadenas2", "4", "http://192.168.1.10:8000", "./crear_linea.sh 4 4 http://192.168.1.10:8000 60"],
    ],
    "cadenas": [
        ["Cadena 1", "Clavos 1", "1", "80", "Solo clavos", "No", "En la VM principal"],
        ["Cadena 2", "Tornillería 2", "2", "60", "Tornillos, tuercas y arandelas", "No", "En la VM principal"],
        ["Cadena 3", "Tornillería 3", "3", "60", "Tornillos, tuercas y arandelas", "No", "En el clon; se reparte el trabajo con la 2 y la 4"],
        ["Cadena 4", "Tornillería 4", "4", "60", "Tornillos, tuercas y arandelas", "No", "En el clon"],
    ],
    "productos": [
        ["100", "Tornillos", "R  Rojo", "60", "Sí"],
        ["200", "Tuercas", "G  Verde", "60", "Sí"],
        ["300", "Arandelas", "B  Azul", "60", "Sí"],
        ["400", "Clavos", "Y  Amarillo", "80", "Sí"],
    ],
    "subproductos": [
        ["100 Tornillos", "2222", "1002222", "Tornillo 10mm", "0,12", "21"],
        ["100 Tornillos", "A20X", "100A20X", "Tornillo 20mm", "0,18", "21"],
        ["200 Tuercas", "3001", "2003001", "Tuerca 10mm", "0,08", "21"],
        ["300 Arandelas", "4001", "3004001", "Arandela 10mm", "0,05", "21"],
        ["400 Clavos", "C030", "400C030", "Clavo 30mm", "0,03", "21"],
        ["400 Clavos", "C050", "400C050", "Clavo 50mm", "0,04", "21"],
    ],
    "paquetes": [
        ["P010", "Paquete de 10",
         ["10 × 1002222 Tornillo 10mm", "10 × 2003001 Tuerca 10mm", "10 × 3004001 Arandela 10mm"], "2,20", "21"],
        ["P020", "Paquete de 20",
         ["20 × 100A20X Tornillo 20mm", "20 × 2003001 Tuerca 10mm", "20 × 3004001 Arandela 10mm"], "5,50", "21"],
        ["P100", "Caja de 100 clavos", ["100 × 400C030 Clavo 30mm"], "(vacío: 3,00)", "21"],
    ],
    "usuarios": [
        ["jefe-taller", "Ana López", "Sí", "No", "Ve pedidos y producción"],
        ["operario1", "Mikel Etxebarria", "Sí", "No", ""],
        ["administracion", "Laura Gómez", "No", "Sí", "Albaranes, facturas y clientes"],
        ["gerente", "Nombre Apellido", "Sí", "Sí", "Ve todo"],
    ],
}

COLORES = [
    ["R", "Rojo", "Sí"], ["G", "Verde", "Sí"], ["B", "Azul", "Sí"],
    ["Y", "Amarillo", "Solo luz"], ["M", "Magenta", "Solo luz"],
    ["C", "Cian", "Solo luz"], ["W", "Blanco", "Solo luz"],
]


def generar(ruta: Path, ejemplo: bool):
    d = EJ if ejemplo else None
    doc = Document()

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.orientation = WD_ORIENT.PORTRAIT
    for lado in ("left_margin", "right_margin"):
        setattr(sec, lado, Cm(1.8))
    sec.top_margin, sec.bottom_margin = Cm(1.8), Cm(1.6)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.font.size = Pt(10.5)
    for nombre, tam in (("Heading 1", 14), ("Title", 22)):
        st = doc.styles[nombre]
        st.font.name = "Calibri"
        st.font.size = Pt(tam)
        st.font.color.rgb = AZUL
        st.font.bold = True
        rfonts = st.element.rPr.find(qn("w:rFonts"))
        for a in ("w:ascii", "w:hAnsi", "w:asciiTheme", "w:hAnsiTheme"):
            if rfonts is not None and rfonts.get(qn(a)) is not None:
                del rfonts.attrib[qn(a)]
        st.element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        st.element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")

    # cabecera y pie
    cab = sec.header.paragraphs[0]
    r = cab.add_run("Configuración del taller" + (f"  ·  {d['empresa']}" if d else ""))
    r.font.size, r.font.color.rgb = Pt(8.5), GRIS
    pie = sec.footer.paragraphs[0]
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for trozo in ("Página ", "PAGE", " de ", "NUMPAGES"):
        run = campo(pie, trozo) if trozo.isupper() else pie.add_run(trozo)
        run.font.size, run.font.color.rgb = Pt(8.5), GRIS

    # portada breve
    doc.add_paragraph("Configuración del taller", style="Title").paragraph_format.space_after = Pt(2)
    texto(doc, "Productos, subproductos, paquetes, cadenas de producción y usuarios"
          + ("  —  EJEMPLO RELLENADO" if ejemplo else ""), color=GRIS, tam=11, despues=10)

    tabla(doc, ["Empresa", "Fecha", "Rellenado por"], [7.4, 3.4, 6.6],
          [[d["empresa"], d["fecha"], d["autor"]]] if d else [["", "", ""]],
          filas_vacias=0, a_mano=not d)

    doc.add_heading("Cómo usar esta plantilla", level=1)
    texto(doc, "Rellénala en orden, de arriba abajo: cada apartado usa lo que se decidió en el anterior.", despues=3)
    vineta(doc, ("Primero se deciden los ", False), ("grupos", True),
           (" (qué familias de productos hay) y qué ", False), ("cadenas", True), (" fabrican cada grupo.", False))
    vineta(doc, ("Luego, en qué ", False), ("ordenador", True),
           (" funciona cada cadena (puede haber cadenas en otro PC o en una máquina virtual).", False))
    vineta(doc, ("Después el ", False), ("catálogo", True),
           (": productos, sus tamaños o variantes (subproductos) y los paquetes que se venden hechos.", False))
    vineta(doc, ("Por último los ", False), ("usuarios", True), (" de la empresa y qué parte ve cada uno.", False))
    vineta(doc, "Con la plantilla rellena, se pasa todo a la web del taller y al panel de control de cada cadena "
                "(al final hay una lista para comprobar que no falta nada).")
    if ejemplo:
        texto(doc, "Este ejemplo es nuestra instalación: cuatro cadenas en dos máquinas virtuales. La 1 y la 2 van "
                   "en la VM principal (la que lleva la web del taller) y la 3 y la 4 en su clon. La 1 solo hace "
                   "clavos; la 2, la 3 y la 4 hacen tornillos, tuercas y arandelas.", cursiva=True, color=GRIS, antes=4)

    recuadro(doc, "Reglas de numeración (léelas antes de empezar)", [
        (("Nº Máquina: ", True), ("del 1 al 49, uno distinto para cada cadena. Nunca el 0 (significa «pedido libre»).", False)),
        (("Grupo: ", True), ("del 50 al 99. El 0 es el grupo de los productos que no tienen grupo.", False)),
        (("Nunca el mismo número para una máquina y un grupo: ", True),
         ("el pedido guarda los dos en el mismo sitio y la cadena se confundiría.", False)),
        (("El grupo se pone al producto, no al subproducto: ", True),
         ("todos los tamaños de tornillo van a las mismas cadenas.", False)),
        (("Varias cadenas pueden tener el mismo grupo: ", True),
         ("se reparten los pedidos solas y nunca hacen dos veces el mismo.", False)),
        (("Códigos: ", True), ("producto = 3 letras o cifras; subproducto = 4. El código completo es los dos seguidos "
                               "(100 + 2222 = 1002222).", False)),
    ], FONDO_NOTA)

    # 1. grupos
    titulo_seccion(doc, 1, "Grupos de cadena",
                   "Cada grupo es una familia de productos. Las cadenas de un grupo solo fabrican los productos de ese grupo.",
                   "no se da de alta en ningún sitio: es el número que luego se pone al producto (apartado 4) y a la cadena (apartado 3).")
    tabla(doc, ["Nº grupo", "Nombre del grupo", "Productos que fabrica", "Cadenas que lo tienen"],
          [2.2, 4.2, 6.2, 4.8], d["grupos"] if d else [], filas_vacias=0 if d else 5, centrar=(0,))

    # 2. ordenadores
    titulo_seccion(doc, 2, "Ordenadores",
                   "Los ordenadores donde funcionan las cadenas. La web del taller va en uno solo (el principal); "
                   "las cadenas de los demás se conectan a ella por la red.",
                   "no se da de alta en ningún sitio: sirve para saber qué hay que arrancar en cada ordenador.")
    tabla(doc, ["Nombre", "Tipo (Linux, Windows, VM)", "Dirección IP", "¿Tiene la web?", "Cadenas que arranca"],
          [3.4, 4.4, 3.0, 2.4, 4.2], d["ordenadores"] if d else [],
          filas_vacias=0 if d else 3, alto_vacia=1.0, centrar=(2, 3))
    recuadro(doc, "Si una cadena está en otro ordenador", [
        (("La web del taller va solo en el ordenador principal. ", True),
         ("Las cadenas de fuera se conectan a ella con su dirección: http://IP_DEL_PRINCIPAL:8000.", False)),
        (("El ordenador principal necesita una IP fija ", True),
         ("(o reservada en el router): si cambia, las cadenas de fuera dejan de ver los pedidos.", False)),
        (("Una máquina virtual tiene que estar en la misma red: ", True),
         ("en VirtualBox, la red en modo «Adaptador puente», para que tenga su propia IP.", False)),
        (("El Nº de línea solo tiene que ser distinto dentro de cada ordenador ", True),
         ("(el principal y otra VM pueden tener cada uno su línea 3). La 1 se arranca con arrancar_todo; "
          "las demás, del 3 en adelante, con crear_linea.", False)),
        (("El Nº Máquina, en cambio, no se repite en ningún ordenador.", True),),
        (("En Windows ", True), ("la dirección de la web se escribe en el panel de control, pestaña Configuración.", False)),
        (("Las Pico se enchufan al ordenador donde funciona su cadena.", True),),
        (("Cada cadena es un Webots completo: ", True), ("una VM con 4 procesadores y 6 GB de memoria mueve dos "
                                                         "cadenas, pero va justa (medido).", False)),
        (("Si clonas una VM: ", True), ("marca «Generar nuevas direcciones MAC» y, ya en la copia, cambia el nombre del "
                                       "equipo y el Nº Máquina de sus cadenas (la copia arrastra los de la original).", False)),
    ], FONDO_NOTA)

    # 3. cadenas
    titulo_seccion(doc, 3, "Cadenas de producción",
                   "Una fila por cadena (línea de robots). El Nombre es para reconocerla de un vistazo; Nº Máquina es su "
                   "número propio; Grupo dice qué productos fabrica.",
                   "panel de control de cada cadena, pestaña Configuración (con la clave): nombre, Nº Máquina, Grupo Cadena y Pico.")
    tabla(doc, ["Cadena", "Nombre (en el panel)", "Nº Máquina", "Grupo", "Qué fabrica", "Pico", "Notas"],
          [1.9, 3.0, 1.8, 1.4, 3.6, 1.9, 3.8],
          d["cadenas"] if d else [[f"Cadena {i}", "", "", "", "", f"{NO} Sí  {NO} No", ""] for i in range(1, 6)],
          filas_vacias=0 if d else 2, centrar=(2, 3), a_mano=not d, alto_vacia=1.0)
    texto(doc, "Las Raspberry Pi Pico (botón de parada y luces) solo pueden obedecer a una cadena a la vez: "
               "márcalas en una sola fila.", cursiva=True, color=GRIS, tam=9)

    h = texto(doc, "Cómo se configura cada cadena en su panel de control (nombre, Grupo, Nº Máquina y URL de la web)",
              negrita=True, color=AZUL, antes=8, despues=4)
    h.paragraph_format.keep_with_next = True
    for linea in (
        (("Abre el panel de control de la cadena y ve a la pestaña ", False), ("Configuración", True), (".", False)),
        (("Pulsa ", False), ("«Desbloquear (clave)»", True),
         (" y escribe la clave. La de fábrica es 1111; conviene cambiarla allí mismo, en «Cambiar clave de "
          "configuración».", False)),
        (("En el recuadro ", False), ("«Identidad de la cadena»", True), (", escribe el nombre en ", False),
         ("«Nombre de la cadena»", True), (" y pulsa ", False), ("Guardar", True), (" (o Enter).", False)),
        (("Debajo están ", False), ("Grupo Cadena", True), (" y ", False), ("Nº Máquina", True),
         (": elige el número en cada lista y pulsa su Guardar. Cada campo tiene el suyo.", False)),
        (("Justo debajo está ", False), ("«URL de Taller_Administracion»", True),
         (": si la cadena funciona en otro ordenador que la web, escribe la dirección de la web del principal "
          f"(http://{'192.168.1.10' if d else 'IP_DEL_PRINCIPAL'}:8000) y pulsa su Guardar. Si está en el mismo "
          "ordenador que la web, déjalo vacío.", False)),
        (("Vuelve a bloquear la pestaña al terminar.", False),),
    ):
        p = rico(doc, linea, estilo="List Number", despues=2)
    texto(doc, "El nombre se ve en grande arriba del panel, en el título de la ventana y en el letrero de la vista "
               "3D de Webots (con el grupo y la máquina debajo). Se guarda y se mantiene al volver a arrancar. "
               "Un nombre que diga qué hace y qué número es (por ejemplo «Tornillería 3») evita confundir paneles.",
          cursiva=True, color=GRIS, tam=9, antes=3)
    recuadro(doc, "Sin la URL, una cadena de otro ordenador no ve los pedidos", [
        "La cadena arranca y el panel funciona, pero busca la web en su propio ordenador, donde no hay ninguna "
        "(o hay otra distinta), y no aparece ningún pedido del principal.",
        "crear_linea.sh ya la deja puesta si se le da la dirección; aun así, compruébala en el panel de cada cadena.",
        "Si la IP del principal cambia, hay que corregir la URL en el panel de todas las cadenas de los demás ordenadores.",
    ], FONDO_AVISO)

    h = texto(doc, "Dónde arranca cada cadena", negrita=True, color=AZUL, antes=8, despues=4)
    h.paragraph_format.keep_with_next = True
    t = tabla(doc, ["Cadena", "Ordenador", "Nº línea", "Dirección de la web del taller", "Orden para arrancarla"],
              [2.1, 2.6, 1.5, 4.0, 7.2],
              d["donde"] if d else [[f"Cadena {i}", "", "", "", ""] for i in range(1, 6)],
              filas_vacias=0 if d else 2, centrar=(2,), a_mano=not d, alto_vacia=1.0)
    for fila in t.rows[1:]:
        for r in fila.cells[4].paragraphs[0].runs:
            r.font.name = "Consolas"
            r.font.size = Pt(8.5)
    texto(doc, "Orden: crear_linea.sh <Nº línea> <Nº Máquina> <dirección de la web> <Grupo>. En el mismo ordenador "
               "que la web, la dirección se deja vacía (\"\"). En Windows: crear_linea_windows.bat.",
          cursiva=True, color=GRIS, tam=9)

    # 3. productos
    titulo_seccion(doc, 4, "Productos",
                   "La familia de pieza (tornillos, clavos...). Es lo que la cadena fabrica y lo que se guarda en el almacén.",
                   "web del taller, catálogo de productos.")
    tabla(doc, ["Código (3)", "Nombre", "Luz (color)", "Grupo", "Activo"],
          [2.4, 5.4, 3.8, 2.2, 3.6], d["productos"] if d else [],
          filas_vacias=0 if d else 8, centrar=(0, 3, 4))
    texto(doc, "Cada producto activo lleva un color distinto (o ninguno). Solo el rojo, el verde y el azul tienen cubo "
               "en la simulación; el resto se ven solo con la luz.", cursiva=True, color=GRIS, tam=9)

    # 4. subproductos
    titulo_seccion(doc, 5, "Subproductos",
                   "Los tamaños o variantes de cada producto. Es lo que pide el cliente y lo que lleva precio.",
                   "web del taller, dentro de cada producto.")
    tabla(doc, ["Producto", "Código (4)", "Código completo", "Nombre", "Precio € sin IVA", "IVA %"],
          [3.2, 2.2, 2.8, 4.6, 2.8, 1.8], d["subproductos"] if d else [],
          filas_vacias=0 if d else 12, centrar=(1, 2, 4, 5))

    # 5. paquetes
    titulo_seccion(doc, 6, "Paquetes",
                   "Lotes cerrados de varios subproductos con cantidades fijas. No tienen almacén propio: al pedir un "
                   "paquete se piden sus piezas, y cada una la fabrica la cadena de su grupo.",
                   "web del taller, catálogo de paquetes.")
    tabla(doc, ["Código", "Nombre", "Qué lleva (cantidad × subproducto)", "Precio € paquete", "IVA %"],
          [2.0, 3.6, 7.0, 3.0, 1.8], d["paquetes"] if d else [],
          filas_vacias=0 if d else 6, alto_vacia=1.6, centrar=(0, 3, 4))
    texto(doc, "Precio vacío = se cobra la suma de lo que lleva, cada pieza a su precio.",
          cursiva=True, color=GRIS, tam=9)

    # 6. usuarios
    titulo_seccion(doc, 7, "Usuarios de la empresa",
                   "Quién entra en la web del taller y qué parte ve: Taller (pedidos y producción) o Administración "
                   "(clientes, albaranes y facturas). Se pueden marcar las dos.",
                   "web del taller, usuarios.")
    recuadro(doc, "En preparación", [
        "El reparto «unos ven solo Taller y otros solo Administración» todavía se está haciendo. "
        "De momento este apartado sirve para dejar apuntado quién tiene que ver qué.",
    ], FONDO_AVISO)
    tabla(doc, ["Usuario", "Nombre y apellidos", "Taller", "Administración", "Notas"],
          [3.0, 4.4, 1.8, 3.4, 4.8], d["usuarios"] if d else [],
          filas_vacias=0 if d else 8, centrar=(2, 3))

    # 7. colores
    titulo_seccion(doc, 8, "Colores de luz disponibles",
                   "Los que trae el taller de serie, para elegir la luz de cada producto en el apartado 4.",
                   "web del taller, colores (se pueden añadir más).")
    tabla(doc, ["Código", "Color", "Cubo en la simulación"], [2.4, 4.0, 5.0], COLORES, centrar=(0,))

    # 9. puesta en marcha
    ip = "192.168.1.10" if d else "IP_DEL_PRINCIPAL"
    titulo_seccion(doc, 9, "Puesta en marcha, paso a paso",
                   "El principal puede ser un PC o una máquina virtual: es el que lleva la web del taller. "
                   "El orden importa: primero se arranca el principal y después los demás, que se conectan a su web.",
                   "terminal de cada ordenador.")
    paso(doc, "A", "Si es una VM clonada: prepararla (solo la primera vez)",
         "Al clonar en VirtualBox: «Clon completo» y «Generar nuevas direcciones MAC». Si la opción Clonar no "
         "aparece, pasa VirtualBox a modo Experto. Ya dentro de la copia:")
    codigo(doc, ["sudo hostnamectl set-hostname vm-cadenas2",
                 "sudo rm /etc/machine-id /var/lib/dbus/machine-id",
                 "sudo systemd-machine-id-setup",
                 "sudo reboot"])
    texto(doc, "Después del reinicio, hostname -I tiene que dar una IP distinta de la VM original.", despues=4)
    paso(doc, "B", "En cada ordenador: entrar como el usuario que tiene Docker",
         "La carpeta de trabajo y el permiso de Docker son de ese usuario (en nuestras VM, aladin).")
    codigo(doc, ["su - aladin"])
    paso(doc, "C", "En cada ordenador: descargar el proyecto (solo la primera vez)")
    codigo(doc, ["cd ~/Carga",
                 "git clone https://github.com/virtual-robotic/virtual-robotic.git robotica",
                 "cd robotica"])
    paso(doc, "D", "En el principal: arrancar todo",
         "Arranca la web del taller y la cadena 1, y abre su panel de control. Solo se hace en el principal. "
         "Esta orden no lleva números: el nombre, el Nº Máquina y el Grupo de la cadena 1 se ponen después "
         "en su panel, pestaña Configuración (ver apartado 3).")
    codigo(doc, ["./arrancar_todo.sh"])
    texto(doc, f"Comprueba desde otro equipo que la web se abre: http://{ip}:8000", despues=4)
    paso(doc, "E", "Las demás cadenas: en el principal sin dirección, en los otros con la de la web",
         "Una orden por cadena, con los números de la tabla «Dónde arranca cada cadena». La primera vez tarda "
         "(descarga y compila); al acabar abre el panel de esa cadena.")
    codigo(doc, (['./crear_linea.sh 3 2 "" 60                          # en la principal: cadena 2',
                  f"./crear_linea.sh 3 3 http://{ip}:8000 60     # en el clon: cadena 3",
                  f"./crear_linea.sh 4 4 http://{ip}:8000 60     # en el clon: cadena 4"] if d else
                 [f"./crear_linea.sh <Nº línea> <Nº Máquina> http://{ip}:8000 <Grupo>"]))
    recuadro(doc, "¿Por qué a unas cadenas se les pone la IP de la principal y a otras no?", [
        (("Cadena en el mismo ordenador que la web ", True), ("(en el ejemplo, la 2): la encuentra sola, por eso su "
                                                              "dirección va vacía (\"\").", False)),
        (("Cadena en otro ordenador ", True), ("(la 3 y la 4, que se ejecutan en el clon): ese ordenador no tiene web "
                                               "propia. Para ver los pedidos y apuntar lo que fabrica tiene que hablar por "
                                               "la red con la web de la principal, y para encontrarla necesita su "
                                               f"dirección: la IP de la principal y el puerto 8000 (http://{ip}:8000).", False)),
        (("Si esa dirección está mal o la IP de la principal cambia, ", True),
         ("la cadena arranca pero no ve ningún pedido.", False)),
    ], FONDO_NOTA)
    paso(doc, "F", "Comprobar en el panel de cada cadena",
         "En la pestaña Configuración, pon su nombre, Grupo y Nº Máquina y, si está en otro ordenador, la URL de la web "
         "del principal (apartado 3). Arriba tiene que verse ese nombre con el grupo y la máquina correctos, y en "
         "Producción tienen que verse los pedidos de la web.")
    recuadro(doc, "Errores que ya nos han pasado", [
        (("arrancar_todo solo en el principal: ", True), ("en los demás arrancaría otra web del taller.", False)),
        (("La IP del principal puede cambiar sola ", True), ("(a una VM ya le pasó: de .133 a .125). Resérvala en el "
                                                             "router o las demás cadenas dejan de ver los pedidos.", False)),
        (("Borrar con sudo: ", True), ("las carpetas creadas por Docker son de root. Para vaciar una carpeta sin "
                                       "borrarla: sudo find <carpeta> -mindepth 1 -delete. Nunca sobre el enlace "
                                       "~/Carga ni sobre /srv/docker_datos entero (ahí están los datos de Docker).", False)),
        (("sudo rm -rf carpeta/* «no borra»: ", True), ("el * lo expande tu usuario, que no puede leer dentro; "
                                                        "usa la orden con find de arriba.", False)),
        (("arrancar_todo en el clon por error: ", True), ("el clon levantó su propia web y su cadena 1, y ese panel "
                                                          "no veía los pedidos del principal. Se para con: docker stop "
                                                          "taller_admin_api ros2_panda_dev24 webots_panda_sim24.", False)),
        (("En la VM, ~ puede no ser aladin: ", True), ("si entras como otro usuario, usa rutas completas "
                                                        "(/home/aladin/Carga).", False)),
    ], FONDO_AVISO)

    # comprobaciones
    doc.add_heading("Antes de darla por buena", level=1).paragraph_format.page_break_before = True
    for linea in (
        "Cada cadena tiene un Nº Máquina distinto, y ninguno es 0.",
        "Ningún número de máquina coincide con un número de grupo.",
        "Cada grupo que tiene productos tiene al menos una cadena encendida (si no, sus pedidos nunca se fabrican).",
        "Cada producto activo tiene un color distinto (o ninguno).",
        "Los códigos de subproducto no se repiten dentro del mismo producto.",
        "Los paquetes solo llevan subproductos que existen en el apartado 5.",
        "Las Pico están marcadas en una sola cadena, y enchufadas al ordenador donde funciona esa cadena.",
        "El ordenador principal (el de la web) tiene IP fija.",
        "Cada cadena de otro ordenador tiene puesta la URL de la web del principal en su panel y ve los pedidos.",
    ):
        rico(doc, ((f"{NO}  ", False), (linea, False)), despues=2)

    doc.save(ruta)


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    generar(destino / "Configuracion_Taller_EJEMPLO.docx", ejemplo=True)
    generar(destino / "Configuracion_Taller_VACIA.docx", ejemplo=False)
    print("ok")
