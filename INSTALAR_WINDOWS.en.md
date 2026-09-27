**Language:** [Español](INSTALAR_WINDOWS.md) · English · [Euskara](INSTALAR_WINDOWS.eu.md)

_Last modified: 2026-09-26_

# Installing on Windows

> **Really tested on 2026-09-23** on a physical PC with Windows 10 22H2 (Intel): clean install from the public repo, `docker compose up -d --build` and the website at `http://localhost:8000` working, with no errors at start-up.

This guide covers **the orders website** (`Taller_Administracion`), tested
and working, and at the end **the cell with the robots**, which **works on
Windows since 2026-09-24**: see
[The cell with the robots on Windows](#the-cell-with-the-robots-on-windows).
On Linux it is started as always (see [LANZAR_PROYECTO.en.md](LANZAR_PROYECTO.en.md)).

> **On Windows you never run `arrancar_todo.sh`**, which is for Linux. For
> the website alone `docker compose` is enough; for everything,
> `arrancar_windows.bat`.

The file and folder names of the project are in Spanish; this guide keeps
them as they are.

## Before you start: is your Windows suitable?

Docker Desktop needs **WSL 2**, which in turn needs **Hyper-V**, which in
turn needs the processor to have **virtualisation enabled**. That gives the
two cases to check before wasting time:

| Where your Windows runs | Does it work? |
|---|---|
| Physical PC | **Yes**, enabling virtualisation in the BIOS if needed |
| VirtualBox virtual machine | **No**, and there is no fix (see below) |

### Checking virtualisation

**Ctrl+Shift+Esc** (Task Manager) → **Performance** tab → **CPU**. Look for
**Virtualisation**: it must say **Enabled**.

If it says *Disabled*, it is enabled in the BIOS:

1. Restart and enter the BIOS by repeatedly pressing **F2** or **Del** right
   after switching on (depending on the computer it can be **F1**, **F10**
   or **Esc**; the start-up screen usually says which).
2. Find the option and set it to **Enabled**:
   - **Intel:** `Intel Virtualization Technology` or `VT-x`.
   - **AMD:** `SVM Mode` or `AMD-V`.

   It is usually under **Advanced → CPU Configuration**; on laptops it is
   sometimes under **Security** or **Configuration**.
3. Save and exit (usually **F10**).

## If `wsl` only shows you the help screen

It happens on a freshly installed Windows 10: `wsl --install`, `wsl --update`
and even `wsl -l -v` answer with the list of options instead of doing
anything. **It is not a syntax error**: it means the Windows features for
WSL are not enabled. They are enabled by hand, in PowerShell **as
administrator**:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Each one must end with *The operation completed successfully*. Then
**restart** Windows and download the kernel with `wsl --update --web-download`
(see below). One more restart, and Docker Desktop can be opened.

## Installation

1. **Docker Desktop for Windows**, from [docker.com](https://www.docker.com/products/docker-desktop/),
   leaving the *Use WSL 2* option ticked. Restart the PC when it asks.
2. Open Docker Desktop. If it asks you to sign in, **no account is needed**:
   look for the small *Skip* or *Continue without signing in* link.
   Wait until the bottom left says **Engine running**.
3. **Git for Windows**, from [git-scm.com](https://git-scm.com/download/win)
   ("Next" to everything is fine).
4. **Webots** (only if you also want the robots; for the website alone it
   is not needed):
   - Download the installer directly from here:
     [webots-R2025a_setup.exe](https://github.com/cyberbotics/webots/releases/download/R2025a/webots-R2025a_setup.exe)
     (about 250 MB). It must be **exactly version R2025a**, the same one the
     project uses; do not take a newer one.
   - Open it. When it asks who to install it for, choose **only for me**
     (*Install for me only*): that way it does not ask for administrator
     rights.
   - Leave the other options as they are and finish the installation.
   - There is no portable (non-installed) version for Windows.
5. **Download the project.** In PowerShell, in the folder where you want it
   (for example `C:\carga`):

   ```powershell
   git clone https://github.com/virtual-robotic/virtual-robotic.git
   ```

6. **Start it**, in one of these two ways:
   - **Only the orders website:**

     ```powershell
     cd virtual-robotic\Taller_Administracion
     docker compose up -d --build
     ```

     The first time it takes a while, because it builds the image. To stop
     it: `docker compose down` in that same folder.
   - **Everything, with the robots:** with **`arrancar_windows.bat`** (see
     how to launch it just below, and what it does in
     [The cell with the robots on Windows](#the-cell-with-the-robots-on-windows)).
     To stop everything: **`cerrar_windows.bat`** (it also closes Webots).

   **How to launch a `.bat` file**, either way:
   - **With the mouse:** open the project folder (`virtual-robotic`) in File
     Explorer and **double-click** `arrancar_windows.bat`. A black window
     opens and tells you what it is doing; **do not close it** until at the
     end it says *«Press any key to continue»*.
   - **From PowerShell**, inside the project folder:

     ```powershell
     .\arrancar_windows.bat
     ```

   The same for shutting down, with `cerrar_windows.bat`. If Windows warns
   that the file may be dangerous, it is because it comes from the internet:
   press *More info* → *Run anyway*.
7. Open the website at `http://localhost:8000` and sign in with **admin** /
   **admin**. If you also started the robots, the **control panel** opens by
   itself in the browser (`http://localhost:6080/vnc.html`) and Webots in its
   own window.

   With `admin` **you cannot place orders**: `admin` is the workshop (it
   delivers and invoices). To order, sign in as a customer, for example
   **`ere-admin`** with password **`1111`**. More details in the README,
   "Who does what on the website".

Run the commands from **your own PowerShell window**, not over SSH or from
a service: Docker keeps its credentials in the Windows Credential Manager
and, outside your session, it fails with *«A specified logon session does
not exist»*.

## Problems we have really run into

Only the **installation** ones here. The ones that happen once everything
is running (robots that do not connect, it is slow, `git pull` fails…) are
in [PROBLEMAS_CONOCIDOS.en.md](PROBLEMAS_CONOCIDOS.en.md).

### «Virtualization support not detected»

Docker Desktop cannot find virtualisation. Two possible causes:

- **On a physical PC:** it is disabled in the BIOS. See *Checking
  virtualisation*, above.
- **Inside VirtualBox:** there is no solution. See the next section.

### Windows inside VirtualBox: it cannot be done, and it is not your fault

**Docker Desktop cannot work with Windows installed in VirtualBox.**
WSL 2 needs Hyper-V, and **VirtualBox does not support Hyper-V as a nested
hypervisor** ([Oracle documentation](https://docs.oracle.com/en/virtualization/virtualbox/6.0/admin/nested-virt.html)).

We tested it thoroughly on 2026-09-23 before giving up: not by enabling
nested virtualisation (`VBoxManage modifyvm "<VM>" --nested-hw-virt on`),
nor by going up to 8 GB of RAM and 6 processors, nor by removing the
paravirtualisation provider. The technical reason is in the VM's own log
(`Logs/VBox.log`): in the line `Gst: 8000000a/...`, which is the CPUID of
virtualisation features that VirtualBox offers the guest, the EDX value is
`0x000000c8` — **bit 0 (nested page tables, NPT) is zero**, and the Windows
hypervisor requires that feature to start.

Watch out for a misleading detail: inside that VM, Windows answers
`HypervisorPresent = True` and `VirtualizationFirmwareEnabled = True`. That
«True» is **misleading** — it belongs to the paravirtualisation interface
that VirtualBox itself announces, not to the Windows hypervisor.

**It does not depend on whether the computer is AMD or Intel.** The
limitation is VirtualBox's, not the processor's: we tried it on an AMD, and
on an Intel the same would happen (there that feature is called EPT instead
of NPT, but VirtualBox does not let Windows use it either).

To try it on Windows you need a **real Windows PC**.

**An alternative, not tested yet:** on a Linux computer, use **KVM** (the
*virt-manager* program) instead of VirtualBox for the Windows virtual
machine. KVM does pass that feature on to Windows, so Docker Desktop should
start inside. That said, the 3D part of a virtual machine is still weak for
Webots.

### `wsl --install` ends in «Catastrophic failure»

It happens when installing or updating WSL, usually because the download
goes through the Microsoft Store. Restart Windows and use the way that
skips it (it downloads the component from GitHub):

```powershell
wsl --update --web-download
```

Afterwards, `wsl --status` must not complain that the kernel is missing.

### `500 Internal Server Error ... dockerDesktopLinuxEngine/_ping`

It only means that **the Docker engine is not running**; the project has
nothing to do with it. Open Docker Desktop, wait for *Engine running* and
repeat the command.

### The website restarts non-stop and does not respond

If in the log (`docker logs taller_admin_api`) you see over and over
*«WatchFiles detected changes … Reloading…»*, it is the **automatic
reloading** of the code, meant only for whoever is programming it. On
Windows the timestamps of mounted files jump around and the reloading goes
into a loop. Since 2026-09-24 it **comes switched off by default**; it is
only switched on if you put `TALLER_RELOAD=1` in
`Taller_Administracion/.env`. On Windows, do not switch it on.

## The cell with the robots on Windows

> **Tested on 2026-09-24** on the same PC with Windows 10: Webots R2025a
> installed on Windows, the 6 controllers connected from Docker, and the
> control panel in the browser moving the robots. It is the first test: it
> still needs to be used for a long while.

**How it is put together.** Webots is **installed on Windows itself** (the
Docker one needs a Linux screen, which Windows does not have, and dies with
*«could not connect to display»*). Only **ROS 2** goes in Docker, and it
reaches that Webots over the network. The **control panel** appears in a
**browser tab**, because it is also a Linux window.

**What to install:** the same as for the website, plus **Webots** (step 4
of the [Installation](#installation)).

**Starting:** double-click **`arrancar_windows.bat`**, in the project's main
folder. In order, it:

1. Checks that Docker Desktop is running.
2. Starts the orders website.
3. Starts the ROS 2 container (with
   `Lab.Panda 2.4/.devcontainer/docker-compose.windows.yml`) and compiles.
   The first time it takes a good while: it downloads an image of several GB.
4. Opens Webots with the cell's world and waits until it accepts
   connections. The first time Webots downloads textures; if the **Windows
   Firewall** asks, **allow it** on private networks.
5. Launches the cell and waits for the 6 controllers.
6. Opens the panel in the browser: `http://localhost:6080/vnc.html`.

**Shutting down:** `cerrar_windows.bat`. Since 2026-09-26 it also closes the
Webots window. Nothing needs saving: when you start again, the cell starts
from scratch as always.

**If the first time Webots appears without robots** (and looking odd,
without textures): it is downloading the models from the internet and the
world opened before it had them. Close Webots and launch
`arrancar_windows.bat` again; the second time it already has them (it
happened to us on 2026-09-24). Do not use *Reload World*: it closed Webots
on us.

**Things still to watch:**

1. **On an old PC it is slow.** On a 2012 laptop the simulation runs at
   **0.15x–0.22x**, that is, between 5 and 7 times slower than reality. That
   number is shown in Webots' top bar, next to the clock.

   It is not that the computer cannot do more: Webots hardly works. What
   slows it down are the messages between Webots and the robots, which are
   inside Docker, and above all **the pictures from the two cameras**, which
   travelled at every step of the simulation (31 per second). **Improved on
   2026-09-25**: now they send 10 per second, which is more than enough for
   the robots to see the cubes. On a modern laptop with Windows 11,
   production almost doubled (from one cube every 43–49 seconds to one
   every 24) and the simulation runs at the same speed as reality (1.0x).

   *If you want to change it:* it is the two files of the top cameras,
   `overhead_camera.urdf` (the Loader's) and `overhead_camera_sorter.urdf`
   (the Sorter's), in the folder
   `Lab.Panda 2.4/ros2_ws/src/panda_controller/resource/`. The number is in
   the line `<updateRate>10</updateRate>`: those are the pictures per
   second. Fewer pictures, the faster everything goes, but the robots see
   with more delay. It works the same on Linux.

   Before, at that speed, **the Sorter's gripper finger broke** very often.
   **It is now fixed** (2026-09-24): the robots now count time with the
   Webots clock and not with the computer's, so even when everything is
   slow, they move properly. If it still breaks, re-arming is not enough:
   close Webots and launch `arrancar_windows.bat` again.

   **Fixed on 2026-09-26: the Loader kept "dancing" endlessly** at the start
   of a batch, and the panel kept saying the batch was running. At the
   start of each batch the robot wiggles its wrist for 5 seconds as a
   signal; it timed that badly if the batch started very quickly, and the
   dance never ended. It happened more with several lines. If it happens to
   you with an older version, launch that line again (`arrancar_windows.bat`,
   or `crear_linea_windows.bat` with its number). Note: after cutting a batch
   halfway, the panel takes **2 minutes** before it lets you launch another
   one (it waits in case a part is still on its way).
2. In the browser panel, to type in a small window (e.g. the *Settings*
   key), **click inside the box** before typing.
3. The Raspberry Pi Pico over USB: on Windows it does not reach the
   container, so the Loader's LED will not work (the rest will; the Pico is
   optional).

**Why the code does not need touching.** In our world **all the
controllers are `<extern>`**: Webots does not run them, they connect from
outside, over TCP to port 1234. The `WEBOTS_SHARED_FOLDER` variable does not
share any folder: it only makes the ROS 2 connector use TCP towards
`host.docker.internal`, which Docker Desktop on Windows points at Windows
itself. (It also spares us a known fault of the connector with WSL: it is
in the other branch of the code, the one we do not use.)

### Several lines on the same Windows

**Tested on 2026-09-25 with 4 lines at once** on a laptop with Windows 11.
Each line has its own Webots, its own ROS 2 container and its own panel:

| Line | Webots on port | Panel in the browser |
|---|---|---|
| 1 | 1234 | `http://localhost:6080/vnc.html` |
| 2 | 1235 | `http://localhost:6081/vnc.html` |
| N (up to 9) | 1233+N | `http://localhost:` 6079+N |

- **Line 1 first**, with `arrancar_windows.bat` as always.
- **To add another:** double-click **`crear_linea_windows.bat`**. It asks
  for the line number (2 to 9) and its machine number (which must not
  repeat another line's). It opens its own Webots and its own panel.
- **To shut down just one:** `cerrar_windows.bat 3` (from PowerShell, in the
  project folder): it stops that line and closes its Webots; the others keep
  going. Without a number, `cerrar_windows.bat` shuts down all the lines,
  their Webots and the website.
- **Without questions:** `arrancar_windows.bat 3 30` does the same as
  `crear_linea_windows.bat` for line 3 with machine number 30. The number
  can be left out and set later in the panel's *Settings* tab. Without any
  number, `arrancar_windows.bat` starts line 1.
- They all work for **the same orders website**.

**How much the computer can take.** Tested on 2026-09-26 on that laptop
(Windows 11, 30 GB of memory), with the 4 lines making parts at once:

| | Before (cameras at 31 pictures/s) | Now (cameras at 10 pictures/s) |
|---|---|---|
| Speed of each line (1x = like reality) | 0.18x | between 0.35x and 0.5x |
| Each line makes a cube every… | — | ~57 seconds |
| Processor / graphics card load | 60 % / 55 % | 77 % / 73 % |

With 4 lines the laptop is already fairly loaded: **4 is a good ceiling**. A
fifth would slow all of them down.

**When it opens, Webots shows only the 3D view** (without the editing
panels), so that several windows fit. If you want to see a panel, it is in
the *View* menu.

### Lines on other computers, working for the Windows website

Another way of having more lines, **tested on 2026-09-24**: the website and
one line on the Windows PC, and **two more lines on another computer with
Linux** (a Linux Mint virtual machine), the three of them working for the
**same orders website**. On the Linux computer, each line is created
pointing at the Windows website:

```bash
./crear_linea.sh 3 33 http://WINDOWS_IP:8000
./crear_linea.sh 4 34 http://WINDOWS_IP:8000
```

- Each line needs its own **machine number** (here 10 for the Windows one,
  33 and 34 for the Linux ones), so that the orders do not get mixed up.
- The Windows Firewall has to let port 8000 in; you can check it by opening
  `http://WINDOWS_IP:8000` from the Linux computer.
- A virtual machine with 4 processors and 6 GB of RAM runs two lines, but
  at its limit. The images need about 14 GB of disk: if they do not fit,
  see [PROBLEMAS_CONOCIDOS.en.md](PROBLEMAS_CONOCIDOS.en.md) (adding a second
  disk for Docker).
