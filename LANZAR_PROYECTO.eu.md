_Azken aldaketa: 2026-09-29 14:38_

# Proiektua abiarazi (Linux)

**Linuxerako** gida. Windows-en, ikusi [INSTALAR_WINDOWS.eu.md](INSTALAR_WINDOWS.eu.md).

## Lehenik eta behin: behar dena instalatu

**Linux Mint / Ubuntu 24.04**-n probatua. Hau behar da:

- **Eskaeren webgunea soilik:** Docker (Docker Compose v2-rekin) eta Git.
- **Robotekin gelaxka:** aurrekoa, gehi mahaigain grafiko bat (SSH bidez
  sartzea ez da nahikoa), 15 GB inguru disko, 8 GB RAM edo gehiago, eta
  internet lehen aldian. Txartel grafikoarekin arin dabil; hura gabe
  `docker-compose.yml`-ko lerro bat (`/dev/dri`) kendu behar da, beherago
  azaltzen den bezala, eta motelago dabil.

Gainerako guztia (Python, ROS 2, Webots…) Docker barruan doa, ez da
instalatu behar. Raspberry Pi Pico plakak aukerakoak dira.

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-v2
sudo apt install -y x11-xserver-utils      # robotekin gelaxkarako bakarrik
sudo usermod -aG docker $USER              # eta itxi saioa eta sartu berriro
docker --version && docker compose version # badabilela egiaztatu

git clone https://github.com/virtual-robotic/virtual-robotic.git
```

**Eskaeren webgunea soilik** ikusteko, nahikoa da:

```bash
cd virtual-robotic/Taller_Administracion
docker compose up -d --build               # eta ireki http://localhost:8000
```

## Abiarazi

Azpiko `cd` guztiak **proiektuaren karpetarekiko erlatiboak** dira
(`virtual-robotic` klonatuta edo kopiatuta duzun tokia, edo `Robotica`
zure kopia bada). Kokatu hor lehenbizi:

```bash
cd virtual-robotic   # edo zuk duzun karpeta
```

**Lasterbidea:** `./arrancar_todo.sh` batek azpiko A eta B ataletako
urratsak tiroan egiten ditu (Pico fisikoak gabe) eta eskuzko kontrol
panela irekitzen amaitzen du. Sesio grafiko lokala behar du (SSH
hutsarekin ez du balio) eta `xhost`.

**Lehen aldiz, hobe EZ erabili lasterbidea — abiarazi eskuz, urratsez
urrats (azpiko A eta B ataletan).** Ez da scripta hondatuta dagoelako:
Webots-en irudiaren lehen eraikuntzak pakete handi bat deskargatzen du
(Webots bera) eta **askoz denboran trabatuta ematen du % 70-80
inguruan** — urratsak banan-banan ikusi gabe, erraza da zerbait huts
egin duela pentsatu eta eraikuntza erdian moztea (eta hori bai,
benetan erdi geratzen da eraikuntza). Eskuz eginez, zehazki zein
urratsetan gelditzen den eta bakoitzak zenbat irauten duen ikusten
duzu; zure makinan/VMn funtzionatzen duela dakizunean, erabili lasai
`./arrancar_todo.sh` hurrengo aldietan, dagoeneko eraikitako guztia
berrerabiltzen du eta azkar doa.

![Webots-en leihoa "Downloading assets"n trabatuta % 72an, Cancel botoiarekin — hau normala da lehen aldiz, ez da hutsegite bat](img/webots_atasco_72_porciento.png)

Hau da hain zuzen ikusiko duzuna: Webots-en leiho bat "Downloading
assets"en trabatuta, % 70 eta % 90 artean, tarte on batez. **Ez sakatu
Cancel.**

**Zergatik gertatzen den "lehen aldiz" bakarrik:** Docker-ek irudiaren
eraikuntzako urrats bakoitza cachean gordetzen du. Webots-en paketea
deskargatzea behin ondo amaitzen denean cachean geratzen den urrats
bat da — irudi bera hurrengoan eraikitzean guztiz saltatzen du eta
% 70-80 hegan pasatzen du. Ez du zertan izan literalki zure lehen aldia
proiektua abiarazten: irudi zehatz hori makina horretan eraikitzen den
lehen aldia da (klona ezabatu eta berriro klonatzen baduzu, edo
`docker system prune` egiten baduzu, berriro itxaron beharko duzu
horretan).

**`arrancar_todo.sh`-ek lehen aldian funtzionatzen ez badu** (kontrol
panela ez bada irekitzen, edo kontrolagailuak ez badira konektatzen
saiakera automatikoa izan arren), errazena, eta praktikan onen
funtzionatzen duena, `./cerrar_todo.sh` da ondoren berriro
`./arrancar_todo.sh` — zuzenean ikusita bigarren buelta ondo abiarazten
dela lehenak ez badu ere. Ez dugu zehazki lokalizatu zergatik huts
egiten duen batzuetan hasiera hotz baten ondoren, beraz oraingoz
funtzionatzen duen errezeta da hau, ez azalpen osoa.

Scriptak hala ere huts egiten badizu edo arraro ematen badu, edo
komando solteak nahi badituzu, jarraitu irakurtzen — scriptak egiten
duen sekuentzia bera da, urratsez urrats azalduta.

**Bi proiektu independente** daude sarearen bidez (HTTP) hitz egiten
dutenak, kodea ez edukiontzirik partekatu gabe:

1. **`Lab.Panda 2.4`** — simulazioa (Webots + ROS 2): bi Panda brazo
   (Loader eta Sorter) kuboak uhal batean mugitzen eta koloreka
   sailkatzen dituztenak, gehi bi Raspberry Pi Pico bakoitzak benetako
   LED RGB batekin.
2. **`Taller_Administracion`** — eskaera eta biltegi web-zerbitzaria
   (FastAPI + SQLite). Robotak zer fabrikatzen duen HTTP bidez jakiten
   du; itzalita badago, simulazioak berdin-berdin funtzionatzen
   jarraitzen du, inork ekoizpena eskaera bati apuntatzen ez dion
   ezik.

Behar duzun bakarra abiarazi dezakezu. Benetako ekoizpena egin nahi
baduzu (eskaerak bakarrik osatzea), biak behar dira.

## Proiektu osoaren 3 Docker edukiontziak

| Edukiontzia | Zein proiektutakoa | Zer den |
|---|---|---|
| `webots_panda_sim24` | Lab.Panda 2.4 | Simulazio 3Da (Webots) |
| `ros2_panda_dev24` | Lab.Panda 2.4 | ROS 2 eta Python nodo guztiak (brazoak, kamerak, LEDak, kontrol panela) |
| `taller_admin_api` | Taller_Administracion | Eskaera/biltegi web-zerbitzaria |

Egiaztatu `docker ps`rekin. **Beste izen batzuk ikusten badituzu**
(`ros2_dev`, `webots_sim`, edo berberak amaieran `24` gabe) proiektu
zahar bateko hondarrak dira, jada ezabatua (`Lab.Panda 2.3`) — geldi
eta ezabatu jarraitu baino lehen: `docker stop <izena> && docker rm <izena>`.

---

## A atala — Taller_Administracion (sinpleena, Webots gabe)

```bash
cd Taller_Administracion
docker compose up -d --build
```

Ireki **http://localhost:8000**: "Virtual Robotic" aurkezpen web-orria
ateratzen da (`Virtual_Robotic/index.html` bera, baina app honek
benetan zerbitzatuta). Sakatu "Sartu" `admin` / `admin` hasierako
erabiltzailearekin eta zuzenean benetako sistemara pasatzen zara
`/panel`-en -- saio bakarra, ez da han berriro sartu behar.

Sortzen den `normal` erabiltzaile edozeinek ere `1111` pasahitz
nagusiarekin sartzen jarraitzen du (kontu bat eman gabe norbaitek
"jolastu" ahal izateko pentsatua); `admin_sistema`/`admin_cliente`
kasuan nagusiak `TALLER_DEV_MODE=true` dagoenean bakarrik balio du
(jada aktibo dago proiektu honen `docker-compose.yml`n).

**Datu-base hutsaren aurka lehen aldiz abiaraztean**, zerbitzariak
berak adibidezko datuak ereiten ditu, guztiz hutsetik ez hasteko: 7 LED
kolore, 3 produktu (Torlojuak/Azkoinak/Arandelak) beren aldaerekin eta
2 pakete, eta 3 adibidezko enpresa (Ferretería Ereño, Suministros
Mungia, Construcciones Busturia) erabiltzaileak jada sukurtsal
desberdinetan eta beren katalogoa jada esleituta dutela — `1111`
pasahitz nagusiarekin edozein bezala sar zaitezke eta benetako
eskaerak egin ezer eskuz alta eman gabe. `data/taller.db` lehendik
bazegoen (bolumen berrerabilia), ereite hau ez da errepikatzen ez du
ezer gainidazten.

**Telefonotik ikusteko** (ordenagailu honen Wi-Fi berean): erabili PC
honen IP lokala `localhost`ren ordez —
```bash
hostname -I   # 192.168.x.x-rekin hasten dena hartu
```
eta sartu `http://<ip_hori>:8000`n.

Itzaltzeko: `docker compose down` karpeta honetan bertan.

---

## B atala — Lab.Panda 2.4 (simulazioa)

### 0. Bi Raspberry Pi Picoak piztu (ezer baino lehen)

**Ez da beharrezkoa** — hardware fisiko aukerakoa dira, ikusi "Nola
dagoen eginda" gorago. Ez badituzu edo konektatzen ez badituzu,
gelaxkak berdin-berdin funtzionatzen du, benetako LEDrik, geldialdi
botoi fisikorik ez pantailarik gabe baino. Nola muntatuta dauden
(pinak, kableatua, erresistentziak, firmwarea) informazio guztia
[Documentacion/PI_PICO_montaje.html](Documentacion/PI_PICO_montaje.html)
dokumentuan dago, eta Loaderreko OLED pantailaren eskema espezifikoa
(uneko produktua zer erakusten duen)
[Documentacion/PI_PICO_cableado_oled.html](Documentacion/PI_PICO_cableado_oled.html)
dokumentuan.

### Zure Wi-Fia: Pico W-ren klabeak (irakurri Picoa ukitu baino lehen)

Sorterreko Pico W-ak zure Wi-Fian sartu behar du, eta horretarako bi
fitxategi daude `Rasberry_Pi_Pico/`n. **Repositorioan plantilak dira
bakarrik**, inoren klaberik gabe:

| Fitxategia | Zer jarri behar den |
|---|---|
| `wifi_config.py` | `SSID` (zure Wi-Fiaren izena), `PASSWORD` (bere klabea) eta `PC_IP` (**ordenagailu honen** IPa sarean; `hostname -I`rekin ateratzen da) |
| `webrepl_cfg.py` | `PASS`: edozein klabe Picora WebREPL bidez sartzeko |

1. Editatu bi fitxategiak zure datuekin eta kopiatu Picora (Thonny →
   *Gorde honela…* → gailua).
2. **Git-ek zure klabeak istripuz ez igotzeko**, esan ahaztu ditzala
   aldaketa horiek:
   ```bash
   git update-index --skip-worktree Rasberry_Pi_Pico/wifi_config.py Rasberry_Pi_Pico/webrepl_cfg.py
   ```
   Hortik aurrera bi fitxategi horiek ez dira aldatuta gisa ateratzen,
   zure klabeak izan arren. Egunen batean plantila *benetan* aldatu
   nahi baduzu: `--no-skip-worktree`, aldatu, commiteatu eta berriro
   markatu (aurretik zure klabeak aparte gordez).
3. **Ez igo inoiz benetako klaberik.** Commit batean sartzen bada,
   aldatu zure Wi-Fiaren pasahitza: gero commit hori ezabatzeak ez du
   balio norbaitek jada kopiatu badu.
4. Routerrak zure ordenagailuaren IPa aldatzen badu, eguneratu
   `PC_IP`: bestela, Picoaren geldialdi botoiak robota abisatzeari
   uzten dio.

Loaderreko Picoa USB bidez doa eta **ez du Wi-Firik behar**.

Robot bakoitzeko Pico bat dago, bakoitzak bere LEDarekin:

- **Sorter → beti bezalako Pico W** (`Rasberry_Pi_Pico/`, Wi-Fi
  bidez). Eman korrontea; `main.py` bakarrik abiarazten da eta
  Wi-Fira konektatzen da, `IP_DE_LA_PICO:5001`n entzuten geratuz.
  **Larrialdiko geldialdi botoi fisikoa** ere daramana da (ikusi
  beherago).
- **Loader → Wi-Firik gabeko Pico berria** (`Rasberry_Pi_Pico_USB_Loader/`).
  Konektatu USB bidez ordenagailu honetara (`docker-compose.yml`k jada
  badaki bere kabuz aurkitzen bere `/dev/serial/by-id/` bide
  egonkorretik, ez dago ezer ukitu beharrik beste Pico batekin
  ordezten ez baduzu).

### 1. Pantaila baimendu eta simulazioko 2 edukiontziak altxatu

```bash
xhost +local:docker
```
Beharrezkoa Webotsek (eta edukiontzi barruan abiarazitako edozein
leiho grafikok) zure pantailan marraztu ahal izateko.

```bash
cd "Lab.Panda 2.4/.devcontainer"
docker compose up -d --build
```
**Lehen aldiz benetan luzatzen da, eta trabatuta eman dezake
progresioaren % 70-80 inguruan** — hor deskargatzen da Webots-en
paketea bera (nahiko astuna da) Cyberbotics-en repotik; sarearen
arabera minutu batzuk irauten ditu hutsegite bat izan gabe. `-d`
etiketak edukiontziak jada eraikita daudenean eta abiarazten direnean
bakarrik eragiten du — irudia **eraikitzen** ari den bitartean,
terminalak progresioa erakusten jarraitzen du eta amaitu arte irekita
utzi behar da. Erdian ixten baduzu (X-arekin, edo Ctrl+C), eraikuntza
moztu egiten da eta errepikatu beharko duzu: ezer iraunkorrik ez du
hausten, baina berriro saiatu baino lehen egiaztatu ezer erdi geratu
ez dela `docker ps -a`rekin eta, proiektukoren bat badago,
`docker compose down` berriro abiarazi baino lehen.

`webots` edukiontziak `/dev/dri`z kexatzen abiaraztea huts egiten
badu (GPU/3D azelerazio gabe makina horretan, ohikoa azelerazioa
gaitu gabeko VM batean), komentatu `webots`en `devices:` ataleko
`- /dev/dri:/dev/dri` lerroa `docker-compose.yml` honetan — Webots
software bidezko errendatzera pasatzen da, motelagoa baina
funtzionatzen du. Loaderreko USB Picoak (`ros2_app`) jada EZ du arazo
hau: lehenespenez (Picorik konektatu gabe, edo inoiz izan ez duen
makina batean, VM batean bezala) edukiontzia berdin abiarazten da,
ezer ukitu beharrik gabe — ikusi `ros2_app`ren `devices:` atalaren
iruzkina fitxategian bertan, Pico hori benetan duen makina batean
gaitu nahi baduzu.

Honek `webots_panda_sim24` sortzen/abiarazten du (`worlds/panda_industrial_cell.wbt`
mundua zuzenean kargatzen du, bi robotetako gelaxka) eta
`ros2_panda_dev24`. Egiaztatu `docker ps`rekin.

### 2. Paketea konpilatu

**Beharrezkoa lehen aldiz** (klon berria, edo `ros2_ws/install/`
ezabatu baduzu): direktorio hori berregin daitezkeen artefaktuak dira
eta `.gitignore`n dago nahita, beraz `git clone` batek ez du ekartzen
— urrats hau gabe, 3. urratseko `ros2 launch`ek huts egiten du
paketea oraindik ez dagoelako. Hurrengo aldietan, Python kodea ukitu
baduzu bakarrik behar da.

```bash
docker exec -it ros2_panda_dev24 bash
cd /workspace
colcon build --packages-select panda_controller --symlink-install
```

### 3. Gelaxka osoa abiarazi (utzi terminal hau irekita)

```bash
docker exec -it ros2_panda_dev24 bash
cd /workspace
ros2 launch panda_controller robot_launch_industrial_cell.py
```
Honek gelaxkako 6 "kontrolagailuak" batera konektatzen ditu: Loader
brazoa, Sorter brazoa, bi goiko kamerak (bata Loaderren kutxaren
gainean, bestea Sorterren jasotze-puntuaren gainean),
`WarehouseSupervisor`a (gorputz fisikorik gabeko robot bat, 3 kuboen
benetako posizioa zaintzen duena: erortzen direnak salbatzen ditu eta
jada sailkatutakoak berriro beren kutxara birziklatzen ditu) eta
`SorterShuttleSupervisor`a (2026-09-10ean gehitua, aurrekoa bezala
gorputz fisikorik gabe: Sorterren jasotze-puntura iristen den kuboa
Xn zentratu eta biratzen duen "erretilua", deszentratuta ez lurreratzeko
— ikusi `Documentacion/carriles_completo.html`). **Itxaron
`Controller successfully connected` 6 aldiz ikusi arte** logean,
jarraitu baino lehen.

**~60 segundo igaro eta bat ere konektatu ez bada** (zuzenean ikusita
hainbat aldiz, batez ere makina/VM berri batean Webots hotzetik lehen
aldiz abiarazten ari denean): ez dago zertan zuzenean "zerbait
trabatzen bada" atalera joan behar, ezta dena 1. urratsetik
errepikatu ere. Azkarrena, eta `arrancar_todo.sh`k automatikoki egiten
duena:
```bash
docker restart webots_panda_sim24
```
Itxaron 20 segundo inguru Webotsek mundua berriro kargatu arte eta
errepikatu 3. urrats bera (`ros2 launch ...`) — bigarren aldiz ia beti
ondo konektatzen da. Ondoren ere konektatzen ez bada, begiratu
`docker exec ros2_panda_dev24 cat /tmp/robot_launch.log` (atzeko
planoan abiarazi baduzu) edo terminal honen errorea bera.

**Terminal hau irekita geratzen da lan egiten duzun bitartean.**
Ixten baduzu (edo komandoa bera gelditzen bada arrazoi batengatik),
urrats hau "eginda" izateari uzten dio 1. urratseko edukiontziak
martxan jarraitzen badute ere — eta beheragoko **ezer** (LEDak,
panela, ekoizpena) ez da funtzionatuko berriro abiarazi arte. Beste
terminal batean jada martxan dagoen egiaztatzeko berriro abiarazi
baino lehen:
```bash
docker exec ros2_panda_dev24 bash -c "ps -ef | grep robot_launch_industrial_cell | grep -v grep"
```
Ezer ez bada ateratzen, ez dago martxan — egin orain 4. edo 5.
urratsarekin jarraitu baino lehen.

### 4. LED zubiak (bat robot bakoitzeko, bakoitza bere terminalean)

**Ez da beharrezkoa Raspberry Pi Picoak ez badituzu** (ikusi 0.
urratsa, gorago): haiek gabe ez dago kolorea bidaltzeko ezer
errealik, beraz ez abiarazi — gelaxkak berdin-berdin funtzionatzen du,
LED fisikorik gabe baino. Ez da kontrol panelerako ere behar (5.
urratsa): bere **Raspberry Pi Pico** fitxak 3 LEDen kolorea simulatzen
du ROS topic berak entzunez, zubi hau (ez Picoa) benetan existitzearen
mende egon gabe.

**Errazago 2026-09-14tik:** kontrol panelean (5. urratsa),
**Konfigurazioa** fitxa → *Desblokeatu (klabea)* → markatu lerro
honek erabiltzen dituen Picoak → *Picoen konfigurazioa aplikatu*.
Panelak bere kabuz abiarazten ditu zubiak (eta panela abiarazten den
bakoitzean berriro abiarazten ditu), eta bi lerro badituzu, Pico
bakoitzak bat bakarrari men egiten diola ziurtatzen du. Azpiko eskuzko
komandoak balio dute panela erabiltzen ez baduzu.

> **Konfigurazioa fitxaren klabea alda daiteke** (2026-09-21): fitxan
> bertan, jada desblokeatuta, *Konfigurazio klabea aldatu* koadro bat
> dago **Hizkuntza**ren azpian. Klabe berria **bi aldiz** idazten
> duzu; bat datozenean eta gutxienez 4 karaktere badituzte bakarrik
> gordetzen da. Lerro bakoitzak berea du, zifratuta gordetzen da
> (inoiz ez testu arruntean) eta ez da galtzen berrabiaraztean.
> Ahazten bada, ezabatu lerro horren `config_maquina_*.json`
> fitxategiko (`ros2_ws/`n) `clave_config` sarrera eta fabrikako
> `1111` itzultzen da.
>
> **Botoiarekin berrezartzea** (2026-09-21): *Konfigurazioa* edo
> *Raspberry Pi Pico* fitxa irekita, mantendu sakatuta **10 s**
> Loaderreko USB Picoaren botoia (edo Pico fitxako botoi gorri
> simulatuetako bat; atzerako kontaketa erakusten dute). Panelak
> galdetu eta, berretsitakoan, `1111` itzultzen da eta OLEDak
> *Pasahitza berrezarrita* jartzen du segundo batzuetan. **Pico
> horretan `Rasberry_Pi_Pico_USB_Loader/main.py` berriro flasheatu**
> behar da Thonnyrekin (Gorde honela → gailua) eta
> **`led_publisher_usb` berriro abiarazi** balio izateko.

```bash
docker exec -it ros2_panda_dev24 bash
ros2 run panda_controller led_publisher       # Sorter, Picorekin Wi-Fi bidez hitz egiten du
```
```bash
docker exec -it ros2_panda_dev24 bash
ros2 run panda_controller led_publisher_usb   # Loader, Picorekin USB bidez hitz egiten du
```
Bakoitzak bere ROS topicetik iristen zaiona (`/comando_led` Sorterrentzat,
`/comando_led_loader` Loaderrentzat) benetako hardwarera bidaltzen du.
Hau gabe robota berdin-berdin mugitzen jarraitzen du, LED fisikoak
erreakzionatzen ez duen ezik.

### 5. Eskuzko kontrol panela (dena kudeatzen den lekua)

**3. urratsa benetan martxan behar du** (ikusi goiko koadroa) —
bestela 45s saiatzen jarraitzen du eta `ERROR [...] Inor ez da
harpidetu 45s ondoren` errorearekin huts egiten du eta leihoa ez da
inoiz irekitzen.

```bash
docker exec -it ros2_panda_dev24 bash
ros2 run panda_controller teleop_gui
```
Leiho bakar batean, hau dakar:
- **LOADER / SORTER** hautagailua eskuz zein brazo mugitzen ari zaren
  aukeratzeko, ezer berrabiarazi gabe.
- Gelaxka osoaren **STOP / BERRARMAKETA** (uneko mugimendua eten
  egiten du, EZ du bertan behera uzten; berrarmatzean bertan
  jarraitzen du utzitako lekuan) — brazoa eskuz mugitzen ari zaren
  zein ekoizpen automatikoa martxan dagoen, berdin funtzionatzen du.
- **Mugimendua** fitxa: aukeratutako brazoaren eskuzko joga.
- **Ekoizpena** fitxa: **"Lotea abiarazi"** botoia (eskuz aukeratutako
  produktu bakarraren kopuru bat fabrikatzen du) eta **"Zain dauden
  eskaera guztiak abiarazi"** botoia (Taller_Administracion-eko
  benetako eskaerei begiratzen die eta hiru koloreetatik falta dena
  batera fabrikatzen du — A atala martxan behar du).

Honekin bakarrik, jada beste terminalik ukitu gabe ekoiztu dezakezu.

### 6. Ekoizpen automatikoa eskuz (5. urratsaren botoien alternatiba)

Zuk zeuk terminal bidez abiarazi nahi baduzu bakarrik, 5. urratseko
botoiak erabili beharrean (adibidez, parametro zehatzekin uzteko):

```bash
docker exec -it ros2_panda_dev24 bash
# Sorter: uhalera iristen dena hartu eta sailkatzen du, kolorea berdin dio
ros2 run panda_controller sorter_demo --ros-args -r __ns:=/sorter \
  -p robot_base_x:=0.0 -p robot_base_y:=1.00 -p robot_base_z:=0.74
```
```bash
docker exec -it ros2_panda_dev24 bash
# Loader: hiru koloreak batera banatzen ditu, 6 buelta
ros2 run panda_controller loader_demo --ros-args -r __ns:=/loader \
  -p cycles:=6 -p led_topic:=/comando_led_loader -p led_topic_producto:=/comando_led_producto
# edo kolore bakarra (adib. 30 azkoin = berdea):
ros2 run panda_controller loader_demo --ros-args -r __ns:=/loader \
  -p cycles:=30 -p only_color:=G -p led_topic:=/comando_led_loader -p led_topic_producto:=/comando_led_producto
```
**Ez abiarazi jada panelaren bidez martxan baduzu** (5. urratsa) —
brazo berarengatik liskarrean sartuko lirateke.

### 7. Ekoizpen lerro bat baino gehiago (aukerakoa)

Goragokoak guztiak **lerro bat** muntatzen du (Webots bat + bere bi
robotak). Bigarren bat piztu daiteke, hirugarren bat... makina
berean paraleloan, bakoitza bere edukiontzietan, elkarrengandik
isolatuta (ez dute elkarri oinik jotzen ez robotik partekatzen) baina
**eskaeren web panel bera partekatuz** — ez dago han bereziki ezer
konfiguratu beharrik, banaketak jada badaki piztuta dauden lerroen
artean lana nola banatu.

Jada badago prest eta probatutako plantila bat
(`Lab.Panda 2.4/.devcontainer2`), beraz bigarren lerroa piztea, laburbilduz:

```bash
cd "Lab.Panda 2.4/.devcontainer2" && docker compose up -d --build
docker exec -d ros2_panda_dev24_linea2 bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && cd /workspace && ros2 launch panda_controller robot_launch_industrial_cell.py > /tmp/robot_launch.log 2>&1"
docker exec -it ros2_panda_dev24_linea2 bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && ros2 run panda_controller teleop_gui"
```

Eta irekitzen den panel berrian, **Konfigurazioa** fitxa (`1111`
klabea): jarri **Kate izena** bat bereizteko, eta beste lerro batek
erabiltzen ez duen **Makina Zk.** bat (horrela eskaeren banaketak ez
du lerroen artean gurutzatzen). Benetako Raspberry Pi Picoak benetan
konektatuta dituen lerroan bakarrik markatzen dira.

**Hirugarren lerro bat edo gehiago** nahi izanez gero, `.devcontainer2`
kopiatu eta hiru eremuak eskuz aldatu beharrean, dena tiroan egiten
duen script bat dago (plantila kopiatu, kutxak/sarea/`ROS_DOMAIN_ID`
berrizendatu, piztu, gelaxka abiarazi eta 6 kontrolagailuak konektatu
arte itxaron):

```bash
./crear_linea.sh 3
# edo jada Makina Zk., Taller_Administracion-en URLa (lerro hau BESTE
# ordenagailu batean bizi bada) eta Kate taldearekin:
./crear_linea.sh 3 3 http://IP_DEL_PRINCIPAL:8000 0
```

Lerroek ez dute zertan ordenagailu berean edo sistema berean egon: 2026-09-24an
lerro bat Windows-en eta bi Linux makina birtual batean aritu ziren aldi berean,
denak Windows-eko webgunearen kontra (ikusi
[INSTALAR_WINDOWS.eu.md](INSTALAR_WINDOWS.eu.md), *Kateak beste ordenagailu batzuetan*).

Urratsez urrateko gida osoa (zer egiten duen bakoitzak, gehienez zenbat
lerro sartzen diren, beste ordenagailu fisiko batean nola abiarazi
lerro bat)
[Documentacion/anadir_cadena_produccion.html](Documentacion/anadir_cadena_produccion.html)
dokumentuan.

---

## Zerbait trabatzen bada (kuboak pilatuta uhalean, bi robotak geldi)

_Arazo ezagun gehiago eta haien konponbideak: [PROBLEMAS_CONOCIDOS.eu.md](PROBLEMAS_CONOCIDOS.eu.md)._

Brazo bat kubo zail batekin hainbat saiakeraren ondoren amore ematen
badu gerta daiteke: 2026-08-31ra arte bere kamera betirako tapatuta
gera zitekeen (jada konponduta — bere kabuz aparkatzen da orain). Hala
ere zerbait korapilatzen bada, ezer garrantzitsurik galdu gabe
berrezartzeko modu garbia:

```bash
docker restart webots_panda_sim24   # 3 kuboak beti bezalako lekuan jartzen ditu
```
Itxaron 8 segundo inguru eta egin berriro **3, 4, 5** urratsak (eta 6a
terminal bidezko ekoizpena erabiltzen ari bazinen). Taller_Administracion-eko
eskaerak eta stocka EZ dira ukitzen honekin — simulazioa bakarrik
berrezartzen da.

---

## Dena itzali amaitzean

**Lasterbidea:** `./cerrar_todo.sh` (bi proiektuak gelditzen ditu eta
zerbaitek eusten badio abisatzen du). Honen baliokidea da:

```bash
cd "Lab.Panda 2.4/.devcontainer" && docker compose down
cd ../../Taller_Administracion && docker compose down
```

---

## Larrialdiko geldialdia — erreferentzia azkarra

- **Botoi fisikoak (bat robot bakoitzeko, 2026-09-01 saioa)**: biek
  gelaxka OSOA gelditzen dute (`/emergency_stop` orokorra da, ez
  robot bakoitzekoa).
  - **Sorter**: GPIO16 GNDra Pico Wn. LEDa unean bertan mozten du (ez
    dago sarearen mende) eta ROSi abisatzen dio 5002 portutik
    (wifi). **Zubi nodoa (`button_listener`) 3. urratsean sartuta
    dago** (2026-08-31tik, benetako konponketa: botoiak "ez zuen
    funtzionatzen" nodo hori urrats eskuzko aparte bat zelako,
    ahazteko erraza).
  - **Loader**: GPIO16 GNDra USB Picon. LEDa unean bertan mozten du
    Sorterrekoak bezala, baina wifirik ez duenez kable USB berari
    abisatzen dio (`BOTON_PARADA` inprimatzen du, `led_publisher_usb`k
    irakurtzen duena — 4. urratsa). Urrats hori martxan gabe, botoi
    honek ere ez dio ROSi abisatzen.

  Biek `/emergency_stop`en argitaratzen dute, `teleop_gui`,
  `loader_demo` eta `sorter_demo`k jada entzuten duten topic bera.
  Botoi fisiko batek mugimendua mozten ez badu, lehenengo egiaztatu
  behar dena 3. urratsa (`button_listener`, Sorter) edo 4. urratsa
  (`led_publisher_usb`, Loader) benetan martxan dagoela da — haiek
  gabe, ez dago zubirik ere.
- **HC-SR04 hurbiltasun sentsorea (Loader, 2026-09-11 saioa)**:
  geldialdia abiarazteko hirugarren modua, botoirik ukitu gabe —
  zerbait sentsoretik **10 cm** baino gutxiagora hurbiltzen bada,
  Loaderreko Picoak bere botoi fisikoaren bide bera zehazki
  abiarazten du (`BOTON_PARADA` USB bidez). Kableatua eta muga
  `Documentacion/cableado_hcsr04.html`n; muga
  `Rasberry_Pi_Pico_USB_Loader/main.py`ko `DISTANCIA_MIN_CM` da.
  Ekoizpen normalean bere kabuz abiarazten bada, brazoa sentsorearen
  aurretik pasatzen dela esan nahi du: jaitsi muga edo mugitu leku
  hori, ez kendu abisua.
- **Paneletik**: `teleop_gui`ren STOP/BERRARMAKETA botoiak (5.
  urratsa) gauza bera egiten du hardwarea ukitu gabe — eguneroko
  gomendatutako modua da.
- **OLED pantaila (Loader, 2026-09-18 saioa)**: fabrikatzen ari den
  produktua testuz erakusten du (izena, aldaera eta kodea), produktu
  LEDak kolorez esaten duen gauza bera baina paleta ikasi gabe
  irakurgarri. SSD1306 128×64 I2C bidez (`SDA=GP4`, `SCL=GP5`),
  `teleop_gui`k `/texto_producto`n argitaratzen du eta
  `led_publisher_usb`k Picora bidaltzen du kable USB berean. Pico
  fisikorik gabe, panelaren **Raspberry Pi Pico** fitxak pantaila
  bera simulatzen du topic hori entzunez. Eskema osoa
  `Documentacion/PI_PICO_cableado_oled.html`n — garrantzitsua:
  `machine.SoftI2C` behar du, hardware bidezko I2Cak `OSError EIO`
  ematen du idaztean muntaia honekin nahiz eta eskaneatzeak pantaila
  aurkitu.

**Ondo berrarmatzea (benetako tranpa, 2026-09-11):** `REARME` LED
topicera bidaltzeak (`/comando_led_loader` edo `/comando_led`) Pico
horren keinuari bakarrik uzten dio; **ez** du `/emergency_stop`
garbitzen, beraz bi robotak isilik geldi jarraitzen dute eta ematen
du berrarmaketak "ez duela funtzionatzen". Benetan berrarmatzen duena
`Bool(false)` da `/emergency_stop`en — panelaren BERRARMAKETA botoiak
hain zuzen egiten duena. Eskuz hiru argitalpenak behar dira:

```bash
ros2 topic pub --once /emergency_stop std_msgs/msg/Bool 'data: false'
ros2 topic pub --once /comando_led_loader std_msgs/msg/String "data: 'rearme'"
ros2 topic pub --once /comando_led std_msgs/msg/String "data: 'rearme'"
```

Geldialdian **panelaren eskuzko joga nahita funtzionatzen jarraitzen
du**: langileak brazoa mugitzen du (sentsoretik aldendu, kubo trabatu
bat askatu) eta berrarmatzean robotak utzitako lekuan hartzen du bere
lana berriro.
- **`estop_panel.py`**: STOP/BERRARMAKETArekin bakarrik leiho bat,
  `teleop_gui`k integratu baino lehenagokoa. Funtzionatzen jarraitzen
  du baina jada erredundantea da panel osoa erabiltzen baduzu; leiho
  txiki bereizi batean larrialdi botoi bat nahi baduzu bakarrik da
  erabilgarria.

LED protokoloa kable/wifi bidez: karaktere bat Pico bakoitzeko —
`R`/`G`/`B`/`0` (itzalita), gehi `PARADA`/`REARME` larrialdiko
keinurako. Bi Picoek protokolo bera ulertzen dute, bakoitza bere
kanalean (Wi-Fi 5001 portua / USB seriea).

---

## Dokumentazio tekniko gehigarria

Erreferentzia orrialde sakonagoak, xehetasun tekniko osoa edo erabaki
zehatz baten arrazoia nahi duenarentzat, ez nola abiarazi bakarrik:

- [Documentacion/panel_control_manual.html](Documentacion/panel_control_manual.html)
  — eskuzko kontrol panela (`teleop_gui`) fitxaz fitxa azalduta.
- [Documentacion/manual_tecnico.html](Documentacion/manual_tecnico.html)
  — Lab.Panda 2.4 + Taller_Administracion-en historia tekniko osoa.
- [Documentacion/manual_usuario_avanzado.html](Documentacion/manual_usuario_avanzado.html)
  — erabilera gida aurreratua, oinarrizkoa jada ezagutzen duenarentzat.
- [Documentacion/boton_led_flujo.html](Documentacion/boton_led_flujo.html)
  — geldialdi botoi fisikoaren froga solte bat, guztiz integratu baino
  lehen (historikoa).
- [Documentacion/motores_panda.html](Documentacion/motores_panda.html)
  — Panda brazoaren artikulazioak nola zenbakituta dauden eta
  bakoitzak zer egiten duen.
- [Documentacion/caras_cubo.html](Documentacion/caras_cubo.html) — uhaleko
  kuboetan zein aurpegi dagoen zeinen aurka (erreferentzia ikusmen
  bidezko heltzeko).

---

## Eranskina — demo eta mundu zaharrak (robot bakarreko proiektua, jada EZ dira erabiltzen)

Hau guztia bi robotetako gelaxka industrialaren aurrekoa da. Kodean
existitzen jarraitzen du (zerbait alderatu edo berreskuratu behar
bada), baina **ez da uneko fluxuaren zati** — ez abiarazi hasiera
normalaren zati dela pentsatuz:

- Munduak: `panda_un_cubo.wbt`, `panda_bolas.wbt`
- Launch: `robot_launch.py` (robot bakarra, namespace gabe)
- Demoak: `stack_tower_demo` (zinematika zaharreko robot bakarreko demoak 2026-09-29an kendu ziren; git-en historian daude)
- Uneko gelaxkaren garapen tresnak (ez dira hasiera normalaren zati
  ere, eraikitzeko erabili ziren): `panda_two_arms_smoke_test.wbt`,
  `panda_sorter_grasp_test.wbt`, `grasp_yaw_test`, `sorter_hover_test`,
  `robot_launch_two_arms.py`, `robot_launch_sorter_grasp_test.py`.
