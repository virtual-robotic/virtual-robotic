**Hizkuntza:** [Español](INSTALAR_WINDOWS.md) · [English](INSTALAR_WINDOWS.en.md) · Euskara

_Azken aldaketa: 2026-09-26_

# Windows-en instalatu

> **Benetan probatua 2026-09-23an** Windows 10 22H2 (Intel) duen PC fisiko batean: instalazio garbia biltegi publikotik, `docker compose up -d --build` eta webgunea `http://localhost:8000`-n martxan, abiaraztean errorerik gabe.

Gida honek **eskaeren webgunea** (`Taller_Administracion`) hartzen du,
probatua eta martxan, eta bukaeran **robotekin gelaxka**, **2026-09-24tik
Windows-en badabilena**: ikusi
[Robotekin gelaxka Windows-en](#robotekin-gelaxka-windows-en).
Linux-en betiko moduan abiarazten da (ikusi [LANZAR_PROYECTO.eu.md](LANZAR_PROYECTO.eu.md)).

> **Windows-en ez da inoiz `arrancar_todo.sh` abiarazten**, Linuxerakoa da.
> Webgunea bakarrik nahi baduzu, `docker compose` nahikoa da; dena nahi
> baduzu, `arrancar_windows.bat`.

Proiektuko fitxategi eta karpeten izenak gaztelaniaz daude; gida honek
dauden bezala uzten ditu.

## Hasi aurretik: zure Windows-ek balio du?

Docker Desktop-ek **WSL 2** behar du, eta horrek **Hyper-V**, eta horrek
prozesadoreak **birtualizazioa gaituta** izatea. Hortik ateratzen dira
denbora galdu aurretik begiratu beharreko bi kasuak:

| Non dabil zure Windows | Badabil? |
|---|---|
| PC fisikoa | **Bai**, behar izanez gero BIOSean birtualizazioa gaituz |
| VirtualBox-eko makina birtuala | **Ez**, eta ez du konponbiderik (ikusi beherago) |

### Birtualizazioa egiaztatu

**Ctrl+Shift+Esc** (Ataza-kudeatzailea) → **Errendimendua** fitxa → **PUZ**.
Bilatu **Birtualizazioa**: **Gaituta** jarri behar du.

*Desgaituta* jartzen badu, BIOSean gaitzen da:

1. Berrabiarazi eta sartu BIOSean piztu bezain laster **F2** edo **Supr**
   behin eta berriz sakatuz (ordenagailuaren arabera **F1**, **F10** edo
   **Esc** izan daiteke; abioko pantailak esan ohi du).
2. Bilatu aukera eta jarri **Enabled**:
   - **Intel:** `Intel Virtualization Technology` edo `VT-x`.
   - **AMD:** `SVM Mode` edo `AMD-V`.

   **Advanced → CPU Configuration**-en egon ohi da; eramangarrietan
   batzuetan **Security** edo **Configuration**-en.
3. Gorde eta irten (normalean **F10**).

## `wsl`-ek laguntza-pantaila bakarrik erakusten badizu

Instalatu berri den Windows 10 batean gertatzen da: `wsl --install`,
`wsl --update` eta baita `wsl -l -v` ere aukeren zerrendarekin erantzuten
dute ezer egin beharrean. **Ez da sintaxi-errore bat**: WSL-rako Windows-en
funtzioak gaituta ez daudela esan nahi du. Eskuz gaitzen dira, PowerShell-en
**administratzaile gisa**:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Bakoitzak *Eragiketa behar bezala osatu da* esanez bukatu behar du. Gero
**berrabiarazi** Windows eta jaitsi kernela `wsl --update --web-download`
-rekin (ikusi beherago). Beste berrabiarazte bat, eta Docker Desktop ireki
daiteke.

## Instalazioa

1. **Docker Desktop Windows-erako**, [docker.com](https://www.docker.com/products/docker-desktop/)
   -etik, *Use WSL 2* aukera markatuta utzita. Berrabiarazi PCa eskatzen
   duenean.
2. Ireki Docker Desktop. Saioa hasteko eskatzen badizu, **ez da konturik
   behar**: bilatu *Skip* edo *Continue without signing in* esteka txikia.
   Itxaron behean ezkerrean **Engine running** jarri arte.
3. **Git for Windows**, [git-scm.com](https://git-scm.com/download/win)
   -etik (denari «Hurrengoa» ematea nahikoa da).
4. **Webots** (robotak ere nahi badituzu bakarrik; webgunea bakarrik
   nahi baduzu ez da behar):
   - Jaitsi instalatzailea zuzenean hemendik:
     [webots-R2025a_setup.exe](https://github.com/cyberbotics/webots/releases/download/R2025a/webots-R2025a_setup.exe)
     (250 MB inguru). **Zehazki R2025a bertsioa** izan behar du,
     proiektuak erabiltzen duen bera; ez hartu berriagorik.
   - Ireki. Norentzat instalatu galdetzen duenean, aukeratu **niretzat
     bakarrik** (*Install for me only*): horrela ez du administratzaile
     baimenik eskatzen.
   - Utzi gainerako aukerak datozen bezala eta amaitu instalazioa.
   - Ez dago Windows-erako bertsio eramangarririk (instalatu gabekorik).
5. **Jaitsi proiektua.** PowerShell-en, nahi duzun karpetan (adibidez
   `C:\carga`):

   ```powershell
   git clone https://github.com/virtual-robotic/virtual-robotic.git
   ```

6. **Abiarazi**, bi modu hauetako batean:
   - **Eskaeren webgunea soilik:**

     ```powershell
     cd virtual-robotic\Taller_Administracion
     docker compose up -d --build
     ```

     Lehen aldian denbora pixka bat behar du, irudia eraikitzen baitu.
     Gelditzeko: `docker compose down` karpeta berean.
   - **Dena, robotekin:** **`arrancar_windows.bat`**-ekin (ikusi nola
     abiarazi hemen behean, eta zer egiten duen
     [Robotekin gelaxka Windows-en](#robotekin-gelaxka-windows-en) atalean).
     Dena gelditzeko: **`cerrar_windows.bat`** (Webots ere ixten du).

   **`.bat` fitxategi bat nola abiarazi**, bi moduetako edozein:
   - **Saguarekin:** ireki proiektuaren karpeta (`virtual-robotic`)
     Fitxategi-arakatzailean eta egin **klik bikoitza**
     `arrancar_windows.bat`-en. Leiho beltz bat irekitzen da zer egiten
     duen kontatuz; **ez itxi** bukaeran *«Sakatu tekla bat jarraitzeko»*
     jarri arte.
   - **PowerShell-etik**, proiektuaren karpetaren barruan:

     ```powershell
     .\arrancar_windows.bat
     ```

   Berdin itzaltzeko, `cerrar_windows.bat`-ekin. Windows-ek fitxategia
   arriskutsua izan daitekeela abisatzen badu, internetetik datorrelako da:
   sakatu *Informazio gehiago* → *Exekutatu hala ere*.
7. Ireki webgunea `http://localhost:8000`-n eta sartu **admin** / **admin**
   -ekin. Robotak ere abiarazi badituzu, **kontrol-panela** berez irekitzen
   da nabigatzailean (`http://localhost:6080/vnc.html`) eta Webots bere
   leihoan.

   `admin`-ekin **ezin da eskaerarik egin**: `admin` tailerra da (banatzen
   eta fakturatzen du). Eskatzeko, sartu bezero gisa, adibidez
   **`ere-admin`** **`1111`** pasahitzarekin. Xehetasun gehiago README-n,
   «Nork zer egiten du webgunean».

Abiarazi komandoak **zure PowerShell leihotik**, ez SSH bidez ez zerbitzu
batetik: Docker-ek bere kredentzialak Windows-eko Kredentzial-kudeatzailean
gordetzen ditu eta, zure saiotik kanpo, *«Zehaztutako saio-hasierako saioa ez
dago»* esanez huts egiten du.

## Benetan aurkitu ditugun arazoak

Hemen **instalatzekoak** bakarrik. Dena martxan dagoenean gertatzen direnak
(konektatzen ez diren robotak, motel doa, `git pull`-ek huts egiten du…)
[PROBLEMAS_CONOCIDOS.eu.md](PROBLEMAS_CONOCIDOS.eu.md) fitxategian daude.

### «Virtualization support not detected»

Docker Desktop-ek ez du birtualizazioa aurkitzen. Bi arrazoi posible:

- **PC fisiko batean:** BIOSean desgaituta dago. Ikusi *Birtualizazioa
  egiaztatu*, goian.
- **VirtualBox barruan:** ez du konponbiderik. Ikusi hurrengo atala.

### VirtualBox barruko Windows: ezin da, eta ez da zure errua

**Docker Desktop-ek ezin du funtzionatu VirtualBox-en instalatutako Windows
batekin.** WSL 2-k Hyper-V behar du, eta **VirtualBox-ek ez du Hyper-V
hipervisore habiaratu gisa onartzen**
([Oracleren dokumentazioa](https://docs.oracle.com/en/virtualization/virtualbox/6.0/admin/nested-virt.html)).

2026-09-23an sakon probatu genuen amore eman aurretik: ez birtualizazio
habiaratua gaituz (`VBoxManage modifyvm "<VM>" --nested-hw-virt on`), ez
8 GB RAM eta 6 prozesadorera igoz, ez paravirtualizazio-hornitzailea kenduz.
Arrazoi teknikoa VMaren beraren erregistroan dago (`Logs/VBox.log`):
`Gst: 8000000a/...` lerroan, VirtualBox-ek gonbidatuari eskaintzen dizkion
birtualizazio-funtzioen CPUIDa, EDXren balioa `0x000000c8` da — **0 bita
(orri-taula habiaratuak, NPT) zeroan dago**, eta Windows-en hipervisoreak
funtzio hori eskatzen du abiarazteko.

Kontuz nahasten duen xehetasun batekin: VM horren barruan, Windows-ek
`HypervisorPresent = True` eta `VirtualizationFirmwareEnabled = True`
erantzuten du. «True» hori **engainagarria** da — VirtualBox-ek berak
iragartzen duen paravirtualizazio-interfazeari dagokio, ez Windows-en
hipervisoreari.

**Ez dago ordenagailua AMD edo Intel izatearen menpe.** Muga VirtualBox-ena
da, ez prozesadorearena: AMD batean probatu genuen, eta Intel batean gauza
bera gertatuko litzateke (han funtzio horri EPT deitzen zaio NPT beharrean,
baina VirtualBox-ek ez dio Windows-i hura erabiltzen uzten).

Windows-en probatzeko **benetako Windows PC bat** behar da.

**Alternatiba bat, oraindik probatu gabea:** Linux ordenagailu batean,
**KVM** (*virt-manager* programa) erabili VirtualBox-en ordez Windows-eko
makina birtualerako. KVM-k bai pasatzen dio funtzio hori Windows-i, beraz
Docker Desktop barruan abiarazi beharko litzateke. Hala ere, makina birtual
baten 3D atala ahula da oraindik Webots-entzat.

### `wsl --install` «Errore katastrofikoa»-rekin bukatzen da

WSL instalatzean edo eguneratzean gertatzen da, normalean deskarga Microsoft
Store-tik doalako. Berrabiarazi Windows eta erabili hura saihesten duen bidea
(osagaia GitHub-etik jaisten du):

```powershell
wsl --update --web-download
```

Ondoren, `wsl --status`-ek ez du kernela falta dela kexatu behar.

### `500 Internal Server Error ... dockerDesktopLinuxEngine/_ping`

**Docker-en motorra martxan ez dagoela** esan nahi du soilik; proiektuak ez
du zerikusirik. Ireki Docker Desktop, itxaron *Engine running* arte eta
errepikatu komandoa.

### Webgunea etengabe berrabiarazten da eta ez du erantzuten

Erregistroan (`docker logs taller_admin_api`) behin eta berriz
*«WatchFiles detected changes … Reloading…»* ikusten baduzu, kodearen
**birkarga automatikoa** da, programatzen ari denarentzat bakarrik pentsatua.
Windows-en muntatutako fitxategien denbora-markak dantzan ibiltzen dira eta
birkarga begizta batean sartzen da. 2026-09-24tik **itzalita dator
lehenetsita**; `Taller_Administracion/.env`-en `TALLER_RELOAD=1` jartzen
baduzu bakarrik pizten da. Windows-en, ez piztu.

## Robotekin gelaxka Windows-en

> **2026-09-24an probatua** Windows 10 duen PC berean: Webots R2025a
> Windows-en instalatuta, 6 kontrolatzaileak Docker-etik konektatuta, eta
> kontrol-panela nabigatzailean robotak mugitzen. Lehen proba da: denbora
> luzez erabiltzea falta da.

**Nola muntatzen den.** Webots **Windows-en bertan instalatuta** doa
(Docker-ekoak Linux pantaila bat behar du, Windows-ek ez duena, eta
*«could not connect to display»*-rekin hiltzen da). Docker-en **ROS 2**
bakarrik doa, eta sarearen bidez iristen da Webots horretara.
**Kontrol-panela** **nabigatzaileko fitxa batean** agertzen da, hura ere
Linux leiho bat delako.

**Zer instalatu behar da:** webgunerako gauza bera, gehi **Webots**
([Instalazioa](#instalazioa)ren 4. urratsa).

**Abiarazi:** klik bikoitza **`arrancar_windows.bat`**-en, proiektuaren
karpeta nagusian. Ordenan, hau egiten du:

1. Docker Desktop martxan dagoela egiaztatzen du.
2. Eskaeren webgunea abiarazten du.
3. ROS 2-ren edukiontzia abiarazten du
   (`Lab.Panda 2.4/.devcontainer/docker-compose.windows.yml`-ekin) eta
   konpilatzen du. Lehen aldian denbora dezente behar du: hainbat GBko
   irudi bat jaisten du.
4. Webots irekitzen du gelaxkaren munduarekin eta konexioak onartu arte
   itxaroten du. Lehen aldian Webots-ek testurak jaisten ditu; **Windows-eko
   suebakiak** galdetzen badu, **baimendu** sare pribatuetan.
5. Gelaxka abiarazten du eta 6 kontrolatzaileei itxaroten die.
6. Panela nabigatzailean irekitzen du: `http://localhost:6080/vnc.html`.

**Itzali:** `cerrar_windows.bat`. 2026-09-26tik Webots-en leihoa ere ixten
du. Ez da ezer gorde behar: berriro abiaraztean, gelaxka zerotik hasten da
betiko moduan.

**Lehen aldian Webots robotik gabe agertzen bada** (eta itxura arraroarekin,
testurarik gabe): modeloak internetetik jaisten ari da eta mundua haiek izan
aurretik ireki zen. Itxi Webots eta abiarazi berriro `arrancar_windows.bat`;
bigarren aldian badauzka (2026-09-24an gertatu zitzaigun). Ez erabili
*Reload World*: guri Webots itxi zigun.

**Oraindik begiratzeko dagoena:**

1. **PC zahar batean motel doa.** 2012ko eramangarri batean simulazioa
   **0.15x–0.22x**-an doa, hau da, errealitatea baino 5 eta 7 aldiz
   motelago. Zenbaki hori Webots-en goiko barran ikusten da, erlojuaren
   ondoan.

   Ez da ordenagailuak gehiagorako ematen ez duela: Webots-ek ia ez du
   lanik egiten. Moteltzen dutenak Webots-en eta roboten arteko mezuak dira,
   Docker barruan baitaude, eta batez ere **bi kameren irudiak**,
   simulazioaren urrats bakoitzean bidaltzen zirenak (31 segundoko).
   **2026-09-25ean hobetua**: orain 10 bidaltzen dituzte segundoko, robotek
   kuboak ikusteko nahikoa baino gehiago. Windows 11 duen eramangarri moderno
   batean ekoizpena ia bikoiztu zen (43–49 segundoan kubo batetik 24an
   batera) eta simulazioa errealitatearen abiadura berean doa (1.0x).

   *Aldatu nahi baduzu:* goiko kameren bi fitxategiak dira,
   `overhead_camera.urdf` (Loaderrarena) eta `overhead_camera_sorter.urdf`
   (Sorterrarena), `Lab.Panda 2.4/ros2_ws/src/panda_controller/resource/`
   karpetan. Zenbakia `<updateRate>10</updateRate>` lerroan dago: segundoko
   argazkiak dira. Argazki gutxiago, azkarrago doa dena, baina robotek
   atzerapen handiagoarekin ikusten dute. Linux-en ere berdin balio du.

   Lehen, abiadura horretan, **Sorterrari pintzaren hatza hausten zitzaion**
   oso maiz. **Konponduta dago** (2026-09-24): orain robotek Webots-en
   erlojuarekin kontatzen dute denbora eta ez ordenagailuarenarekin, beraz
   dena motel joan arren ondo mugitzen dira. Hala ere hausten bada,
   berrarmatzea ez da nahikoa: itxi Webots eta abiarazi berriro
   `arrancar_windows.bat`.

   **2026-09-26an konpondua: Loaderra amaierarik gabe «dantzan»** geratzen
   zen lote bat hastean, eta panelak loteak martxan jarraitzen zuela
   esaten zuen. Lote bakoitzaren hasieran robotak eskumuturra 5 segundoz
   mugitzen du abisatzeko; denbora hori gaizki neurtzen zuen lotea oso
   azkar hasten bazen, eta dantza ez zen inoiz bukatzen. Hainbat katerekin
   gehiago gertatzen zen. Bertsio zaharrago batekin gertatzen bazaizu,
   abiarazi berriro kate hori (`arrancar_windows.bat`, edo
   `crear_linea_windows.bat` bere zenbakiarekin). Kontuz: lote bat
   erdibidean moztu ondoren, panelak **2 minutu** behar ditu beste bat
   abiarazten uzteko (pieza bat bidean dagoen badaezpada itxaroten du).
2. Nabigatzaileko panelean, leiho txiki batean idazteko (adib.
   *Konfigurazioa*ko gakoa), **egin klik laukiaren barruan** idatzi aurretik.
3. USB bidezko Raspberry Pi Pico: Windows-en ez da edukiontzira iristen,
   beraz Loaderraren LEDak ez du funtzionatuko (gainerakoak bai; Pico
   aukerakoa da).

**Zergatik ez den kodea ukitu behar.** Gure munduan **kontrolatzaile guztiak
`<extern>` dira**: Webots-ek ez ditu exekutatzen, kanpotik konektatzen dira,
TCP bidez 1234 atakara. `WEBOTS_SHARED_FOLDER` aldagaiak ez du karpetarik
partekatzen: ROS 2-ren konektoreak TCP erabil dezan egiten du soilik,
`host.docker.internal`-erantz, Windows-en Docker Desktop-ek Windows bera
seinalatzen duena. (Bide batez konektoreak WSL-rekin duen akats ezagun batetik
libratzen gaitu: kodearen beste adarrean dago, erabiltzen ez duguna.)

### Hainbat kate Windows berean

**2026-09-25ean probatua 4 kate aldi berean** Windows 11 duen eramangarri
batean. Kate bakoitzak bere Webots, bere ROS 2 edukiontzia eta bere panela
ditu:

| Katea | Webots atakan | Panela nabigatzailean |
|---|---|---|
| 1 | 1234 | `http://localhost:6080/vnc.html` |
| 2 | 1235 | `http://localhost:6081/vnc.html` |
| N (9 arte) | 1233+N | `http://localhost:` 6079+N |

- **Lehenik 1. katea**, `arrancar_windows.bat`-ekin betiko moduan.
- **Beste bat gehitzeko:** klik bikoitza **`crear_linea_windows.bat`**-en.
  Katearen zenbakia (2tik 9ra) eta bere makina-zenbakia galdetzen dizkizu
  (beste kate batekin errepikatu behar ez dena). Bere Webots eta bere panela
  irekitzen ditu.
- **Bat bakarrik itzaltzeko:** `cerrar_windows.bat 3` (PowerShell-etik,
  proiektuaren karpetan): kate hori gelditzen du eta bere Webots ixten du;
  besteek jarraitzen dute. Zenbakirik gabe, `cerrar_windows.bat`-ek kate
  guztiak, beren Webots-ak eta webgunea itzaltzen ditu.
- **Galderarik gabe:** `arrancar_windows.bat 3 30`-ek `crear_linea_windows.bat`
  -en gauza bera egiten du 3. katerako 30 makina-zenbakiarekin. Zenbakia utz
  daiteke eta gero panelaren *Konfigurazioa* fitxan jarri. Zenbakirik gabe,
  `arrancar_windows.bat`-ek 1. katea abiarazten du.
- Denak **eskaeren webgune berarentzat** aritzen dira.

**Ordenagailuak zenbat eusten dion.** 2026-09-26an probatua eramangarri
horretan (Windows 11, 30 GB memoria), 4 kateak aldi berean fabrikatzen:

| | Lehen (kamerak 31 argazki/s) | Orain (kamerak 10 argazki/s) |
|---|---|---|
| Kate bakoitzaren abiadura (1x = errealitatea bezala) | 0.18x | 0.35x eta 0.5x artean |
| Kate bakoitzak kubo bat ateratzen du… | — | ~57 segundoan behin |
| Prozesadorearen / txartel grafikoaren karga | % 60 / % 55 | % 77 / % 73 |

4 katerekin eramangarria nahiko kargatuta dabil: **4 muga ona da**. Bosgarren
batek denak moteltuko lituzke.

**Irekitzean, Webots-ek 3D ikuspegia bakarrik erakusten du** (edizio-panelik
gabe), hainbat leiho sar daitezen. Panelen bat ikusi nahi baduzu, *View*
menuan dago.

### Kateak beste ordenagailu batzuetan, Windows-eko webgunearentzat lanean

Kate gehiago izateko beste modu bat, **2026-09-24an probatua**: webgunea eta
kate bat Windows PCan, eta **beste bi kate Linux duen beste ordenagailu
batean** (Linux Mint makina birtual bat), hirurak **eskaeren webgune
berarentzat** lanean. Linux ordenagailuan, kate bakoitza Windows-eko
webgunea seinalatuz sortzen da:

```bash
./crear_linea.sh 3 33 http://WINDOWS_IPa:8000
./crear_linea.sh 4 34 http://WINDOWS_IPa:8000
```

- Kate bakoitzak bere **makina-zenbakia** behar du (hemen 10 Windows-ekoak,
  33 eta 34 Linuxekoek), eskaerak nahas ez daitezen.
- Windows-eko suebakiak 8000 ataka sartzen utzi behar du; Linux
  ordenagailutik `http://WINDOWS_IPa:8000` irekiz egiaztatzen da.
- 4 prozesadore eta 6 GB RAM dituen makina birtual batek bi kate mugitzen
  ditu, baina mugan. Irudiek 14 GB disko inguru behar dituzte: sartzen ez
  badira, ikusi [PROBLEMAS_CONOCIDOS.eu.md](PROBLEMAS_CONOCIDOS.eu.md)
  (Docker-entzat bigarren disko bat gehitu).
