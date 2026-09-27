**Hizkuntza:** [Español](PROBLEMAS_CONOCIDOS.md) · [English](PROBLEMAS_CONOCIDOS.en.md) · Euskara

_Azken aldaketa: 2026-09-26_

# Arazo ezagunak

Benetan gertatu zaiguna bakarrik, bere konponbidearekin. Arazoak eta haien
konponbideak dituen **leku bakarra** da: gidek hona estekatzen dute.

Windows-en **instalatzeko** arazoak (birtualizazioa, WSL, Docker Desktop…)
bere gidan daude: [INSTALAR_WINDOWS.eu.md](INSTALAR_WINDOWS.eu.md),
«Benetan aurkitu ditugun arazoak» atalean.

## Robotekin gelaxka (Linux)

**Kontrolatzaileak ez dira konektatzen / Webots kargatzen geratzen da lehen
aldian.** Batzuetan gertatzen da hotzean. `arrancar_todo.sh` eta
`crear_linea.sh` berak saiatzen dira Webots-en `docker restart` batekin.
Eskuz: `docker restart webots_panda_sim24 ros2_panda_dev24` eta berriro
abiarazi.

**Berrabiaraztean, Webots-ek «Giving up» edo «Address already in use» dio.**
Aurreko aldiko kontrolatzaileak bizirik geratu ziren (`ros2 launch`-en
`pkill` batek ez ditu bere seme-alabak hiltzen). Konponbidea: bi edukiontzien
`docker restart` (Webots eta ROS 2) eta berriro abiarazi.

**Sorterraren pintzaren hatza hausten da.** Berrarmatzeak ez du balio:
Webots berrabiarazi behar da. Ordenagailu motel batean oso maiz gertatzen
zen; 2026-09-24tik robotek simulazioaren erlojuarekin neurtzen dituzte
beren itxaronaldiak eta jada ez (ikusi *Windows*, beherago).

**Prozesu errepikatuak daude ROS 2-ren edukiontziaren barruan** (hainbat
`button_listener`). Gelaxka berrabiaraztean gertatzen zen: scriptak
`ros2 launch` hiltzen zuen baina ez bere seme-alabak. 2026-09-24tik scriptek
edukiontzia berrabiarazten dute abiarazi aurretik.

**Makina birtual batean ez dago tokirik Docker-entzat.** Webots-en eta
ROS 2-ren irudiek 14 GB inguru hartzen dute. Makina birtualaren diskoak
gehiagorako ematen ez badu, errazena eta seguruena **Docker-entzat bakarrik
bigarren disko bat ematea** da, sistemakoa ukitu gabe:

1. Itzali makina birtuala.
2. VirtualBox-en, sortu disko berri bat (40 GB nahikoa da) eta konektatu
   makinari. VirtualBox-ek uzten ez badizu, *SATA* kontrolatzaileak ez du
   zulo librerik: konfigurazioan, igo bere atakak 2ra.
3. Piztu makina birtuala eta, barruan, jarri disko hori Docker-ek bere
   gauzak gordetzen dituen tokitzat (`/var/lib/docker` eta
   `/var/lib/containerd` karpetak).

Horrela egin genuen 2026-09-24an: 3. urratsa proiektuko
`vm_disco_docker.sh` scriptak egiten du, `sudo`-rekin abiarazita.

## Eskaeren webgunea

**Etengabe berrabiarazten da («WatchFiles detected changes … Reloading»).**
Programatzeko birkarga automatikoa da. 2026-09-24tik itzalita dator;
`Taller_Administracion/.env`-ko `TALLER_RELOAD=1`-ekin bakarrik pizten da.
Windows-en, ez piztu.

**Biltegian ez dira zirrindolak (edo beste produktu bat) agertzen.** Ez da
akatsa: fabrikatutako unitate bakoitza berehala esleitzen zaie zain dauden
eskaerei, beraz stocka 0an geratzen da eskaerak zain dauden bitartean.

## Windows

**Motel doa (Webots 0.15x–0.22x-an PC zahar batean).** Ez da ordenagailuak
gehiagorako ematen ez duela: Webots-ek segundoko askotan itxaroten die
robotei erantzun diezaioten, Docker barruan baitaude, eta Windows-en mezu
horiek motel doaz. Gehien pisatzen zutenak goitik begiratzen duten bi
kameren argazkiak ziren, etengabe bidaltzen zirenak. **2026-09-25ean
hobetua** (segundoko 10 argazki): Windows 11 duen eramangarri batean kate bat
errealitatearen abiadura berera pasatu zen (1x), eta **4 kate aldi berean**
bakoitza 0.35x–0.5x-an doa (lehen 0.18x). Segundoko argazkiak nola aldatu:
ikusi [INSTALAR_WINDOWS.eu.md](INSTALAR_WINDOWS.eu.md).

**Loaderra eskumuturra etengabe mugitzen geratzen da lote bat hastean, eta
panelak loteak martxan jarraitzen duela dio.** 2026-09-26an konpondua. Lote
bakoitzaren hasieran robotak eskumuturra 5 segundoz mugitzen du abisatzeko,
eta denbora hori gaizki neurtzen zuen lotea oso azkar hasten bazen (gehiago
gertatzen zen hainbat katerekin). Bertsio zaharrago batekin: abiarazi berriro
kate hori. Lote bat erdibidean moztu ondoren, panelak **2 minutu** behar ditu
beste bat abiarazten uzteko.

**Lehen aldian Webots «Downloading assets 72 %»-n geratzen da.** Eszenaren
marrazkiak internetetik jaisten zintzilik geratu da. Itxi (erantzuten ez
badu, `cerrar_windows.bat`-ek ixten du) eta abiarazi berriro: jaitsitakoa
gorde egiten da, eta bigarren aldian kargatzen du.

**`git pull`-ek huts egiten du `.wbproj` batengatik.** Webots-ek fitxategi
horiek berridazten ditu; 2026-09-24tik git-ek ez ditu jarraitzen. Klon
zahar batekin gertatzen bada:
`git checkout -- "Lab.Panda 2.4/worlds/.panda_industrial_cell.wbproj"` eta
berriro `git pull`.

**`git pull`-ek erabiltzailea eskatzen du eta autentifikazioak huts egiten
du.** Ezabatu gordetako gakoa `cmdkey /delete:git:http://GITEA_IPa:3000`
-rekin eta saiatu berriro.

Instalazioko arazoak (birtualizazioa, bere laguntza bakarrik erakusten duen
WSL, «Errore katastrofikoa», `500 … _ping`, VirtualBox)
[INSTALAR_WINDOWS.eu.md](INSTALAR_WINDOWS.eu.md) fitxategian daude.
