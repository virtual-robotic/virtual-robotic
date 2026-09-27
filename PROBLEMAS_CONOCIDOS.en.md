**Language:** [Español](PROBLEMAS_CONOCIDOS.md) · English · [Euskara](PROBLEMAS_CONOCIDOS.eu.md)

_Last modified: 2026-09-26_

# Known problems

Only what has really happened to us, with its fix. This is the **only
place** with the problems and their solutions: the guides link here.

The problems with **installing** on Windows (virtualisation, WSL, Docker
Desktop…) are in its guide: [INSTALAR_WINDOWS.en.md](INSTALAR_WINDOWS.en.md),
section "Problems we have really run into".

## Cell with robots (Linux)

**The controllers do not connect / Webots keeps loading the first time.**
It sometimes happens from cold. `arrancar_todo.sh` and `crear_linea.sh`
already try it by themselves with a `docker restart` of Webots. By hand:
`docker restart webots_panda_sim24 ros2_panda_dev24` and launch again.

**After relaunching, Webots says «Giving up» or «Address already in use».**
Controllers from the previous time were left running (a `pkill` of
`ros2 launch` does not kill its children). Fix: `docker restart` both
containers (Webots and ROS 2) and launch again.

**The finger of the Sorter's gripper breaks.** Re-arming does not help: you
have to restart Webots. On a slow computer it happened very often; since
2026-09-24 the robots time their waits with the simulation clock and it no
longer does (see *Windows*, below).

**There are repeated processes inside the ROS 2 container** (several
`button_listener`). It happened when relaunching the cell: the script killed
`ros2 launch` but not its children. Since 2026-09-24 the scripts restart the
container before launching.

**There is no room for Docker in a virtual machine.** The Webots and ROS 2
images take about 14 GB. If the virtual machine's disk has no more space,
the easiest and safest thing is to **give it a second disk just for
Docker**, without touching the system one:

1. Shut down the virtual machine.
2. In VirtualBox, create a new disk (40 GB is fine) and attach it to the
   machine. If VirtualBox does not let you, the *SATA* controller has no free
   slot: in the settings, raise its ports to 2.
3. Start the virtual machine and, inside it, make that disk the place where
   Docker keeps its things (the folders `/var/lib/docker` and
   `/var/lib/containerd`).

That is how we did it on 2026-09-24: step 3 is done by the project's
`vm_disco_docker.sh` script, run with `sudo`.

## Orders website

**It restarts non-stop («WatchFiles detected changes … Reloading»).**
It is the automatic reloading meant for programming. Since 2026-09-24 it
comes switched off; it is only switched on with `TALLER_RELOAD=1` in
`Taller_Administracion/.env`. On Windows, do not switch it on.

**No washers (or another product) show up in the warehouse.** It is not a
fault: each unit made is assigned straight away to the orders waiting for
it, so the stock stays at 0 while there are pending orders.

## Windows

**It is slow (Webots at 0.15x–0.22x on an old PC).** It is not that the
computer cannot do more: many times per second Webots waits for the robots,
which are inside Docker, to answer, and on Windows those messages travel
slowly. What weighed the most were the pictures from the two cameras that
look from above, which were sent non-stop. **Improved on 2026-09-25**
(10 pictures per second): on a laptop with Windows 11 one line went to the
same speed as reality (1x), and with **4 lines at once** each one runs at
0.35x–0.5x (0.18x before). How to change the pictures per second: see
[INSTALAR_WINDOWS.en.md](INSTALAR_WINDOWS.en.md).

**The Loader keeps wiggling its wrist non-stop at the start of a batch, and
the panel says the batch is still running.** Fixed on 2026-09-26. At the
start of each batch the robot wiggles its wrist for 5 seconds as a signal,
and it timed that badly if the batch started very quickly (it happened more
with several lines). With an older version: launch that line again. After
cutting a batch halfway, the panel takes **2 minutes** before it lets you
launch another one.

**The first time, Webots gets stuck at «Downloading assets 72 %».** It has
hung while downloading pictures for the scene from the internet. Close it
(if it does not respond, `cerrar_windows.bat` closes it) and launch again:
what was downloaded is kept, and the second time it loads.

**`git pull` fails because of a `.wbproj` file.** Webots rewrites those
files; since 2026-09-24 git no longer tracks them. If it happens with an old
clone: `git checkout -- "Lab.Panda 2.4/worlds/.panda_industrial_cell.wbproj"`
and `git pull` again.

**`git pull` asks for a user and the authentication fails.** Delete the
saved key with `cmdkey /delete:git:http://GITEA_IP:3000` and try again.

The installation problems (virtualisation, WSL that only shows its help,
«Catastrophic failure», `500 … _ping`, VirtualBox) are in
[INSTALAR_WINDOWS.en.md](INSTALAR_WINDOWS.en.md).
