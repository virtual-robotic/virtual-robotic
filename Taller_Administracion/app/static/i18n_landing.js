// Traducciones de la landing (ES es el texto de la propia pagina; aqui EN y EU). Generado el 2026-09-21.
// Cada elemento marcado con data-i18n="clave" (o data-i18n-alt / -title / -aria-label) se cambia al elegir idioma.
// El euskera esta escrito a mano y agradece revision de un hablante nativo.
// Para anadir un texto: ponle data-i18n="una-clave" en el HTML y una entrada con esa clave en 'en' y en 'eu'
// (las claves actuales son un resumen del texto en castellano; da igual cual uses, solo tiene que coincidir).
// Las dos copias (Taller_Administracion/app/static y Virtual_Robotic) deben ser iguales.
window.VR_I18N = {
 "en": {
  "t22a830": "2 — Sign in to the panel",
  "t225062": "If you are seeing this page it is because the orders panel is already running — press \"Sign in\" above with <strong>admin</strong> / <strong>admin</strong> and you go straight into the system. If you want to set it up yourself from scratch on your own computer:",
  "t60d2bc": "<strong>The cell with the robots</strong> (Webots + ROS&nbsp;2): in addition a graphical desktop with X11 and the <code>xhost</code> command, about <strong>15&nbsp;GB of free disk</strong>, <strong>8&nbsp;GB of RAM</strong> or more and internet the first time (it downloads Webots and its textures). With a graphics card it runs smoothly; without one you have to comment out a line in <code>docker-compose.yml</code> and it is slower.",
  "t906fa5": "<strong>Only the orders website:</strong> <strong>Docker Desktop</strong> (with WSL&nbsp;2 enabled) and <strong>Git for Windows</strong>. Then <code>docker compose up -d --build</code> and open <code>http://localhost:8000</code>. It is a normal Python image, but <strong>we have not tested it on Windows</strong>.",
  "tfa5e9f": "Internal access",
  "tcb4bc0": "<strong>Git:</strong> install <em>Git for Windows</em> from git-scm.com (just click \"Next\" all the way).",
  "td8741c": "Check that it works:",
  "taea234": "Windows",
  "t441220": "Enter production",
  "ta127c8": "For the cell with the robots follow <a href=\"/manual/lanzar\">LANZAR_PROYECTO.md</a>. The first time it takes quite a while because Webots gets downloaded.",
  "tb687c6": "Sign in",
  "tb72d12": "Optional, not critical",
  "t5988a9": "<strong>For the robots:</strong> install <em>VirtualBox</em>, create a virtual machine with <em>Linux Mint</em> (4 processors, 8&nbsp;GB of RAM and 40&nbsp;GB of disk work well) and follow the Linux steps inside it. A virtual machine normally has no 3D acceleration: comment out the <code>/dev/dri</code> line as explained in <a href=\"../LANZAR_PROYECTO.md\">LANZAR_PROYECTO.md</a>.",
  "tede40a": "With Docker installed, this runs on your own computer in a couple of commands. You do not need the Raspberry Pi Picos or any of the other physical hardware for it to work.",
  "td3888c": "For the cell with the robots follow <a href=\"../LANZAR_PROYECTO.md\">LANZAR_PROYECTO.md</a>. The first time it takes quite a while because Webots gets downloaded.",
  "t03d264": "<strong>Docker Desktop:</strong> download the <em>Docker Desktop for Windows</em> installer from docker.com and leave the <em>Use WSL 2</em> option ticked. Restart the PC, open Docker Desktop and wait for it to say <em>Engine running</em>. If it tells you WSL is missing, open PowerShell <strong>as administrator</strong>, type <code>wsl --install</code> and restart.",
  "t1edcfb": "Orders panel",
  "t0b6986": "<strong>For the robots:</strong> install <em>VirtualBox</em>, create a virtual machine with <em>Linux Mint</em> (4 processors, 8&nbsp;GB of RAM and 40&nbsp;GB of disk work well) and follow the Linux steps inside it. A virtual machine normally has no 3D acceleration: comment out the <code>/dev/dri</code> line as explained in <a href=\"/manual/lanzar\">LANZAR_PROYECTO.md</a>.",
  "t1c1a6d": "Open <code>http://localhost:8000</code> and sign in with <strong>admin</strong> / <strong>admin</strong>.",
  "t72c007": "It is a separate project that talks to the panel over the network — if you only want to play with orders and warehouse, step 1 is enough. The full commands (Webots + ROS 2, two containers) are in <a href=\"../LANZAR_PROYECTO.md\">LANZAR_PROYECTO.md</a>.",
  "ta10351": "The two Pandas, the belt and the physics of the cubes live in Webots. ROS 2 connects all the Python nodes: arm kinematics, cameras, grasp control and the control panel.",
  "td1d561": "Simulation",
  "t314a36": "Touch it yourself",
  "t8701b7": "<strong>Virtual Robotic</strong> is the name we gave to that virtual workshop: two simulated Panda arms that pick, sort and deliver pieces without losing a single one, with computer vision checking every grasp — and some real hardware thrown in, explained a little further down.",
  "tf49ab8": "Two Raspberry Pi Pico",
  "t239bcb": "How it is built",
  "t48980b": "Three pieces of one cell",
  "t390f9d": "The two Raspberry Pi Picos on a breadboard, with the product LED lit in blue and green, wired to the HC-SR04 sensor at the top left.",
  "t6dc8b6": "Open <strong>http://localhost:8000</strong>. Start-up user: <strong>admin</strong> / <strong>admin</strong>. Any user you create with the \"normal\" role also signs in with the password <strong>1111</strong>, meant precisely to let someone in to have a look around without giving them an account of their own.",
  "t6a4b8e": "<strong>System:</strong> Linux Mint or Ubuntu 24.04 (it also works inside a virtual machine running Linux Mint).",
  "t4b1415": "Screenshot of the Webots simulation: the two Panda arms, the belt with coloured cubes and the two computer-vision camera windows in the corners.",
  "ta772bd": "Download the code and start the orders website:",
  "t55c907": "Access",
  "t2e3a20": "This opens the real panel (Taller_Administracion) at <code>localhost:8000</code>. It only works if you have it running yourself — see <a href=\"#jugar\">Play with it</a> to start it in two commands.",
  "t232b7d": "Start-up user: <strong>admin</strong> / <strong>admin</strong>. Any user you create with the \"normal\" role also signs in with the password <strong>1111</strong>, meant precisely to let someone in to have a look around without giving them an account of their own.",
  "t71996f": "Linux <small>— where we have tested it</small>",
  "t92eb39": "Close",
  "t64cabd": "3 — Start the simulated cell (optional)",
  "tc240fc": "Gernika estuary, Bizkaia",
  "t1a6a87": "<strong>The cell with the robots:</strong> <strong>it is not tested on Windows</strong>. It uses Docker with Linux graphical windows. The way we have tested is a <strong>Linux virtual machine</strong> (VirtualBox with Linux Mint). Another option, untested: WSL&nbsp;2 with Ubuntu, which on Windows&nbsp;11 already brings graphical windows, and follow the Linux steps there.",
  "t639ada": "You do not need to know any of this to play with the project — it is only for those who feel technically curious, told in the same hobbyist vocabulary I used to build it.",
  "t6b1124": "Everything else (Python, FastAPI, ROS&nbsp;2, Webots…) lives inside the containers: you do not have to install it by hand. The <strong>Raspberry Pi Picos</strong> are optional (a USB cable and Thonny). Always start with the orders website: the \"Play with it\" section gives you the commands.",
  "t9562a2": "This did not start as a business plan: it started with wanting to understand how a robot arm really moves, cube by cube, until a good grasp was no longer enough and sorting, restocking and orders had to be solved as if it were a real workshop.",
  "t2127e4": "1 — Start the orders panel",
  "tac6cb6": "Origin",
  "t88d823": "Sign in to the system",
  "tf9dd43": "<a class=\"btn-ghost\" href=\"/manual/lanzar\">📘 How to start everything</a> <a class=\"btn-ghost\" href=\"/manual/taller\">📦 Our orders website</a> <a class=\"btn-ghost\" href=\"/manual/panda\">🤖 Our production line</a>",
  "t93ede0": "Verification by real position",
  "tc4eff0": "The manuals just as I use them, not polished for visitors:",
  "t48301d": "Restocking without intervention",
  "t468a5a": "From curiosity to a whole workshop",
  "t828bac": "<a class=\"btn-primary\" href=\"#jugar\" style=\"text-decoration:none;\">Play with it</a>",
  "t6e7bc0": "Password",
  "t63f672": "One carries a real LED that shows the colour of the product being made; the other, a proximity sensor that acts as an emergency stop button. They are a physical extra, not a part of the machinery: <strong>if these two Picos do not start, the rest of the cell works exactly the same.</strong>",
  "t4eaf34": "Every sorted piece instantly notifies a web orders panel: what was ordered, what is still to be made, what is ready and what has already been delivered to the customer, with its numbered delivery note and amounts. If the panel is off the cell keeps working the same, only nobody records the production in any order.",
  "tc54e67": "Code",
  "t0f3c68": "It is not enough for the finger sensor to say \"I have something\": where the cube really is gets checked too. If a cube is lost or stuck, it is rescued by itself instead of the robot carrying on blindly.",
  "t92e27d": "How to install it, step by step",
  "t3207a8": "One arm loads pieces onto a belt, the other picks them up and sorts them by colour. Every grasp is checked with computer vision before it is accepted — if the arm thinks it holds a piece it does not have, it is detected and corrected by itself.",
  "ta5ae08": "User",
  "t9c1e40": "It is a separate project that talks to the panel over the network — if you only want to play with orders and warehouse, step 1 is enough. The full commands (Webots + ROS 2, two containers) are in <a href=\"/manual/lanzar\">LANZAR_PROYECTO.md</a>.",
  "t219360": "Open PowerShell, download the code and start the orders website:",
  "tce97ea": "When it finishes, open <code>http://localhost:8000</code> and sign in with <strong>admin</strong> / <strong>admin</strong>.",
  "td62a32": "Language",
  "t36583b": "To use Docker without <code>sudo</code>, add your user to the group and <strong>log out and back in</strong>:",
  "t608db5": "Personal robotics project · Gernika estuary",
  "tb9024d": "<strong>So why are they there?</strong> Because that is where it all started. I did not have a real robot (an arm like the Panda costs a fortune), but I wanted to touch something physical: to make what happens inside the computer do something <em>for real</em>, outside the screen. So I started with a Pico, an LED and a button wired by hand on a breadboard. When the LED takes the colour of the piece the simulated robot is making, or when you bring your hand close to the sensor and everything stops, you can tell the software is attached to the real world. Then everything else grew and the Picos stayed as the bridge between the virtual and the physical: the day a real robot arrives, I already know how to plug things into the computer.",
  "t1122f1": "2 — Sign in to the system",
  "tc5cc77": "Vision",
  "t079912": "For those who want to go into detail",
  "t165471": "Warehouse and traceability",
  "t9ac83d": "<a class=\"btn-ghost\" href=\"../LANZAR_PROYECTO.md\">📘 How to start everything</a> <a class=\"btn-ghost\" href=\"../Taller_Administracion/README.md\">📦 Our orders website</a> <a class=\"btn-ghost\" href=\"../Lab.Panda%202.4/resumen_proyecto_panda.md\">🤖 The Panda simulation</a>",
  "tc31836": "The orders panel just below this page is a separate project that only talks to the cell over HTTP. It has its own user roles, a two-stage order cycle (pieces ready and then delivered, with a delivery note) prepared for invoicing, and over 250 automated tests that check, among other things, that stock is never handed out on its own.",
  "t52cb90": "<strong>Docker</strong> with <strong>Docker Compose v2</strong> (the <code>docker compose</code> command) and your user in the <code>docker</code> group. Plus <strong>Git</strong> to download the code.",
  "t49f508": "Warehouse",
  "tc8694e": "Hands on",
  "t3841a5": "What you need to install it",
  "t7e7e50": "Play with it",
  "t36c58c": "How it works",
  "t59c5ce": "Two arms that pick and sort",
  "t41ca21": "The belt moves the pieces and a tray (shuttle) brings them to the exact grasping point. The workstation never runs out of pieces: it restocks itself, with nobody having to keep watch.",
  "t2dc777": "Virtual Robotic does not sell anything — it is a personal project that keeps growing piece by piece. All the code is on GitHub: download it, open it, break it.",
  "t947c38": "The orders panel is a separate project that only talks to the cell over HTTP, with its own user roles, a two-stage order cycle (pieces ready and then delivered, with a delivery note) prepared for invoicing, and over 250 automated tests that check that stock is never handed out on its own. The catalogue distinguishes product, variant (sub-product) and kit (package); each one can carry, if wanted, an associated colour LED — it is only decoration to see at a glance what is being made, never a requirement for production to work.",
  "tc70f4f": "Open a terminal and install Git, Docker and Docker Compose (the last line is only for the cell with robots):",
  "tbb14ef": "A hobbyist, two simulated robot arms and a warehouse that runs by itself. None of this is a real company — it is a project that has grown piece by piece and that you can now touch.",
  "t9b4bd7": "Built with <a href=\"https://claude.com/claude-code\">Claude Code</a> (Anthropic).",
  "t8d0305": "Belt and tray",
  "tded7f5": "<strong>Only the orders website:</strong> that is all you need. It takes up a little over 0.5&nbsp;GB.",
  "t2e7ad2": "Loader &amp; Sorter"
 },
 "eu": {
  "t22a830": "2 — Sartu panelean",
  "t225062": "Orri hau ikusten ari bazara, eskaeren panela martxan dagoelako da — sakatu goiko \"Sartu\" botoia <strong>admin</strong> / <strong>admin</strong> erabiliz eta zuzenean sisteman sartuko zara. Zeure ordenagailuan hutsetik jarri nahi baduzu:",
  "t60d2bc": "<strong>Robotekin gelaxka</strong> (Webots + ROS&nbsp;2): horrez gain, X11 duen mahaigain grafikoa eta <code>xhost</code> agindua, <strong>15&nbsp;GB disko</strong> libre inguru, <strong>8&nbsp;GB RAM</strong> edo gehiago eta internet lehen aldian (Webots eta bere testurak deskargatzen ditu). Txartel grafikoarekin arin dabil; gabe, <code>docker-compose.yml</code> fitxategiko lerro bat komentatu behar da eta motelago dabil.",
  "t906fa5": "<strong>Eskaeren webgunea soilik:</strong> <strong>Docker Desktop</strong> (WSL&nbsp;2 gaituta) eta <strong>Git for Windows</strong>. Gero <code>docker compose up -d --build</code> eta ireki <code>http://localhost:8000</code>. Python irudi arrunt bat da, baina <strong>ez dugu Windows-en probatu</strong>.",
  "tfa5e9f": "Barne-sarbidea",
  "tcb4bc0": "<strong>Git:</strong> instalatu <em>Git for Windows</em> git-scm.com-etik (\"Hurrengoa\" sakatzearekin nahikoa da).",
  "td8741c": "Egiaztatu funtzionatzen duela:",
  "taea234": "Windows",
  "t441220": "Sartu ekoizpenean",
  "ta127c8": "Robotekin gelaxkarako jarraitu <a href=\"/manual/lanzar\">LANZAR_PROYECTO.md</a>. Lehen aldian nahiko denbora behar du, Webots deskargatzen delako.",
  "tb687c6": "Sartu",
  "tb72d12": "Aukerakoa, ez kritikoa",
  "t5988a9": "<strong>Robotentzat:</strong> instalatu <em>VirtualBox</em>, sortu makina birtual bat <em>Linux Mint</em>-ekin (4 prozesadore, 8&nbsp;GB RAM eta 40&nbsp;GB disko ondo doaz) eta barruan Linux-eko pausoak jarraitu. Makina birtual batean normalean ez dago 3D azelerazioa: komentatu <code>/dev/dri</code> lerroa <a href=\"../LANZAR_PROYECTO.md\">LANZAR_PROYECTO.md</a>-n azaltzen den bezala.",
  "tede40a": "Docker instalatuta izanda, zeure ordenagailuan abiarazten da komando pare batean. Ez duzu Raspberry Pi Pico-ak ezta gainerako hardware fisikoa ere behar funtzionatzeko.",
  "td3888c": "Robotekin gelaxkarako jarraitu <a href=\"../LANZAR_PROYECTO.md\">LANZAR_PROYECTO.md</a>. Lehen aldian nahiko denbora behar du, Webots deskargatzen delako.",
  "t03d264": "<strong>Docker Desktop:</strong> deskargatu <em>Docker Desktop for Windows</em> instalatzailea docker.com-etik eta utzi <em>Use WSL 2</em> aukera markatuta. Berrabiarazi PC-a, ireki Docker Desktop eta itxaron <em>Engine running</em> jartzen duen arte. WSL falta dela esaten badizu, ireki PowerShell <strong>administratzaile gisa</strong>, idatzi <code>wsl --install</code> eta berrabiarazi.",
  "t1edcfb": "Eskaeren panela",
  "t0b6986": "<strong>Robotentzat:</strong> instalatu <em>VirtualBox</em>, sortu makina birtual bat <em>Linux Mint</em>-ekin (4 prozesadore, 8&nbsp;GB RAM eta 40&nbsp;GB disko ondo doaz) eta barruan Linux-eko pausoak jarraitu. Makina birtual batean normalean ez dago 3D azelerazioa: komentatu <code>/dev/dri</code> lerroa <a href=\"/manual/lanzar\">LANZAR_PROYECTO.md</a>-n azaltzen den bezala.",
  "t1c1a6d": "Ireki <code>http://localhost:8000</code> eta sartu <strong>admin</strong> / <strong>admin</strong> erabiliz.",
  "t72c007": "Proiektu bereizi bat da, panelarekin sarearen bidez hitz egiten duena — eskaerekin eta biltegiarekin soilik jolastu nahi baduzu, 1. pausoarekin nahikoa duzu. Komando osoak (Webots + ROS 2, bi edukiontzi) <a href=\"../LANZAR_PROYECTO.md\">LANZAR_PROYECTO.md</a> fitxategian daude.",
  "ta10351": "Bi Pandak, uhala eta kuboen fisika Webots-en bizi dira. ROS 2-k Python nodo guztiak lotzen ditu: besoen zinematika, kamerak, harrapaketaren kontrola eta agintepanela.",
  "td1d561": "Simulazioa",
  "t314a36": "Ukitu ezazu zeuk",
  "t8701b7": "<strong>Virtual Robotic</strong> da tailer birtual horri jarri diogun izena: simulatutako bi Panda beso, piezak hartu, sailkatu eta entregatzen dituztenak bat ere galdu gabe, ikusmen artifizialak harrapaketa bakoitza egiaztatzen duela — eta benetako hardware apur bat tartean, beherago azalduko dena.",
  "tf49ab8": "Bi Raspberry Pi Pico",
  "t239bcb": "Nola dagoen eginda",
  "t48980b": "Gelaxka bereko hiru pieza",
  "t390f9d": "Bi Raspberry Pi Pico protoboard baten gainean, produktuaren LED-a urdin eta berdez piztuta, goian ezkerrean dagoen HC-SR04 sentsorera kableatuta.",
  "t6dc8b6": "Ireki <strong>http://localhost:8000</strong>. Hasierako erabiltzailea: <strong>admin</strong> / <strong>admin</strong>. \"Normal\" rolarekin sortzen duzun edozein erabiltzailek ere <strong>1111</strong> pasahitzarekin sartzen da, norbaiti kontu propiorik eman gabe kuxkuxeatzen uzteko pentsatua.",
  "t6a4b8e": "<strong>Sistema:</strong> Linux Mint edo Ubuntu 24.04 (Linux Mint duen makina birtual baten barruan ere funtzionatzen du).",
  "t4b1415": "Webots simulazioaren pantaila-argazkia: bi Panda besoak, kolorezko kuboak dituen uhala eta ikusmen artifizialeko bi kamera-leihoak izkinetan.",
  "ta772bd": "Deskargatu kodea eta abiarazi eskaeren webgunea:",
  "t55c907": "Sarbidea",
  "t2e3a20": "Honek benetako panela irekitzen du (Taller_Administracion) <code>localhost:8000</code> helbidean. Zuk martxan jarrita baduzu bakarrik funtzionatzen du — ikusi <a href=\"#jugar\">Jolastu harekin</a> bi komandotan abiarazteko.",
  "t232b7d": "Hasierako erabiltzailea: <strong>admin</strong> / <strong>admin</strong>. \"Normal\" rolarekin sortzen duzun edozein erabiltzailek ere <strong>1111</strong> pasahitzarekin sartzen da, norbaiti kontu propiorik eman gabe kuxkuxeatzen uzteko pentsatua.",
  "t71996f": "Linux <small>— probatu dugun tokian</small>",
  "t92eb39": "Itxi",
  "t64cabd": "3 — Abiarazi simulatutako gelaxka (aukerakoa)",
  "tc240fc": "Gernikako itsasadarra, Bizkaia",
  "t1a6a87": "<strong>Robotekin gelaxka:</strong> <strong>ez dago Windows-en probatuta</strong>. Docker erabiltzen du Linux leiho grafikoekin. Probatu dugun bidea <strong>Linux makina birtual</strong> bat da (VirtualBox eta Linux Mint). Beste aukera bat, probatu gabe: WSL&nbsp;2 eta Ubuntu, Windows&nbsp;11-n leiho grafikoak dakartzana, eta bertan Linux-eko pausoak jarraitu.",
  "t639ada": "Ez duzu honetako ezer jakin beharrik proiektuarekin jolasteko — jakin-min teknikoa duenarentzat besterik ez da, nik eraikitzeko erabili dudan zaletuaren hiztegi berarekin kontatua.",
  "t6b1124": "Gainerako guztia (Python, FastAPI, ROS&nbsp;2, Webots…) edukiontzien barruan dago: ez da eskuz instalatu behar. <strong>Raspberry Pi Pico</strong>-ak aukerakoak dira (USB kable bat eta Thonny). Hasi beti eskaeren webgunearekin: \"Jolastu harekin\" atalak komandoak ematen dizkizu.",
  "t9562a2": "Hau ez zen negozio-plan batekin hasi: beso robotiko batek benetan nola mugitzen den ulertu nahi izatetik hasi zen, kuboz kubo, harrapaketa on bat nahikoa izan ez zen arte eta sailkapena, berrornitzea eta eskaerak benetako tailer batean bezala ebatzi behar izan ziren.",
  "t2127e4": "1 — Abiarazi eskaeren panela",
  "tac6cb6": "Jatorria",
  "t88d823": "Sartu sisteman",
  "tf9dd43": "<a class=\"btn-ghost\" href=\"/manual/lanzar\">📘 Dena nola abiarazi</a> <a class=\"btn-ghost\" href=\"/manual/taller\">📦 Gure eskaeren webgunea</a> <a class=\"btn-ghost\" href=\"/manual/panda\">🤖 Gure ekoizpen-katea</a>",
  "t93ede0": "Benetako posizioaren bidezko egiaztapena",
  "tc4eff0": "Eskuliburuak nik erabiltzen ditudan bezala, bisitarientzat leundu gabe:",
  "t48301d": "Berrornitzea inor tartean egon gabe",
  "t468a5a": "Jakinminetik tailer oso batera",
  "t828bac": "<a class=\"btn-primary\" href=\"#jugar\" style=\"text-decoration:none;\">Jolastu harekin</a>",
  "t6e7bc0": "Pasahitza",
  "t63f672": "Batek benetako LED bat darama, fabrikatzen ari den produktuaren kolorea adierazten duena; besteak hurbiltasun-sentsore bat, larrialdiko geldiketa-botoi gisa jarduten duena. Gehigarri fisiko bat dira, ez makinaria osoaren pieza bat: <strong>bi Pico hauek abiarazten ez badira, gelaxkaren gainerakoak berdin-berdin funtzionatzen du.</strong>",
  "t4eaf34": "Sailkatutako pieza bakoitzak berehala abisatzen dio eskaeren web panel bati: zer eskatu den, zer falta den fabrikatzeko, zer dagoen prest eta zer entregatu zaion dagoeneko bezeroari, bere albaran zenbakituarekin eta zenbatekoekin. Panela itzalita badago gelaxkak berdin jarraitzen du, baina inork ez du ekoizpena eskaeretan apuntatzen.",
  "tc54e67": "Kodea",
  "t0f3c68": "Ez da nahikoa hatzen sentsoreak \"zerbait dut\" esatea: kuboa benetan non dagoen ere egiaztatzen da. Kubo bat galtzen bada edo trabatzen bada, bere kasa erreskatatzen da, robota itsu-itsuan jarraitu beharrean.",
  "t92e27d": "Nola instalatu, pausoz pauso",
  "t3207a8": "Beso batek piezak uhal batean kargatzen ditu, besteak jaso eta koloreka sailkatzen ditu. Harrapaketa bakoitza ikusmen artifizialarekin egiaztatzen da onartu aurretik — besoak ez duen pieza bat duela uste badu, detektatu eta bere kasa zuzentzen da.",
  "ta5ae08": "Erabiltzailea",
  "t9c1e40": "Proiektu bereizi bat da, panelarekin sarearen bidez hitz egiten duena — eskaerekin eta biltegiarekin soilik jolastu nahi baduzu, 1. pausoarekin nahikoa duzu. Komando osoak (Webots + ROS 2, bi edukiontzi) <a href=\"/manual/lanzar\">LANZAR_PROYECTO.md</a> fitxategian daude.",
  "t219360": "Ireki PowerShell, deskargatu kodea eta abiarazi eskaeren webgunea:",
  "tce97ea": "Amaitzean, ireki <code>http://localhost:8000</code> eta sartu <strong>admin</strong> / <strong>admin</strong> erabiliz.",
  "td62a32": "Hizkuntza",
  "t36583b": "Docker <code>sudo</code> gabe erabiltzeko, gehitu zure erabiltzailea taldera eta <strong>itxi saioa eta sartu berriro</strong>:",
  "t608db5": "Robotika proiektu pertsonala · Gernikako itsasadarra",
  "tb9024d": "<strong>Orduan zergatik daude?</strong> Hemen hasi zelako dena. Ez nuen benetako robot bat (Panda bezalako beso batek dirutza balio du), baina zerbait fisikoa ukitu nahi nuen: ordenagailuaren barruan gertatzen dena <em>benetan</em> zerbait egitea pantailatik kanpo. Beraz, Pico batekin, LED batekin eta botoi batekin hasi nintzen, protoboard batean eskuz kableatuak. LED-a simulatutako robotak fabrikatzen duen piezaren kolorea hartzen duenean, edo eskua sentsorera hurbiltzen duzunean eta dena gelditzen denean, software-a mundu errealari lotuta dagoela nabari da. Gero gainerako guztia hazi zen eta Pico-ak birtualaren eta fisikoaren arteko zubi gisa geratu ziren: benetako robot bat iristen den egunean, jada badakit nola konektatu gauzak ordenagailura.",
  "t1122f1": "2 — Sartu sisteman",
  "tc5cc77": "Ikusmena",
  "t079912": "Xehetasunetan sartu nahi dutenentzat",
  "t165471": "Biltegia eta trazabilitatea",
  "t9ac83d": "<a class=\"btn-ghost\" href=\"../LANZAR_PROYECTO.md\">📘 Dena nola abiarazi</a> <a class=\"btn-ghost\" href=\"../Taller_Administracion/README.md\">📦 Gure eskaeren webgunea</a> <a class=\"btn-ghost\" href=\"../Lab.Panda%202.4/resumen_proyecto_panda.md\">🤖 Panda-en simulazioa</a>",
  "tc31836": "Web honen azpian duzun eskaeren panela proiektu bereizi bat da, gelaxkarekin HTTP bidez soilik hitz egiten duena. Bere erabiltzaile-rolak ditu, bi faseko eskaera-ziklo bat (piezak prest eta gero banatuta, albaranarekin) fakturatzeko prest, eta 250 proba automatiko baino gehiago, besteak beste stocka inoiz bere kasa ez dela banatzen egiaztatzen dutenak.",
  "t52cb90": "<strong>Docker</strong> eta <strong>Docker Compose v2</strong> (<code>docker compose</code> agindua), eta zure erabiltzailea <code>docker</code> taldean. Eta <strong>Git</strong> kodea deskargatzeko.",
  "t49f508": "Biltegia",
  "tc8694e": "Eskuak lanean",
  "t3841a5": "Zer behar duzun instalatzeko",
  "t7e7e50": "Jolastu harekin",
  "t36c58c": "Nola dabilen",
  "t59c5ce": "Hartu eta sailkatzen duten bi beso",
  "t41ca21": "Uhalak piezak mugitzen ditu eta erretilu batek (shuttle) harrapatzeko puntu zehatzera hurbiltzen ditu. Lanpostua ez da inoiz piezarik gabe geratzen: bere kasa berrornitzen da, inor adi egon beharrik gabe.",
  "t2dc777": "Virtual Robotic-ek ez du ezer saltzen — pixkanaka hazten jarraitzen duen proiektu pertsonala da. Kode guztia GitHub-en dago: deskargatu, ireki, apurtu.",
  "t947c38": "Eskaeren panela proiektu bereizi bat da, gelaxkarekin HTTP bidez soilik hitz egiten duena, bere erabiltzaile-rolekin, bi faseko eskaera-ziklo batekin (piezak prest eta gero banatuta, albaranarekin) fakturatzeko prest, eta 250 proba automatiko baino gehiagorekin, stocka inoiz bere kasa ez dela banatzen egiaztatzen dutenak. Katalogoak produktua, aldaera (azpiproduktua) eta kit-a (paketea) bereizten ditu; bakoitzak, nahi bada, kolorezko LED bat izan dezake lotuta — zer fabrikatzen den begiratu batean ikusteko apaingarri bat besterik ez da, inoiz ez ekoizpenak funtzionatzeko baldintza.",
  "tc70f4f": "Ireki terminal bat eta instalatu Git, Docker eta Docker Compose (azken lerroa robotekin gelaxkarako bakarrik da):",
  "tbb14ef": "Zaletu bat, simulatutako bi beso robotiko eta bere kasa dabilen biltegi bat. Hau ez da benetako enpresa bat — pixkanaka hazi den proiektu bat da, eta orain ukitu daiteke.",
  "t9b4bd7": "<a href=\"https://claude.com/claude-code\">Claude Code</a>-rekin eraikia (Anthropic).",
  "t8d0305": "Uhala eta erretilua",
  "tded7f5": "<strong>Eskaeren webgunea soilik:</strong> horrekin nahikoa duzu. 0,5&nbsp;GB baino apur bat gehiago hartzen du.",
  "t2e7ad2": "Loader &amp; Sorter"
 }
};
(function () {
  var D = window.VR_I18N;
  function poner(lang) {
    var tr = lang !== 'es' ? (D[lang] || {}) : {};
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      if (el.dataset.es === undefined) el.dataset.es = el.innerHTML;
      var t = tr[el.getAttribute('data-i18n')];
      el.innerHTML = t !== undefined ? t : el.dataset.es;
    });
    ['alt', 'title', 'aria-label'].forEach(function (attr) {
      document.querySelectorAll('[data-i18n-' + attr + ']').forEach(function (el) {
        var guardado = 'es' + attr.replace('-', '');
        if (el.dataset[guardado] === undefined) el.dataset[guardado] = el.getAttribute(attr) || '';
        var t = tr[el.getAttribute('data-i18n-' + attr)];
        el.setAttribute(attr, t !== undefined ? t : el.dataset[guardado]);
      });
    });
    document.documentElement.lang = lang;
  }
  window.VR_aplicarIdioma = poner;
})();

// Textos que la propia pagina escribe con JavaScript (boton de entrar, sesion iniciada).
(function () {
  var DIN = {
    en: {'Entrar': 'Sign in', 'Entrar al sistema ↗': 'Go to the system ↗', 'Salir': 'Sign out', 'Producción': 'Production'},
    eu: {'Entrar': 'Sartu', 'Entrar al sistema ↗': 'Sisteman sartu ↗', 'Salir': 'Irten', 'Producción': 'Ekoizpena'}
  };
  window.VR_tr = function (es) {
    var d = DIN[document.documentElement.lang];
    return (d && d[es]) || es;
  };
  var base = window.VR_aplicarIdioma;
  window.VR_aplicarIdioma = function (lang) {
    base(lang);
    if (window.VR_alCambiarIdioma) window.VR_alCambiarIdioma();
  };
})();
