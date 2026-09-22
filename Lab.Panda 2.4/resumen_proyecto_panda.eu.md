# Gure ekoizpen katea

Lehen aldiz ikusten baduzu proiektu hau: hau da benetako (tira,
simulatutako) brazo robotikoak mugitzen dituen zatia, piezak fabrikatu
eta sailkatzeko. Ez duzu robotikaz ezer jakin behar orrialde hau
jarraitzeko — dena hutsetik azaltzen da.

## Zer den Webots

**Webots** robotak 3Dn simulatzen dituen programa bat da: benetako
fisika (pisua, marruskadura, talkak), benetan ikusiko luketena ikusten
duten kamera birtualak, eta robot errealaren motorren berdin-berdin
mugitzen diren motoreak. Kode irekikoa da, Cyberbotics enpresak egina,
eta asko erabiltzen da ikerkuntzan eta industrian robot bat probatzeko
**ukitu baino lehen** — simulazioko akats batek ez du ezer hausten ez
inori kalterik egiten.

Proiektu honetan, ikusten duzun guztia — brazoak, garraio-uhala, kolore
askotako kuboak, kamerak — Webotsen barruan bizi da. Ez dago benetako
brazo robotikorik nabe batean mugitzen; taller birtual osoa da.

## Panda robota nondik datorren

**Panda** benetako brazo robotiko bat da, **Franka Emika** enpresa
alemaniarrak fabrikatua. "Cobot" (robot kolaboratibo) izenekoa da:
segurtasun-jaularik gabe pertsonen ondoan lan egiteko diseinatua dago,
mugimendu bakoitzean egiten duen indarra kontrolatzen duelako eta
zehatz eta leun izateko programa daitekeelako. Munduko robotika
unibertsitate eta ikerketa-zentroetan gehien erabiltzen diren brazoetako
bat da.

Webotsek robot honen eredu 3D ofiziala dakar, bere geometria eta fisika
errealekin (7 artikulazio, benetako mugimendu-mugak, bi hatzeko pintza
bera). Horregatik, hemen simulazioan probatzen dena benetako brazoak
egingo lukeen bezala portatzen da.

![Webotsek margotzen duen Panda robota: zazpi artikulazioko brazo zuria, amaieran bi hatzeko pintzarekin, mahai baten gainean muntatua](img/panda_robot.jpg)

## Gure bi Panda

Proiektu honek ez du Panda brazo bakarra erabiltzen, **bi** baizik,
bakoitzak bere lana duela industria-gelaxka txiki baten barruan:

- **Loader** ("kargatzen duena"): piezak (kolore askotako kuboak)
  kutxa batetik hartzen ditu eta garraio-uhal baten gainean uzten ditu.
- **Sorter** ("sailkatzen duena"): uhalaren amaieran itxaroten du,
  kamera batekin zein koloretako pieza iristen den ikusten du, hartu
  eta kolore horri dagokion kutxan uzten du.

Bien artean, pieza bakoitzak bide osoa bakarrik egiten du: kargatu,
garraiatu eta sailkatu egiten da, inork ezer eskuz ukitu behar izan
gabe.

Sinplifikatzeko (ez dago kubo amaigabeko fabrikarik atzean), pieza bat
sailkatzen amaitu bezain laster **bere jatorrizko kutxara itzultzen da
bakarrik**, Loaderrak berriro hartzeko prest — horrela ekoizpen sistema
jarraitu bat simulatzen da, inoiz piezarik gabe geratzen ez dena,
benetako kubo puñatxo bat etengabe bueltaka.

![Bi Panda robotak gelaxkan lanean: Loader ezkerrean kuboak uhalean uzten, Sorter goian koloreka sailkatzen](img/webots_cell.jpg)

## "Nodoak": zer diren eta zeintzuk ditugun

Hau guztia **ROS 2**rekin (Robot Operating System) kontrolatzen da,
robotak programatzeko "sistema eragile" estandarra dena. ROS 2ren ideia
nagusia **nodoak** dira: programa txiki eta independenteak, bakoitzak
lan zehatz bat duela, elkarren artean "kanalen" (*topic* deituak) bidez
mezuak bidaliz hitz egiten dutenak — talkie-walkie talde baten antzera,
bakoitzak berea baino ez du esaten eta bere kontuko dena entzuten du.

Hauek dira gelaxka honetako nodo nagusiak, lerro batean azalduta:

- **Webots-en driverra** (robot bakoitzeko bat): "brazoa posizio
  honetara eraman" aginduak jasotzen ditu eta robot simulatua benetan
  mugitzen du Webotsen barruan. **Robota faltsua dela dakien pieza
  bakarra da**: gainerako nodoek "artikulazioak horrela jarri" eta
  "pintza honaino itxi" esaten dute besterik ez, nork betetzen duen
  jakin gabe. Horregatik, benetako Panda bat dugun egunean, driver hau
  **benetako robotaren aurka** hitz egingo luke simulatzailearen ordez,
  eta gainerako nodoak berdin-berdin geratuko lirateke. (Benetako
  Pandaren driver berarekin ordeztu beharko litzateke, eta abiadura,
  segurtasuna eta kamerak — orain ere simulatuak — kontuz probatu.)
- **`loader_demo` / `sorter_demo`**: robot bakoitzaren "burua" — urratsez
  urrats zer egin erabakitzen dute (pieza batera joan, heldu, eraman,
  askatu) eta driverrari agintzen diote.
- **Goiko kamerak**: mahaia goitik begiratzen dute eta "kubo berde bat
  dago posizio honetan" esaten dute — horrela dakidako robotak nora
  joan behar duen, inork koordenatuak eskuz esan gabe.
- **Biltegiaren gainbegiratzailea**: piezak ez galtzeaz eta posizio
  ezinezko batean ez geratzeaz arduratzen da, eta behar izanez gero
  berriro kokatzen ditu.
- **LED zubiak**: benetako Raspberry Pi Pico bat konektatuta badago,
  fabrikatzen ari den koloreko benetako LED bat pizten dute. Picorik
  gabe, gelaxkak berdin-berdin funtzionatzen du, argi fisikorik gabe
  besterik ez — hala ere simulazioa ikusi nahi baduzu, gure kontrol
  panelean dago, **Raspberry Pi Pico** fitxan.
- **Kontrol panela** (`teleop_gui`): pertsona batek robotak eskuz
  mugitzeko, ekoizpena abiarazteko eta guztiaren egoera begirada batean
  ikusteko leihoa. Egunen batean gelaxka bat baino gehiago aldi berean
  funtzionatzen badu (ekoizpen "lerro" bat baino gehiago), **bakoitzak
  bere panel independentea du** — leiho bakoitzak bere lerroko robotak
  bakarrik kontrolatzen ditu, guztiek eskaeren web panel bera partekatu
  arren.

![Eskuzko kontrol panela: EN MARCHA goiburuarekin, loteen egoera eta larrialdiko geldialdia, eta Mugimendua, Ekoizpena, Raspberry Pi Pico eta Konfigurazioa fitxak](img/panel_control_manual.png)

<a href="/manual/lanzar/assets/Documentacion/panel_control_manual.html" style="display:block; margin:0 0 1.3rem; padding:1rem 1.2rem; background:var(--bg-elevated); border:1px solid var(--line); border-left:4px solid var(--accent-brick); border-radius:6px; text-decoration:none; color:inherit;">
  <strong style="color:var(--accent-brick);">📋 Eskuzko kontrol panela, fitxaz fitxa</strong><br>
  <span style="color:var(--fg-muted); font-size:0.92rem;">Botoi eta fitxa bakoitzak zer egiten duen, bakoitzaren argazki batekin.</span>
</a>

## Ekoizpen lerro bat baino gehiago

Lerro bakoitza bere panela duen edukiontzi-multzo independentea denez
(ikusi gorago), bigarren bat piztu daiteke, hirugarren bat... makina
berean, guztiak aldi berean lanean eta eskaeren web panel bera
partekatuz, elkarri oinik jo gabe. Jada badago horretarako plantila
prest eta probatuta — urratsez urrateko gida, programatzailea izan
gabe jarraitzeko pentsatua, hemen:
[Ekoizpen lerro bat gehiago nola gehitu](/manual/lanzar/assets/Documentacion/anadir_cadena_produccion.html).

## Nola ikusi funtzionatzen

Simulazioa abiarazteko urratsak (Webots + robotak + kontrol panela)
[Nola abiarazi dena](/manual/lanzar) gidan daude — komandoak kopiatu eta
itsatsiz, hitzez hitz jarraitzeko pentsatuta dago.

## Xehetasun teknikoa nahi baduzu

Orrialde hau "zer den eta zertarako balio duen" mailan geratzen da.
Barne-arkitektura osoa (mugimenduak nola kalkulatzen diren, zein
diseinu-erabaki hartu ziren eta zergatik, nola eraiki zen kontatzen duen
historia osoa) aparte dago,
[`detalle_tecnico_panda.md`](detalle_tecnico_panda.md) fitxategian —
programatzen edo zerbait aldatzen hasi nahi duenarentzat pentsatua,
gelaxka erabiltzeko ez da irakurri behar.
