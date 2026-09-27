**Language:** [Español](README.md) · English · [Euskara](README.eu.md)

# Virtual Robotic

A personal hobby project, not a real company. It started out of curiosity
—wanting to understand how a real robot arm moves— and ended up as a
complete industrial cell: two arms that pick up and sort coloured cubes
along a conveyor belt, and a website that handles the orders as if it were
a real workshop.

![The two robot arms working over the belt, with coloured cubes and the computer vision camera windows](Virtual_Robotic/img/webots_cell.jpg)

**Videos of the cell at work** (30 seconds each; click the picture to watch it):

[![Video: the Loader puts the cubes on the belt and the Sorter picks them up and sorts them by colour](Virtual_Robotic/img/celda_trabajando_1.gif)](Virtual_Robotic/img/celda_trabajando_1.mp4)
[![Video: both arms working at the same time in the simulation](Virtual_Robotic/img/celda_trabajando_2.gif)](Virtual_Robotic/img/celda_trabajando_2.mp4)

## What is here

**1. The robot cell, simulated.** Two robot arms (the Franka Emika Panda
model) work inside **Webots**, a program that imitates real physics. One
puts cubes on a belt and the other picks them up and sorts them by colour,
checking with cameras that it really has picked up what it thinks. Under
the hood, the pieces talk to each other with **ROS 2**, the "nervous
system" used by almost every real robot.

**2. The orders website.** A normal website that acts as the workshop's
office: customers order, the robots make the parts, the warehouse keeps
itself up to date, and delivery notes and invoices come out. It is the
easiest part to try: it does not need the simulation.

**3. Two Raspberry Pi Pico boards, optional.** Tiny boards (about €5) with
LEDs, a proximity sensor, a small screen and real emergency stop buttons.
They are the bridge between the virtual and the physical, but **everything
works the same without them**: the control panel draws them on screen.

<img src="Virtual_Robotic/img/pico_hardware.jpg" alt="The two Raspberry Pi Pico boards on a breadboard, with a red and a blue LED lit, the small OLED screen at the bottom and the proximity sensor on the left" width="420">

Built together with **[Claude Code](https://claude.com/claude-code)**
(Anthropic): the design and much of the code came out of working sessions
with Claude.

## Try it in 3 steps (website only)

With [Docker](https://www.docker.com/) and Git installed:

```bash
git clone https://github.com/virtual-robotic/virtual-robotic.git
cd virtual-robotic/Taller_Administracion
docker compose up -d --build
```

Open **http://localhost:8000**. There you will find the presentation page,
which works as the project's manual, and the button to sign in. It already
comes with sample products and customers to play with. The website has a
language selector (Spanish, English, Basque).

### Who does what on the website

| You sign in as… | Password | You are… | You can… |
|---|---|---|---|
| `admin` | `admin` | The workshop | See everything, send orders to be made, deliver, issue delivery notes and invoices. **It does not place orders.** |
| `ere-admin` | `1111` | A sample customer (Ereño) | **Place orders** and see its own orders, delivery notes and invoices. |

To try an order from start to finish: sign in as `ere-admin`, place the
order, and then sign in as `admin` to see how it is delivered and invoiced.

## Where is everything?

| I want to… | Where |
|---|---|
| Install and start everything on **Linux** (with robots) | [LANZAR_PROYECTO.en.md](LANZAR_PROYECTO.en.md) — or `./arrancar_todo.sh` |
| Install and start it on **Windows** (with robots) | [INSTALAR_WINDOWS.en.md](INSTALAR_WINDOWS.en.md) — or double-click `arrancar_windows.bat` |
| Have **several lines** of robots at once | [Documentacion/anadir_cadena_produccion.md](Documentacion/anadir_cadena_produccion.md) (in Spanish) |
| Use the website: orders, warehouse, delivery, invoices | [Taller_Administracion/README.en.md](Taller_Administracion/README.en.md) |
| Assemble the Raspberry Pi Pico boards | [Documentacion/PI_PICO_montaje.html](Documentacion/PI_PICO_montaje.html) (in Spanish) |
| Fix something that goes wrong | [PROBLEMAS_CONOCIDOS.en.md](PROBLEMAS_CONOCIDOS.en.md) |
| Know how it is built inside | [Lab.Panda 2.4/detalle_tecnico_panda.md](Lab.Panda%202.4/detalle_tecnico_panda.md) (in Spanish) |

### Where it works today

| | Orders website | Cell with robots |
|---|---|---|
| **Linux** | Yes | Yes |
| **Windows** (a real PC) | Yes | Yes, with Webots installed on Windows |
| **Windows inside VirtualBox** | No | No (VirtualBox does not allow it) |

## What is in each folder

- `Lab.Panda 2.4/` — the simulation: Webots and the robots' program.
- `Taller_Administracion/` — the orders website and its presentation page.
- `Virtual_Robotic/` — the same presentation page, to open with a double
  click without Docker.
- `Rasberry_Pi_Pico/` and `Rasberry_Pi_Pico_USB_Loader/` — the program of
  the two Pico boards. `wifi_config.py` and `webrepl_cfg.py` are only
  templates: put your own keys there and **never upload them** (see
  [LANZAR_PROYECTO.en.md](LANZAR_PROYECTO.en.md), "Your Wi-Fi: the Pico W's credentials").
- `Documentacion/` — assembly guides and technical notes (in Spanish); you
  do not need to read them to get started.
- The loose files in the main folder (`arrancar_todo.sh`,
  `arrancar_windows.bat`, `crear_linea.sh`…) are the shortcuts to start
  and stop everything; each guide explains which one to use. The file and
  folder names are in Spanish.

## Licence

**MIT** (see [LICENSE](LICENSE)). In plain words: you can use, copy, change
and share this project as you like, even for something commercial, as long
as you keep the licence notice with the author's name. It comes as it is,
without warranty.

The third-party pieces the project uses (Webots, the Panda robot models,
ROS 2, FastAPI…) are not ours and keep their own licences.
