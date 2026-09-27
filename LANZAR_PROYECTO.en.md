_Last updated: 2026-09-26 11:37_

# Starting the project (Linux)

Guide for **Linux**. On Windows, see [INSTALAR_WINDOWS.en.md](INSTALAR_WINDOWS.en.md).

## First of all: install what you need

Tested on **Linux Mint / Ubuntu 24.04**. You need:

- **Only the orders website:** Docker (with Docker Compose v2) and Git.
- **The cell with the robots:** the above, plus a graphical desktop (logging
  in over SSH is not enough), about 15 GB of disk, 8 GB of RAM or more, and
  internet the first time. With a graphics card it runs smoothly; without one
  you have to remove one line (`/dev/dri`) from `docker-compose.yml`, as
  explained below, and it runs slower.

Everything else (Python, ROS 2, Webots…) goes inside Docker; you do not
have to install it. The Raspberry Pi Pico boards are optional.

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-v2
sudo apt install -y x11-xserver-utils      # only for the cell with robots
sudo usermod -aG docker $USER              # then log out and back in
docker --version && docker compose version # check that it works

git clone https://github.com/virtual-robotic/virtual-robotic.git
```

To see **only the orders website**, this is enough:

```bash
cd virtual-robotic/Taller_Administracion
docker compose up -d --build               # and open http://localhost:8000
```

## Starting it

Every `cd` below is **relative to the project folder** (wherever you
cloned or copied `virtual-robotic`, or `Robotica` if it's your own
copy). Get there first:

```bash
cd virtual-robotic   # or wherever you have it
```

**Shortcut:** `./arrancar_todo.sh` does Parts A and B below in one go
(without the physical Picos) and finishes by opening the manual
control panel. It needs a local graphical session (plain SSH won't do)
and `xhost`.

**The first time, it's better NOT to use the shortcut — start by hand,
step by step (Parts A and B below).** It's not that the script is
broken: it's that the first build of the Webots image downloads a
large package (Webots itself) and **can look stuck for a long while
around 70-80%** — without seeing the steps separately it's easy to
think something failed and cut it off mid-build (which really does
leave the build half-done). Going step by step you can see exactly
where it stops and how long each part takes; once you know it works
on your machine/VM, go ahead and use `./arrancar_todo.sh` for next
times, it reuses everything already built and is fast.

![Webots window stuck on "Downloading assets" at 72%, with a Cancel button — this is normal the first time, not a failure](img/webots_atasco_72_porciento.png)

This is exactly what you're going to see: a Webots window with
"Downloading assets" stuck somewhere between 70 and 90% for a good
while. **Don't press Cancel.**

**Why it only happens "the first time":** Docker caches every step of
the image build. Downloading the Webots package is a step that, once
it completes successfully once, stays cached — the next build of that
same image skips it entirely and flies through the 70-80% mark. It
doesn't have to be literally your first time starting the project: it's
the first time that particular image is built on that machine (if you
delete the clone and clone again, or run `docker system prune`, you'll
have to wait there again).

**If `arrancar_todo.sh` doesn't work the first time** (the control
panel never opens, or the controllers don't connect despite the
automatic retry), the simplest thing, and what works best in practice,
is `./cerrar_todo.sh` followed by `./arrancar_todo.sh` again — seen
live that the second round starts fine even when the first didn't. We
haven't pinned down the exact cause of why it sometimes fails on a
first cold start, so for now this is the recipe that works, not a full
explanation.

If the script still fails for you or looks odd, or you'd simply rather
have the loose commands, keep reading — it's the same sequence the
script runs, explained step by step.

There are **two independent projects** that talk to each other over the
network (HTTP), sharing no code or containers:

1. **`Lab.Panda 2.4`** — the simulation (Webots + ROS 2): two Panda arms
   (Loader and Sorter) that move cubes along a belt and sort them by
   colour, plus two Raspberry Pi Picos each with a real RGB LED.
2. **`Taller_Administracion`** — the orders and warehouse web server
   (FastAPI + SQLite). It finds out what the robot makes over HTTP; if
   it's off, the simulation keeps working exactly the same, just with
   nobody logging the production against any order.

You can start only the one you need. If you're going to do real
production (orders completing on their own), you need both.

## The project's 3 Docker containers

| Container | From which project | What it is |
|---|---|---|
| `webots_panda_sim24` | Lab.Panda 2.4 | The 3D simulation (Webots) |
| `ros2_panda_dev24` | Lab.Panda 2.4 | ROS 2 and every Python node (arms, cameras, LEDs, control panel) |
| `taller_admin_api` | Taller_Administracion | The orders/warehouse web server |

Check with `docker ps`. **If you see other names** (`ros2_dev`,
`webots_sim`, or the same ones without the trailing `24`) they're
leftovers from an old, already-deleted project (`Lab.Panda 2.3`) —
stop and remove them before going on: `docker stop <name> && docker rm <name>`.

---

## Part A — Taller_Administracion (the simplest one, no Webots)

```bash
cd Taller_Administracion
docker compose up -d --build
```

Open **http://localhost:8000**: the "Virtual Robotic" presentation web
comes up (the same as `Virtual_Robotic/index.html`, but really served
by this app). Press "Sign in" with the starter user `admin` / `admin`
and you go straight into the real system at `/panel` -- a single
login, you don't have to sign in again there.

Any `normal` user that gets created also logs in with the master
password `1111` (meant to let someone "play" without being given an
account); for `admin_sistema`/`admin_cliente` the master password only
works with `TALLER_DEV_MODE=true` (already on in this project's
`docker-compose.yml`).

**The first time it starts against an empty database**, the server
itself seeds sample data so you're not starting completely from
scratch: 7 LED colours, 3 products (Screws/Nuts/Washers) with their
variants and 2 packages, and 3 sample companies (Ferretería Ereño,
Suministros Mungia, Construcciones Busturia) with users already spread
across different sites and their catalogue already assigned — with the
master password `1111` you can log in as any of them and place real
orders without signing anything up by hand. If `data/taller.db`
already existed (a reused volume), this seeding doesn't repeat or
overwrite anything.

**To see it from your phone** (same Wi-Fi as this computer): use this
PC's local IP instead of `localhost` —
```bash
hostname -I   # take the one starting with 192.168.x.x
```
and go to `http://<that_ip>:8000`.

To shut it down: `docker compose down` in this same folder.

---

## Part B — Lab.Panda 2.4 (the simulation)

### 0. Power on the two Raspberry Pi Picos (before anything else)

**Not required** — they're optional physical hardware, see "How it's
built" further up. If you don't have them or don't connect them, the
cell works exactly the same, just without the real LED, the physical
stop button or the screen. All the information on how they're wired up
(pins, wiring, resistors, firmware) is in
[Documentacion/PI_PICO_montaje.html](Documentacion/PI_PICO_montaje.html),
and the specific wiring for the Loader's OLED screen (what shows the
current product) in
[Documentacion/PI_PICO_cableado_oled.html](Documentacion/PI_PICO_cableado_oled.html).

### Your Wi-Fi: the Pico W's credentials (read this before touching the Pico)

The Sorter's Pico W needs to join your Wi-Fi, and for that there are
two files in `Rasberry_Pi_Pico/`. **In the repository they're only
templates**, with nobody's real credentials:

| File | What to fill in |
|---|---|
| `wifi_config.py` | `SSID` (your Wi-Fi's name), `PASSWORD` (its password) and `PC_IP` (**this computer's** IP on the network; get it with `hostname -I`) |
| `webrepl_cfg.py` | `PASS`: any password to reach the Pico over WebREPL |

1. Edit both files with your own details and copy them to the Pico
   (Thonny → *Save as…* → device).
2. **So Git doesn't accidentally upload your credentials**, tell it to
   forget those changes:
   ```bash
   git update-index --skip-worktree Rasberry_Pi_Pico/wifi_config.py Rasberry_Pi_Pico/webrepl_cfg.py
   ```
   From then on those two files won't show up as modified, even with
   your credentials in them. If you ever want to *really* change the
   template: `--no-skip-worktree`, change it, commit, and mark them
   again (saving your own credentials aside first).
3. **Never push your real credentials.** If they slip into a commit,
   change your Wi-Fi password: deleting the commit afterwards isn't
   enough if someone already copied it.
4. If your router changes your computer's IP, update `PC_IP`:
   otherwise the Pico's stop button stops notifying the robot.

The Loader's Pico goes over USB and **doesn't need Wi-Fi**.

There's one Pico per robot, each with its own LED:

- **Sorter → the usual Pico W** (`Rasberry_Pi_Pico/`, over Wi-Fi). Power
  it on; `main.py` starts on its own and connects to the Wi-Fi, ending
  up listening on `192.168.1.101:5001`. It's also the one carrying the
  **physical emergency stop button** (see further down).
- **Loader → the new Pico with no Wi-Fi** (`Rasberry_Pi_Pico_USB_Loader/`).
  Plug it into this computer over USB (`docker-compose.yml` already
  knows how to find it on its own via its stable
  `/dev/serial/by-id/` path, no need to touch anything unless you
  swap it for a different Pico).

### 1. Authorise the display and bring up the 2 simulation containers

```bash
xhost +local:docker
```
Needed so Webots (and any graphical window launched inside the
container) can draw on your screen.

```bash
cd "Lab.Panda 2.4/.devcontainer"
docker compose up -d --build
```
**The first time really does take a while, and it can look stuck
around 70-80% of the progress** — that's where the Webots package
itself gets downloaded from Cyberbotics' repo (it's fairly large);
depending on your connection it can take several minutes without that
being a failure. The `-d` flag only matters once the containers are
already built and starting — while the image is **being built**, the
terminal keeps showing progress and you need to leave it open until it
finishes. If you close it mid-build (with the X, or Ctrl+C), the build
gets cut off and you'll have to repeat it: nothing permanent breaks,
but before retrying check nothing was left half-done with
`docker ps -a` and, if there's anything from the project, run
`docker compose down` before relaunching.

If the `webots` container fails to start complaining about
`/dev/dri` (no GPU/3D acceleration on that machine, typical on a VM
with acceleration not enabled), comment out the
`- /dev/dri:/dev/dri` line under `webots`'s `devices:` in this
`docker-compose.yml` — Webots falls back to software rendering,
slower but it works. The Loader's USB Pico (`ros2_app`) no longer has
this problem: by default (with no Pico connected, or on a machine that
has never had one, like a VM) the container starts the same, nothing
needs touching — see the comment on `ros2_app`'s `devices:` block in
the file itself if you want to enable that Pico on a machine that does
have one.

This creates/starts `webots_panda_sim24` (it loads the
`worlds/panda_industrial_cell.wbt` world directly, the two-robot cell)
and `ros2_panda_dev24`. Check with `docker ps`.

### 2. Build the package

**Required the first time** (a fresh clone, or if you've deleted
`ros2_ws/install/`): that directory holds regenerable artefacts and is
in `.gitignore` on purpose, so a `git clone` doesn't bring it — without
this step, step 3's `ros2 launch` fails because the package doesn't
exist yet. From then on, it's only needed if you've touched Python
code.

```bash
docker exec -it ros2_panda_dev24 bash
cd /workspace
colcon build --packages-select panda_controller --symlink-install
```

### 3. Launch the whole cell (leave this terminal open)

```bash
docker exec -it ros2_panda_dev24 bash
cd /workspace
ros2 launch panda_controller robot_launch_industrial_cell.py
```
This connects all 6 of the cell's "controllers" at once: the Loader
arm, the Sorter arm, the two overhead cameras (one over the Loader's
box, another over the Sorter's pickup point), the `WarehouseSupervisor`
(an invisible robot that watches the real position of the 3 cubes:
rescues any that fall and recycles the already-sorted ones back into
their box) and the `SorterShuttleSupervisor` (added 2026-09-10, with no
physical body either, like the previous one: the "tray" that centres
on X and rotates the cube arriving at the Sorter's pickup point, so it
doesn't land off-centre — see `Documentacion/carriles_completo.html`).
**Wait to see** `Controller successfully connected` **6 times** in the
log before going on.

**If after ~60 seconds none of them have connected** (seen live
several times, especially on a new machine/VM starting Webots cold for
the first time): there's no need to jump straight to "if something
gets stuck" further down, or to repeat everything from step 1. The
fastest fix, and what `arrancar_todo.sh` does automatically, is:
```bash
docker restart webots_panda_sim24
```
Wait about 20 seconds for Webots to load the world again and repeat
this same step 3 (`ros2 launch ...`) — the second time it connects
fine almost always. If it still doesn't connect after that, check
`docker exec ros2_panda_dev24 cat /tmp/robot_launch.log` (if you
launched it in the background) or the error in this terminal itself.

**This terminal stays open while you work.** If you close it (or the
command itself stops for whatever reason), this step stops being
"done" even if step 1's containers are still up — and **nothing**
below (LEDs, panel, production) will work until you relaunch it. To
check whether it's already running in ANOTHER terminal before
launching it again:
```bash
docker exec ros2_panda_dev24 bash -c "ps -ef | grep robot_launch_industrial_cell | grep -v grep"
```
If nothing shows up, it's not running — do this now before moving on
to step 4 or 5.

### 4. LED bridges (one per robot, each in its own terminal)

**Not needed if you don't have the Raspberry Pi Picos** (see step 0
above): without them there's nothing real to forward the colour to,
so just don't launch it — the cell works exactly the same, just
without the physical LED. It's not needed for the control panel
either (step 5): its **Raspberry Pi Pico** tab simulates the colour of
the 3 LEDs by listening to the same ROS topics, with no dependency on
this bridge (or the Pico) actually existing.

**Easier since 2026-09-14:** in the control panel (step 5),
**Configuration** tab → *Unlock (password)* → tick the Picos this
line uses → *Apply Pico configuration*. The panel launches the
bridges on its own (and relaunches them every time the panel starts),
and if you have two lines it makes sure each Pico only obeys one of
them. The manual commands below still work if you're not using the
panel.

> **The Configuration tab's password can be changed** (2026-09-21): on
> the tab itself, once unlocked, there's a *Change configuration
> password* box right under **Language**. You type the new password
> **twice**; it only gets saved if they match and are at least 4
> characters long. Each line has its own, it's saved encrypted (never
> in plain text) and it isn't lost on restart. If it's forgotten,
> delete the `clave_config` entry from that line's `config_maquina_*.json`
> file (in `ros2_ws/`) and the factory `1111` comes back.
>
> **Resetting it with the button** (2026-09-21): with the
> *Configuration* or *Raspberry Pi Pico* tab open, hold down the
> Loader's USB Pico button for **10 s** (or one of the simulated red
> buttons on the Pico tab; they show a countdown). The panel asks for
> confirmation and, once confirmed, brings back `1111` and the OLED
> shows *Password reset* for a few seconds. You need to **reflash
> `Rasberry_Pi_Pico_USB_Loader/main.py`** on that Pico with Thonny
> (Save as → device) and **relaunch `led_publisher_usb`** for it to
> take effect.

```bash
docker exec -it ros2_panda_dev24 bash
ros2 run panda_controller led_publisher       # Sorter, talks to the Pico over Wi-Fi
```
```bash
docker exec -it ros2_panda_dev24 bash
ros2 run panda_controller led_publisher_usb   # Loader, talks to the Pico over USB
```
Each one forwards whatever arrives on its ROS topic
(`/comando_led` for the Sorter, `/comando_led_loader` for the Loader)
to the real hardware. Without this the robot keeps moving exactly the
same, the physical LED just doesn't react.

### 5. Manual control panel (the place everything gets driven from)

**Needs step 3 really running** (see the box above) — otherwise it
spends 45s trying and fails with `ERROR [...] Nobody has subscribed
after 45s` and the window never opens.

```bash
docker exec -it ros2_panda_dev24 bash
ros2 run panda_controller teleop_gui
```
In a single window, this brings:
- A **LOADER / SORTER** selector to choose which arm you're moving by
  hand, without restarting anything.
- **STOP / RESET** for the whole cell (pauses whatever movement is in
  progress, it does NOT abort it; it resumes exactly where it left off
  once reset) — works whether you're moving the arm by hand or there's
  automatic production running.
- **Movement** tab: manual jog of the chosen arm.
- **Production** tab: a **"Launch batch"** button (makes a chosen
  quantity of a single, hand-picked product) and a **"Launch all
  pending orders"** button (looks at Taller_Administracion's real
  orders and makes whatever's missing of all three colours at once —
  needs Part A running).

With this alone, you can already produce without touching any other
terminal.

### 6. Automatic production by hand (an alternative to the panel's buttons)

Only if you'd rather launch it yourself from the terminal instead of
using step 5's buttons (for example, to set it going with specific
parameters):

```bash
docker exec -it ros2_panda_dev24 bash
# Sorter: picks up whatever reaches the belt and sorts it, any colour
ros2 run panda_controller sorter_demo --ros-args -r __ns:=/sorter \
  -p robot_base_x:=0.0 -p robot_base_y:=1.00 -p robot_base_z:=0.74
```
```bash
docker exec -it ros2_panda_dev24 bash
# Loader: hands out all three colours at once, 6 rounds
ros2 run panda_controller loader_demo --ros-args -r __ns:=/loader \
  -p cycles:=6 -p led_topic:=/comando_led_loader -p led_topic_producto:=/comando_led_producto
# or a single colour (e.g. 30 nuts = green):
ros2 run panda_controller loader_demo --ros-args -r __ns:=/loader \
  -p cycles:=30 -p only_color:=G -p led_topic:=/comando_led_loader -p led_topic_producto:=/comando_led_producto
```
**Don't launch this if you already have it running from the panel**
(step 5) — they'd fight over the same arm.

### 7. More than one production line (optional)

Everything above sets up **one** line (one Webots + its two robots).
You can switch on a second, a third... in parallel on the same
machine, each in its own containers, isolated from each other (they
don't clash or share robots) but **sharing the same web orders
panel** — nothing extra needs configuring there, the delivery logic
already knows how to split the work between whichever lines are
switched on.

There's already a ready-made, tested template
(`Lab.Panda 2.4/.devcontainer2`), so switching on the second line boils
down to:

```bash
cd "Lab.Panda 2.4/.devcontainer2" && docker compose up -d --build
docker exec -d ros2_panda_dev24_linea2 bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && cd /workspace && ros2 launch panda_controller robot_launch_industrial_cell.py > /tmp/robot_launch.log 2>&1"
docker exec -it ros2_panda_dev24_linea2 bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && ros2 run panda_controller teleop_gui"
```

And in the new panel that opens, **Configuration** tab (password
`1111`): give it a **Line name** to tell it apart, and a
**Machine No.** no other line is using (so order delivery doesn't
cross between lines). The physical Raspberry Pi Picos are only ticked
on the line that actually has them connected.

For a **third line or more**, instead of copying `.devcontainer2` and
changing the three fields by hand, there's a script that does it all
in one go (copies the template, renames boxes/network/`ROS_DOMAIN_ID`,
switches it on, launches the cell and waits for the 6 controllers to
connect):

```bash
./crear_linea.sh 3
# or with Machine No., Taller_Administracion's URL (if this line lives
# on ANOTHER computer) and Machine group already set:
./crear_linea.sh 3 3 http://192.168.1.XXX:8000 0
```

The lines do not have to be on the same computer or the same system: on
2026-09-24 one line on Windows and two on a Linux virtual machine worked at
the same time, all against the Windows website (see
[INSTALAR_WINDOWS.en.md](INSTALAR_WINDOWS.en.md), *Lines on other computers*).

Full step-by-step guide (what each part does, how many lines fit at
most, how to launch a line on another physical computer) in
[Documentacion/anadir_cadena_produccion.html](Documentacion/anadir_cadena_produccion.html).

---

## If something gets stuck (cubes piling up on the belt, both robots stopped)

_More known problems and their fixes: [PROBLEMAS_CONOCIDOS.en.md](PROBLEMAS_CONOCIDOS.en.md)._

This can happen if an arm gives up on a difficult cube after several
tries: until 2026-08-31 it could get stuck blocking its own camera
forever (already fixed — it now parks itself out of the way). If
something still goes wrong, the clean way to reset without losing
anything important is:

```bash
docker restart webots_panda_sim24   # puts the 3 cubes back in their usual spot
```
Wait about 8 seconds and redo steps **3, 4, 5** (and 6 if you were
using terminal production). Taller_Administracion's orders and stock
are NOT touched by this — only the simulation gets reset.

---

## Shutting everything down when you're done

**Shortcut:** `./cerrar_todo.sh` (stops both projects and warns if
something resists). It's the same as:

```bash
cd "Lab.Panda 2.4/.devcontainer" && docker compose down
cd ../../Taller_Administracion && docker compose down
```

---

## Emergency stop — quick reference

- **Physical buttons (one per robot, session 2026-09-01)**: both stop
  the ENTIRE cell (`/emergency_stop` is global, not per robot).
  - **Sorter**: GPIO16 to GND on the Pico W. Cuts the LED instantly
    (doesn't depend on the network) and notifies ROS over port 5002
    (wifi). **The bridge node (`button_listener`) is included in
    step 3** (since 2026-08-31, a real fix: the button "wasn't
    working" because this node used to be a separate manual step,
    easy to forget).
  - **Loader**: GPIO16 to GND on the USB Pico. Cuts the LED instantly
    just like the Sorter's, but with no wifi it notifies over the same
    USB cable (it prints `BOTON_PARADA`, which `led_publisher_usb`
    reads — step 4). Without that step running, this button doesn't
    notify ROS either.

  Both publish to `/emergency_stop`, the same topic already listened
  to by `teleop_gui`, `loader_demo` and `sorter_demo`. If a physical
  button doesn't stop the movement, the first thing to check is that
  step 3 (`button_listener`, Sorter) or step 4 (`led_publisher_usb`,
  Loader) is really running — without them, there's no bridge either.
- **HC-SR04 proximity sensor (Loader, session 2026-09-11)**: a third
  way to trigger the stop, without touching any button — if something
  gets closer than **10 cm** to the sensor, the Loader's Pico fires
  exactly the same path as its physical button (`BOTON_PARADA` over
  USB). Wiring and threshold in `Documentacion/cableado_hcsr04.html`;
  the threshold is `DISTANCIA_MIN_CM` in
  `Rasberry_Pi_Pico_USB_Loader/main.py`. If it triggers itself during
  normal production, it means the arm passes in front of the sensor:
  lower the threshold or relocate it, don't remove the alert.
- **From the panel**: `teleop_gui`'s STOP/RESET button (step 5) does
  the same thing without touching hardware — this is the recommended
  everyday way.
- **OLED screen (Loader, session 2026-09-18)**: shows as text the
  product currently being made (name, variant and code), the same
  thing the product LED says in colour but readable without learning
  the palette. SSD1306 128×64 over I2C (`SDA=GP4`, `SCL=GP5`),
  `teleop_gui` publishes it on `/texto_producto` and
  `led_publisher_usb` forwards it to the Pico over the same USB cable.
  Without a physical Pico, the panel's **Raspberry Pi Pico** tab
  simulates the same screen by listening to that topic. Full diagram
  in `Documentacion/PI_PICO_cableado_oled.html` — important: it needs
  `machine.SoftI2C`, the hardware I2C gives `OSError EIO` on write
  with this wiring even though the scan does find the screen.

**Resetting properly (a real gotcha, 2026-09-11):** sending `REARME` to
the LED topic (`/comando_led_loader` or `/comando_led`) only stops
that Pico's blinking; it does **not** clear `/emergency_stop`, so both
robots stay quietly stopped and it looks like the reset "doesn't
work". What actually resets things is `Bool(false)` on
`/emergency_stop` — which is exactly what the panel's RESET button
does. By hand you need all three publishes:

```bash
ros2 topic pub --once /emergency_stop std_msgs/msg/Bool 'data: false'
ros2 topic pub --once /comando_led_loader std_msgs/msg/String "data: 'rearme'"
ros2 topic pub --once /comando_led std_msgs/msg/String "data: 'rearme'"
```

During the stop the **panel's manual jog keeps working on purpose**:
the operator moves the arm (pulls it away from the sensor, frees a
stuck cube) and once reset the robot picks its work back up where it
left off.
- **`estop_panel.py`**: a separate window with just STOP/RESET, from
  before `teleop_gui` integrated them. It still works but is now
  redundant if you use the full panel; only useful if you want a
  panic button in a small separate window.

LED protocol over cable/wifi: one character per Pico —
`R`/`G`/`B`/`0` (off), plus `PARADA`/`REARME` for the emergency
blinking. Both Picos understand the same protocol, each on its own
channel (Wi-Fi port 5001 / USB serial).

---

## Additional technical documentation

Deeper reference pages, for anyone who wants the full technical detail
or the reasoning behind a specific decision, not just how to start
things up:

- [Documentacion/panel_control_manual.html](Documentacion/panel_control_manual.html)
  — the manual control panel (`teleop_gui`) explained tab by tab.
- [Documentacion/manual_tecnico.html](Documentacion/manual_tecnico.html)
  — the full technical history of Lab.Panda 2.4 + Taller_Administracion.
- [Documentacion/manual_usuario_avanzado.html](Documentacion/manual_usuario_avanzado.html)
  — an advanced usage guide, for anyone who already knows the basics.
- [Documentacion/boton_led_flujo.html](Documentacion/boton_led_flujo.html)
  — an early, standalone test of the physical stop button, before it
  was fully integrated (historical).
- [Documentacion/motores_panda.html](Documentacion/motores_panda.html)
  — how the Panda arm's joints are numbered and what each one does.
- [Documentacion/caras_cubo.html](Documentacion/caras_cubo.html) — which
  face sits opposite which on the belt's cubes (a reference for
  vision-based grasping).

---

## Appendix — old demos and worlds (single-robot project, NO LONGER used)

All of this predates the two-robot industrial cell. It still exists in
the code (in case something needs comparing or recovering), but **it's
not part of the current flow** — don't launch it thinking it's part of
the normal startup:

- Worlds: `panda_un_cubo.wbt`, `panda_bolas.wbt`
- Launch: `robot_launch.py` (a single robot, no namespaces)
- Demos: `stack_tower_demo`, `move_above_ball`, `pick_and_place`,
  `visit_balls`, `lift_ball`, `vision_lift_cube`,
  `best_color_repeat_lift`, `teleop_manual`
- Development tools for the current cell (also not part of normal
  startup, they were used to build it): `panda_two_arms_smoke_test.wbt`,
  `panda_sorter_grasp_test.wbt`, `grasp_yaw_test`, `sorter_hover_test`,
  `robot_launch_two_arms.py`, `robot_launch_sorter_grasp_test.py`.
