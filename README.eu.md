**Hizkuntza:** [Español](README.md) · [English](README.en.md) · Euskara

# Virtual Robotic

Zaletasunezko proiektu pertsonala, ez benetako enpresa bat. Jakin-minagatik
hasi zen —benetako beso robotiko bat nola mugitzen den ulertu nahi izateagatik—
eta gelaxka industrial oso bat bihurtu zen: koloretako kuboak uhal batetik
jaso eta sailkatzen dituzten bi beso, eta eskaerak benetako tailer bat balitz
bezala eramaten dituen webgune bat.

![Bi beso robotikoak uhalaren gainean lanean, koloretako kuboekin eta ikusmen artifizialeko kameren leihoekin](Virtual_Robotic/img/webots_cell.jpg)

**Gelaxka lanean ikusteko bideoak** (30 segundo bakoitza; sakatu irudia ikusteko):

[![Bideoa: Loaderrak kuboak uhalean uzten ditu eta Sorterrak jaso eta kolorearen arabera sailkatzen ditu](Virtual_Robotic/img/celda_trabajando_1.gif)](Virtual_Robotic/img/celda_trabajando_1.mp4)
[![Bideoa: bi besoak aldi berean lanean simulazioan](Virtual_Robotic/img/celda_trabajando_2.gif)](Virtual_Robotic/img/celda_trabajando_2.mp4)

## Zer dago hemen

**1. Robotekin gelaxka, simulatua.** Bi beso robotiko (Franka Emika Panda
modeloa) **Webots**-en barruan aritzen dira, benetako fisika imitatzen duen
programa batean. Batek kuboak uhal batean jartzen ditu eta besteak jaso eta
kolorearen arabera sailkatzen ditu, kamerekin egiaztatuz uste duena benetan
jaso duela. Azpian, piezek **ROS 2**-rekin hitz egiten dute, ia benetako
robot guztiek erabiltzen duten «nerbio-sistema».

**2. Eskaeren webgunea.** Tailerreko bulego gisa aritzen den webgune arrunt
bat: bezeroek eskatu, robotek fabrikatu, biltegia berez eguneratzen da eta
albaranak eta fakturak ateratzen dira. Probatzeko errazena da: ez du
simulaziorik behar.

**3. Bi Raspberry Pi Pico, aukerakoak.** Plaka txiki-txikiak (5 € inguru)
LEDekin, hurbiltasun-sentsore batekin, pantaila txiki batekin eta benetako
larrialdi-geldialdiko botoiekin. Birtualaren eta fisikoaren arteko zubia
dira, baina **haiek gabe dena berdin dabil**: kontrol-panelak pantailan
marrazten ditu.

<img src="Virtual_Robotic/img/pico_hardware.jpg" alt="Bi Raspberry Pi Pico plakak protoboard batean, LED gorri bat eta urdin bat piztuta, OLED pantaila txikia behean eta hurbiltasun-sentsorea ezkerrean" width="420">

**[Claude Code](https://claude.com/claude-code)**-rekin batera eraikia
(Anthropic): diseinua eta kodearen zati handi bat Claude-rekin egindako lan
saioetatik atera ziren.

## 3 urratsetan probatu (webgunea soilik)

[Docker](https://www.docker.com/) eta Git instalatuta:

```bash
git clone https://github.com/virtual-robotic/virtual-robotic.git
cd virtual-robotic/Taller_Administracion
docker compose up -d --build
```

Ireki **http://localhost:8000**. Hor dago aurkezpen-orria, proiektuaren
eskuliburu gisa aritzen dena, eta sartzeko botoia. Adibideko produktuak eta
bezeroak ditu jada jolasteko. Webguneak hizkuntza-hautatzailea du
(gaztelania, ingelesa, euskara).

### Nork zer egiten du webgunean

| Honela sartzen zara… | Pasahitza | Zu zara… | Hau egin dezakezu… |
|---|---|---|---|
| `admin` | `admin` | Tailerra | Dena ikusi, fabrikatzera bidali, banatu, albaranak eta fakturak atera. **Ez du eskaerarik egiten.** |
| `ere-admin` | `1111` | Adibideko bezero bat (Ereño) | **Eskaerak egin** eta bere eskaerak, albaranak eta fakturak ikusi. |

Eskaera bat hasieratik bukaeraraino probatzeko: sartu `ere-admin` gisa, egin
eskaera, eta gero sartu `admin` gisa nola banatzen eta fakturatzen den
ikusteko.

## Non dago bakoitza?

| Hau nahi dut… | Non |
|---|---|
| Dena **Linux**-en instalatu eta abiarazi (robotekin) | [LANZAR_PROYECTO.eu.md](LANZAR_PROYECTO.eu.md) — edo `./arrancar_todo.sh` |
| **Windows**-en instalatu eta abiarazi (robotekin) | [INSTALAR_WINDOWS.eu.md](INSTALAR_WINDOWS.eu.md) — edo klik bikoitza `arrancar_windows.bat`-en |
| Robot-**lerro bat baino gehiago** aldi berean | [Documentacion/anadir_cadena_produccion.md](Documentacion/anadir_cadena_produccion.md) (gaztelaniaz) |
| Webgunea erabili: eskaerak, biltegia, banaketa, fakturak | [Taller_Administracion/README.eu.md](Taller_Administracion/README.eu.md) |
| Raspberry Pi Pico plakak muntatu | [Documentacion/PI_PICO_montaje.html](Documentacion/PI_PICO_montaje.html) (gaztelaniaz) |
| Huts egiten duen zerbait konpondu | [PROBLEMAS_CONOCIDOS.eu.md](PROBLEMAS_CONOCIDOS.eu.md) |
| Barrutik nola dagoen egina jakin | [Lab.Panda 2.4/detalle_tecnico_panda.md](Lab.Panda%202.4/detalle_tecnico_panda.md) (gaztelaniaz) |

### Non dabil gaur

| | Eskaeren webgunea | Robotekin gelaxka |
|---|---|---|
| **Linux** | Bai | Bai |
| **Windows** (benetako PCa) | Bai | Bai, Webots Windows-en instalatuta |
| **VirtualBox barruko Windows** | Ez | Ez (VirtualBox-ek ez du uzten) |

## Zer dago karpeta bakoitzean

- `Lab.Panda 2.4/` — simulazioa: Webots eta roboten programa.
- `Taller_Administracion/` — eskaeren webgunea eta bere aurkezpen-orria.
- `Virtual_Robotic/` — aurkezpen-orri bera, klik bikoitzarekin Docker gabe
  irekitzeko.
- `Rasberry_Pi_Pico/` eta `Rasberry_Pi_Pico_USB_Loader/` — bi Picoen
  programa. `wifi_config.py` eta `webrepl_cfg.py` txantiloiak dira soilik:
  jarri hor zure klabeak eta **ez igo inoiz** (ikusi
  [LANZAR_PROYECTO.eu.md](LANZAR_PROYECTO.eu.md), «Zure Wi-Fia: Pico W-ren klabeak»).
- `Documentacion/` — muntatzeko gidak eta ohar teknikoak (gaztelaniaz); ez
  dago zertan irakurri abiarazteko.
- Karpeta nagusiko fitxategi solteak (`arrancar_todo.sh`,
  `arrancar_windows.bat`, `crear_linea.sh`…) dena abiarazteko eta
  itzaltzeko lasterbideak dira; gida bakoitzak azaltzen du zein erabili.
  Fitxategi eta karpeten izenak gaztelaniaz daude.

## Lizentzia

**MIT** (ikusi [LICENSE](LICENSE)). Hitz arruntetan: proiektu hau nahi
bezala erabili, kopiatu, aldatu eta partekatu dezakezu, baita helburu
komertzialetarako ere, lizentziaren oharra egilearen izenarekin mantentzen
baduzu. Dagoen bezala ematen da, bermerik gabe.

Proiektuak erabiltzen dituen besteen piezak (Webots, Panda robotaren
modeloak, ROS 2, FastAPI…) ez dira gureak eta beren lizentziekin jarraitzen
dute.
