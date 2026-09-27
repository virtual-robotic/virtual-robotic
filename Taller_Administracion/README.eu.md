# Gure eskaera webgunea

Lehen aldiz ikusten baduzu: hau da **tailerraren bulegoa**. Hemen eskatzen
dira piezak, zer fabrikatzen den apuntatzen da, soberakina biltegian gordetzen
da, bezeroari bere albaranarekin entregatzen zaio eta fakturatzen da.
Gelaxkako robotak (Loader eta Sorter) dira benetako **tailerra**; web honek
esaten die zer behar den eta apuntatzen du zer egiten ari diren. Ez duzu
informatikaz ezer jakin behar orrialde hau jarraitzeko: adibidezko eskaera
batekin kontatzen da, urratsez urrats.

> Web hau itzalita badago, gelaxkak berdin-berdin funtzionatzen jarraitzen du.
> Gertatzen den bakarra da inork ez duela ekoizpena apuntatzen eskaera
> batean.

## Eskaera baten bidaia, hasieratik amaierara

**🛒 Eskatzen da** → **🏭 Lortzen da** (biltegitik edo fabrikatuta) → **✅ Prest gelditzen da** → **🚚 Banatzen da** (albarana) → **🧾 Fakturatzen da**

Adibide bat: *Astilleros Murueta* enpresak 20 torloju, 10 azkoin eta pieza
askotariko pakete bat behar ditu, eta Bilboko sukurtsalak eskatzen ditu.

### 1. Saskiarekin eskatzen da 🛒

**Nork eskatzen duen.** **Bezero baten erabiltzaile** batek eskatzen du.
Bezero bakoitzak (adibidez, Astilleros Murueta) admin erabiltzaile bat du eta,
nahi izanez gero, bat **sukurtsal** bakoitzeko (Bilbo, Bartzelona,
Madril...). Piezak behar dituenak webgunea irekitzen du bere nabigatzailean
(beste fitxa batean edo beste ordenagailu batean, berdin dio), **Sartu**
sakatzen du eta bere erabiltzailea eta pasahitza sartzen ditu; adibidean,
Astilleros Muruetaren `mur-bilbao` erabiltzailea. Sartzean **Eskaerak** fitxa
bakarrik ikusten du, eta zerrendan bere enpresak eska ditzakeen piezak
bakarrik ateratzen zaizkio. Eskaera bakoitzean apuntatuta geratzen da **zein
bezerok eskatu duen eta zein erabiltzailek egin duen**; enpresaren
administratzaileak bere sukurtsal guztietakoak ikusten ditu, eta albarana eta
faktura **bezeroaren** izenean ateratzen dira, ez sukurtsalarenean.

Denda bat bezala da: produktu bat **edo pakete oso bat** aukeratzen duzu,
zenbat esaten duzu, eta saskira sartzen duzu. Saskia nahi duzun bezala
dagoenean, **Saskia eskatu** sakatzen duzu. Saski bateko guztia batera
bidaltzen da eta **albaran bakar batean** aterako da. Gauza bakar bateko
eskaera lerro bakarreko saski bat besterik ez da.

![Eskaerak pantaila: goian produktua edo paketea aukeratzen da, erdian hiru lerroko saskia dago eta azpian jada martxan dauden eskaerak, bakoitza bere egoerarekin](img/web_1_pedir_cesta.png)

Saskiaren azpian eskaera bakoitzak egoera aldatzen doa: *zain* (oraindik hasi
gabe), *prozesuan* (piezak lortzen ari dira), *banatzeko prest* (jada
guztiak daude, ateratzeko zain) eta *banatuta* (jada entregatu dira).

### 2. Lortzen da: biltegitik edo fabrikatuta 🏭

Sistemak lehenengo egiten duena **biltegia** begiratzea da. Jada piezak
gordeta badaude, unean bertan esleitzen zaizkio eskaerari eta ez da ezer
fabrikatu behar. Ez badago, falta dena **Tailerreko Eskaerak**en apuntatzen
da, robotentzako erosketa zerrenda dena: gelaxkak pieza horiek fabrikatzen
jarraitzen du eta, amaitu ahala, webgunea abisatzen du eta eskaerak bere
kabuz aurrera egiten du.

![Tailerreko Eskaerak fitxa fabrikatzeko falta denarekin: 6 azkoin eta 10 arandela](img/web_2_fabricar.png)

Hemen erabaki daiteke zein makinatan egiten den eskaera bakoitza, **urgente**
gisa markatu edo bertan behera utzi.

![Bi Panda robotak gelaxkan lanean: Loader ezkerrean kuboak uhalean uzten, Sorter goian koloreka sailkatzen](img/webots_cell.jpg)

Pieza horiek fabrikatzen dituen gure ekoizpen katea
[Gure ekoizpen katea](/manual/panda)n azaltzen da.

### 3. Prest gelditzen da eta banatzen da 🚚

Eskaerako pieza **guztiak** jada daudenean (saski batekoak badira, saskiko
guztiak), bigarren fasea iristen da: **Banaketa**. Bezeroari entregatzen
zaio eta **albaran** batekin apuntatzen da, entregatutakoaren egiaztagiria
dena. Bi etengailu ditu: bata stocka eskaerei bakarrik esleitzeko, eta
bestea jada prest dagoena bakarrik entregatzeko. Azken hori itzalita,
guztia hemen itxaroten du norbaitek **Banatu** sakatu arte.

![Banaketa fitxa: etengailuak, entregatzeko zain dauden piezak eta jada egindako albaranak](img/web_3_reparto.png)

**Pakete** bat beti osorik entregatzen da: pieza bakar bat falta bada,
paketea itxaroten du. Eta saski batek osatu arte itxaroten du, bezeroak
**albaran bakar bat** jaso dezan hiruren ordez.

### 4. Albarana 📄

Entrega lagundu duen orria da. Pakete bat **pakete bat** gisa ateratzen da
(bere prezioarekin) eta azpian, txiki, barruan daramana.

![Egindako albaranak: goikoak bi produktu eta bere hiru osagaiekin pakete bat darama](img/web_4_albaran_emitido.png)

Ikusi eta inprimatu (edo PDF gisa gorde) daiteke enpresaren logotipoarekin,
entregatzen duenaren eta jasotzen duenaren datuekin, eta BEZarekin
zenbatekoarekin.

![Albarana inprimatzen den bezala: logotipoa duen goiburua, bezeroa, prezioa duten lerroak eta guztira](img/web_5_albaran_papel.png)

### 5. Fakturatzen da 🧾

Hilaren amaieran (edo tokatzen denean), oraindik kobratu ez diren bezero
baten albaranak **faktura** batean biltzen dira. Guztia markatu daiteke,
bezero baten guztiak markatu, edo albaranez albaran aukeratu. Akatsen bat
badago, faktura ez da editatzen: beste **zuzenketa** batekin baliogabetzen
da eta albaranak berriro fakturatzeko libre geratzen dira, jada zuzenduta.
Hainbat enpresatatik fakturatu daiteke, bakoitza bere zenbaketarekin.

![Fakturazioa fitxa: bezero bakoitzaren fakturatzeko zain dauden albaranak, zein fakturatu aukeratzeko laukitxoekin](img/web_6_facturar.png)

## Nork zer egin dezakeen

| Nork sartzen den | Zer ikusten duen |
|---|---|
| **Erabiltzaile arrunta** (bezeroaren langile bat) | **Eskaerak** fitxa bakarrik: saskiarekin eskatzen du eta bereak nola doazen ikusten du |
| **Bezero enpresa baten administratzailea** | Aurrekoa bere enpresa osoarena, gehi bere albaranak eta fakturak |
| **Sistemaren administratzailea** (tailerra) | Dena: ekoizpena, kontabilitatea eta oinarrizko datuak (produktuak, bezeroak, prezioak...) |

## Jakin behar diren gauzak

- **Prezioak izoztu egiten dira eskatzean.** Bihar tarifa aldatzen bada,
  jada egindako eskaerek eskatu zireneko prezioa mantentzen dute. Bezero
  bakoitzak bere prezio propioak izan ditzake.
- **Ezer ez da isilean ezabatzen.** Prezio edo egoera aldaketa oro
  apuntatuta geratzen da: nork, noiz eta zenbatetik zenbatera.
- **Stocka ez da isilean banatzen.** *Banaketa automatiko* etengailu bat
  dago: piztuta, gordetako piezak bakarrik esleitzen zaizkie behar dituzten
  eskaerei; itzalita, geldi geratzen dira norbaitek **Stocka esleitu**
  sakatu arte.
- **Beldurrik gabe jolas dezakezu**: ikasteko proiektu bat da. Demoaren
  datuak asmatuak dira eta adibidezko erabiltzaileen pasahitza `1111` da.

### Adibideko erabiltzaileekin probatu

| Honela sartzen zara… | Pasahitza | Zu zara… |
|---|---|---|
| `admin` | `admin` | Tailerra: dena ikusten du, fabrikatzera bidaltzen du, banatzen eta fakturatzen du. Ez du eskaerarik egiten. |
| `ere-admin` | `1111` | Adibideko bezero bat: eskaerak egiten ditu eta bereak ikusten ditu. |

### Piezak eskuz sartu biltegian

**Biltegia** fitxan (tailerrak bakarrik), produktu bakoitzak **«Stockera
gehitu»** eta **«Stocketik kendu»** botoiak ditu, robotetatik datozen ez
diren piezetarako: kanpoan erositakoak, inbentarioa, itzulketak. Bakoitza
*Mugimenduak* atalean apuntatzen da «ajuste_manual» (eskuzko doikuntza)
gisa. Banaketa automatikoa piztuta badago, osorik osa ditzaketen eskaerei
ematen zaizkie berez; zati bat bakarrik estaltzen badute, robotei edo
**Banaketa** fitxako **«Stocka esleitu»** botoiari itxaroten diete.

---

**Barrutik nola dagoen egina jakin nahi duzu?** (bideak, datu-basea,
abiaraztea, panelaren fitxa bakoitza, proba automatikoak…):
[DETALLE_TECNICO.eu.md](DETALLE_TECNICO.eu.md) fitxategian dago.
