_Last modified: 2026-09-26 11:36_

# The orders website inside (technical detail)

For programmers. How to use it, with a sample order step by step, is in the
[website README](README.en.md).

Web server + order and warehouse database for the industrial cell. It's a
project **separate** from the cell: they only talk over HTTP. If it's off,
the cell keeps working, it's just that nobody logs the production.

Stack: FastAPI 0.115.0 + SQLAlchemy 2.0.35 + pydantic 2.9.2 + SQLite, served
by uvicorn (automatic code reloading is only switched on with
`TALLER_RELOAD=1` in `.env`). Interactive API at `/docs`.

## Routes served

- `/` — `app/static/landing.html`: the "Virtual Robotic" presentation web
  (same brand/typography as `../Virtual_Robotic/index.html`, but here the
  login is real because this same app is already running).
  The front page can be read in **Spanish, English and Basque** (ES/EN/EU
  selector at the top): the translated text lives in
  `app/static/i18n_landing.js` (and the copy under `../Virtual_Robotic/`).
  The orders system (`/panel`) and its manuals are still Spanish-only; the
  robots' control panel (`teleop_gui`) is already in all three languages.
- `/panel` — `app/static/panel.html`: the real system (orders, warehouse,
  users). Shares its session with `/` via `sessionStorage` (`taller_token`,
  `taller_yo`): log in once from the landing page and it never asks for
  login again.
- `/manual/{lanzar,taller,panda}` — serves the raw `LANZAR_PROYECTO.md`,
  this project's README and the `Lab.Panda 2.4` summary, linked from the
  landing page. It needs the `..:/workspace/repo:ro` volume from
  `docker-compose.yml` (the parent repo mounted read-only) — outside Docker
  it just falls back to the real path on disk (`TALLER_REPO_DIR`, two
  levels above `app/` by default).

## Starting it up

```bash
docker compose up -d --build
```

Publishes the host's port **8000**. `data/taller.db` gets created on its own
when it starts (inside the `./data` volume, ignored by git). The first time
it starts against an empty database, the server seeds (see `SEED_*` and
`sembrar_datos()` in `app/main.py`) sample data so you can play without
having to sign anything up by hand:

- 7 LED colours (R/G/B with a physical cube, Y/M/C/W LED-only), 3 products
  (Screws/100, Nuts/200, Washers/300) with their sub-products (10mm/20mm
  variants) and 2 sample packages (P010, P020).
- The **starting customers and users**, read from
  `Documentacion/UsuariosBBDDArranque.txt` (see "Starting customers and
  users" below), all with the full catalogue and the starting password
  `1111`. If that file doesn't exist, 3 sample companies from the code get
  seeded instead.
- User `admin` (`admin_sistema`, password `admin` by default — configurable
  with `TALLER_ADMIN_PASSWORD`).
- Warehouse configuration with `reparto_automatico = True` and
  `expedicion_automatica = True` (the two delivery switches, see "An
  order's cycle").
- Sample prices on the sub-products (in cents, without VAT; 21% VAT) so
  delivery notes come out with amounts from the very first start, and a
  sample issuing company (so you can invoice; change it under
  Administration → Companies).

### Starting customers and users

An **empty** database gets filled with the customers and users from
`Documentacion/UsuariosBBDDArranque.txt` (or whichever file
`TALLER_DATOS_ARRANQUE` points to). It's a text file edited by hand:

```
Cliente:
    R.S.: Astilleros Murueta S.L.        <- registered name; starts a customer
    Cod.: MUR                            <- OPTIONAL: 3-letter/digit code; without it, taken from the registered name
    Cif : B48111222
    Dir.: Carretera Bermeo 34
    C.P.: 48333
    Pob.: Murueta
    Pro.: Bizkaia
    cor.: administracion@example.com
    Productos: 100, Arandelas             <- OPTIONAL (code or name); without it, ALL
        sucursal admin -> Murueta         <- user  mur-admin   (the company's admin)
        sucursal -> Bilbao   nombre -> Ana López   <- user  mur-bilbao   (name OPTIONAL)
        sucursal -> Madrid                <- user  mur-madrid
```

- **The username is formed just from the customer's code and the branch**:
  `<code>-admin` for the company's admin (`admin_cliente`) and
  `<code>-<branch>` for each branch (`normal`). That way two customers can
  each have their own Bilbao branch (`mur-bilbao`, `ere-bilbao`) without
  making up names, and the username shows which customer an order comes
  from. Without `nombre ->`, the full name is "Administrator <branch>" or
  "Operator <branch>". The old form, with the username written by hand
  (`user normal-> bilbao2 sucursal -> Bilbao`), still works. Usernames are
  stored in lowercase.
- In the panel (**Administration → Customers**) the code is shown and can be
  changed (only by the system admin); when signing up a user, leaving the
  username empty still forms it the same way from the customer's code and
  branch. Customers from an old database just get a code, without their
  users being renamed.
- Everyone is born with the password **`1111`** (another one:
  `TALLER_PASSWORD_INICIAL`). The file **carries no passwords** and
  shouldn't: it goes into the shared git repo.
- An error (a malformed or repeated code, a repeated username, a customer
  with no `sucursal admin`, a product that doesn't exist…) **stops the
  startup**, naming the line, instead of loading things half-done.
  `tests/test_datos_arranque.py` and `tests/test_codigos_cliente.py` also
  check that the real file is valid.
- Only used with an **empty** database. To add whatever's missing to a
  database that already has data, without deleting anything (a customer
  with the same tax ID or a user with the same name gets skipped and
  listed):

  ```bash
  docker exec taller_admin_api python -m app.cargar_arranque
  ```

  To **move an old database over to code-based usernames**, add
  `--renombrar`: customers that already exist (same tax ID) get the code
  from the file and their users from the same branch and role get switched
  to the new name (`murueta` → `mur-admin`, `bilbao` → `mur-bilbao`);
  orders and delivery notes aren't touched.

With `TALLER_DEV_MODE=true` (the default in this repo's
`docker-compose.yml`) the master password (`TALLER_MASTER_PASSWORD`,
`1111` by default) works to log in as any of the sample users above, with
no need for their own passwords — meant exactly for cloning the repo on a
new machine and having something to play with from the very first start.

## Inside the panel (tab by tab)

![The panel with its two-level menu: the three sections at the top (Production, Accounting, Administration) and below them the tabs of the chosen section](img/panel_pestanas.png)

Once inside `/panel`, right at the top there are **three sections** and,
inside each one, its tabs:

| Section | Tabs (admin_sistema) | What happens there |
|---|---|---|
| **Production** | Orders · Workshop Orders · Delivery · Warehouse · Diagnostics | The day-to-day: ordering, making, storing and delivering pieces |
| **Accounting** | Summary · Rates · Invoicing | Prices, invoices, payments and how much is still owed |
| **Administration** | Company · Products · Sub-products · Packages · Colours · Catalogue · Users · Customers · Audit log | The base data: catalogue, customers, users and who invoices |

An `admin_cliente` sees the same three sections but cut down (Production:
Orders · Accounting: Summary, Delivery notes, Invoices · Administration:
Catalogue, Users). A `normal` user only has Orders and doesn't see the
section menu. Here's what each tab does, told without jargon:

- **Orders**: the day-to-day tab. You **always** order with the basket: pick
  a piece or a whole package and how many, **+ Add to basket**, and once
  it's how you want it, **Order the basket**. Everything in a basket is
  delivered together, in a single delivery note; an order for a single item
  is a one-line basket. The basket is saved in the browser until it's
  ordered. Once ordered, the cell starts making it on its own. As it
  progresses you see how many it's already made, whether there was stored
  stock covering part or all of the order without making anything new, and
  which machine is making it (if you have more than one production line).
  "Active" orders are the ones still not complete; "history" are the ones
  already finished or cancelled.
- **Products**: the catalogue of what gets made in general — "Screws",
  "Nuts"... Each product has a short code and, if you want, you can assign
  it a coloured LED: it's pure decoration (it lights up on the robot arm
  while it's making it) and doesn't affect production working at all.
- **Sub-products**: the specific variants of each product — within
  "Screws" you can have a "10mm screw" and a "20mm screw". This is what
  actually gets ordered, not the bare product.
- **Packages**: closed packs of several pieces at once, like "Pack of 10" =
  10 screws + 10 nuts + 10 washers. They don't hold their own stock:
  ordering a package simply creates a normal order for each piece it's
  made of.
- **Colours**: the catalogue of LED colours you can assign to a product.
  The ones marked "physical" really exist as a cube in the simulation; the
  rest are just decorative lights.
- **Catalogue**: here you decide which products each customer can order —
  if a product isn't ticked for one, that customer won't even see it in
  their order dropdown. This is a step you have to do: every new customer
  needs their catalogue assigned by hand (nothing is ticked by default), or
  even with users they still won't be able to order anything.
- **Users**: who can log in and what they can touch. The chain of command,
  at a glance:

  ```
  System admin  (you)
    └─ sees and touches EVERYTHING, for every customer

  Customer (company) ── logs in with its "Customer admin" account
    └─ signs up / edits / removes ITS Users (role "Normal")
         └─ each "Normal" User logs in with their own and places THEIR orders
  ```

  In other words: the customer logs in with its own admin account, manages
  its own people (users, branches) without needing anything from
  administration, and each of those users then logs in with their own
  account to order what they need. A "Customer admin" can't see or touch
  another company's users, nor create a new "System admin" — only
  administration can.
- **Customers**: the companies using the system. Each one lives in its own
  sealed compartment, never crossing paths with the others:

  ```
  Customer "Ferretería Ereño"        Customer "Suministros Mungia"
    ├─ its Users                       ├─ its Users
    ├─ its Catalogue (what it can order) ├─ its Catalogue
    └─ its Orders                      └─ its Orders

           -- nothing is seen or mixed between one and the other --
  ```

  Signing up a new customer here also creates its first "Customer admin"
  user at the same time — with that, it can already log in and set up the
  rest (its own users on the Users tab, its catalogue on the Catalogue
  tab) without administration having to do anything else.
- **Workshop Orders** (`admin_sistema` only): the orders **the warehouse
  can't cover** and that the workshop needs to be asked to make. Only
  what's still missing shows up; from here you assign a machine, mark it
  urgent or cancel it.
- **Delivery** (`admin_sistema` only): the second stage. Whatever's already
  ready (or covered by stock) and still needs **delivering to the
  customer**. Delivering issues a **delivery note** per customer. This is
  where the two automatic switches live, the "Assign stock to pending
  orders" button and the list of delivery notes issued.
- **Summary** (`admin_sistema` and `admin_cliente`): the accounts at a
  glance — invoiced this month and this year, collected, pending
  collection (by age), delivered without invoicing and, for
  administration, the breakdown per customer. Only valid invoices count.
  Includes "Download invoice ledger (CSV)" for the accountant.
- **Companies** (`admin_sistema` only): the companies that **issue
  invoices** — there can be several, each with its own registered name,
  tax ID, address and **own numbering** (series). One gets marked as
  default; a company isn't deleted, it's deactivated.
- **Rates** (`admin_sistema` only): the price each customer pays (a special
  rate or the general one), for products **and for packages**, plus the
  history of every price change.
- **Invoicing** (`admin_sistema` only): you choose which company invoices
  and see the delivery notes pending invoicing (with checkboxes to
  **select all** or **all of one customer**) (per customer or selected)
  and invoices already issued, with marking as paid, voiding (credit note)
  and viewing/printing.
- **Delivery notes** and **Invoices** (`admin_cliente` only): its
  deliveries and its invoices, read-only, with "View / print".
- **Warehouse**: the stock of already-made pieces and its movements. With
  **«Add to stock»** and **«Remove from stock»** pieces are added or removed
  by hand, without going through production (parts bought elsewhere, stock
  counts, returns); each one is recorded in Movements as «ajuste_manual».
  With automatic delivery on, the website hands them out by itself, within
  a few seconds, to the orders it can complete **in full**; if they only
  cover part of one, they wait for the robots or for the «Assign stock»
  button. Handing it out among orders is the
  **Delivery** tab's job: that's where the "Automatic delivery" switch is
  (with it on, free stock gets **assigned** on its own to pending orders
  and the pieces become ready) and the "Assign stock" button to do it by
  hand.
- **Diagnostics**: a technical look at how production is really going
  (pieces made, grip failures, reach limits...) — no need to check it for
  normal use, it's for when something goes wrong and needs investigating.
- **Audit log**: the who-did-what-and-when for every other tab, in case a
  history ever needs reconstructing.

Only `admin_sistema` sees all of these tabs in full; an `admin_cliente` or a
`normal` user see a cut-down version, with only what applies to them (see
"Roles" below).

## Model

Each **colour** is the product's identity (`Producto.color` is unique): the
cell only tells colours apart. R/G/B have a physical cube; Y/M/C/W are
product-LED-only colours (a wildcard mode), made with the three real cubes.

Tables: `clientes`, `usuarios`, `audit_log`, `colores`, `productos`,
`subproductos`, `paquetes`, `paquete_componentes`, `cliente_productos`,
`pedidos`, `stock`, `movimientos_stock` (an append-only log),
`eventos_produccion`, `configuracion_almacen` (a single row), `repartos` and
`reparto_lineas` (delivery notes), `tarifas_cliente`, `historial_precios`,
`emisores` (invoicing companies), `facturas` and `factura_lineas` (invoices
and credit notes).

### An order's cycle (2026-09-19)

An order goes through **two stages**, and each one has its own switch:

```
        workshop makes it                warehouse assigns it              delivery hands it over
 order ───────────────► FREE STOCK ─────────────────────► READY ─────────────────────► DELIVERED
        (cubo_clasificado)        reparto_automatico   (cantidad_completada)  expedicion_automatica   (delivery note)
```

| State | Means | Seen in |
|---|---|---|
| `pendiente` | Nothing ready yet | Orders, Workshop Orders |
| `en_proceso` | Something ready, the rest still missing | Orders, Workshop Orders and/or Delivery |
| `listo` | Everything ready, not delivered yet | Orders, Delivery |
| `completado` | **Delivered** (with a delivery note) | History |
| `cancelado` | Cancelled (only if it was `pendiente`) | History |

- `cantidad_completada` = pieces **ready** for the order (already left the
  free stock); `cantidad_repartida` = the ones already **delivered**
  (recorded on a delivery note). Always `repartida <= completada <= pedida`.
- `falta_fabricar` (what Workshop Orders shows) and `para_repartir` (what
  Delivery shows) are worked out on every query; an order with stock only
  covering part of it shows up in both tabs.
- Automatic dispatch only delivers **complete** orders (`listo`): if it
  delivered each loose piece there'd be a delivery note per cube. By hand,
  a half-finished order can be delivered too.
- **A package and a basket come out in ONE delivery note.** Ordering a
  package creates one order per component, and the **basket**
  (`POST /pedidos/multiple`: loose products and/or packages ordered at
  once) creates one per line; they all share `grupo_entrega`. With
  automatic dispatch they wait as `listo` until **the whole group** is
  ready and then they go out together, in a single delivery note (named
  after whichever packages it carries). With manual delivery, delivering
  one order from the group delivers the whole group. Everything is
  validated before anything gets created (either it all goes in, or none
  of it). Two baskets are two delivery notes. The panel only orders with a
  basket (a one-line basket is a loose order); `POST /pedidos` and
  `/pedidos/paquete` still exist in the API and their orders each go out
  on their own.
- **Stalled-stock sweep** (2026-09-20). Every 10s the server checks whether
  the free stock **fully** covers any open order and, if automatic
  delivery is on, assigns it (and, with automatic dispatch, it goes out as
  usual). Born from a real incident: piece 9 of 10 entered the warehouse
  without being assigned to its order, the cell saw it as "covered by
  stock" and stopped making more, and the order got stuck. Rules: only if
  the stock covers ALL of what the order still needs (an order that isn't
  fully covered doesn't block the following ones), ordered by urgency and
  age, and it leaves a trace in the audit log ("stock sweep: #…"). The
  14/09 rule (a piece from another machine doesn't complete my order
  *the moment it arrives*) still holds; the sweep only acts once nothing
  is left to make. `TALLER_BARRIDO_SEGUNDOS` (10 by default; 0 = off; the
  tests turn it off and call `barrer_stock()` by hand).
- **A package is delivered WHOLE** (user's decision, 2026-09-20): its
  products only go out once all of them are ready and always together,
  even by hand; a basket's loose products can go out half-finished, the
  package waits.
- `POST /reparto/expedir` (`admin_sistema` only) first assigns the free
  stock that covers the order and then delivers it, even if
  `reparto_automatico` is off: pressing Deliver is an explicit order.
- The cell **doesn't change**: it keeps reading `cantidad_completada`,
  `estado` and `stock_disponible`. A `listo` order isn't offered anything
  because nothing is missing any more.

### Price control and invoicing (2026-09-19)

How a price is tracked, from source to invoice (code in
`app/contabilidad.py`):

```
 GENERAL RATE (Sub-product)     ─┐
 or CUSTOMER RATE                ├─► ORDER (copies price + source) ─► DELIVERY NOTE (copies) ─► INVOICE (copies)
                                 ┘        tarifa_general | tarifa_cliente | manual
```

- **Rates.** The general price lives on the sub-product. A customer can
  have a **special rate** (*Rates* tab): without one, it pays the general
  price. Changing a rate only affects **new** orders; what's already
  ordered keeps its price.
- **Price history** (`historial_precios`, append-only). Every price
  change — general rate, customer rate, a correction to an order or a
  delivery-note line — stores who, when, from how much to how much, and
  the **reason** (required for corrections).
- **Corrections before invoicing.** An order not yet delivered can be
  corrected (`PATCH /pedidos/{id}/precio`, ends up with source *manual*);
  a delivery-note line not yet invoiced can too
  (`PATCH /repartos/lineas/{id}/precio`). The delivered quantity is never
  touched. A line already invoiced isn't corrected: the invoice gets
  voided instead.
- **Delivery note** (`repartos` + `reparto_lineas`): append-only, number
  `ALB-AAAA-nnnnnn`. **Prices in whole cents**, never `float`.
- **Invoice** (`facturas` + `factura_lineas`): groups ONE customer's
  **not-yet-invoiced** delivery notes (all of them, or the ones you pick),
  number `FAC-AAAA-nnnnnn`. It copies the lines, the price, the VAT and
  **both parties' tax details** (the issuer and the customer) at that
  moment: if the customer or the issuing company get edited afterwards,
  the invoice doesn't change. It requires the customer's tax ID and
  address and an active issuing company (Administration → Companies), and
  rejects lines at €0 unless explicitly confirmed.
- **Several issuing companies** (`emisores`). Each one has its own invoice
  and credit-note series (`FAC`/`RECT`, `TVR`/`RTVR`…), different from the
  others, and its own counter per year. The series can't be changed once
  it's already issued invoices. A credit note uses the credit-note series
  of the company on the original invoice.
- **Credit note.** An invoice is never edited or deleted: it gets
  **voided** by issuing its credit note (`RECT-AAAA-nnnnnn`, the same
  lines with a negative quantity, with a reason). The original ends up
  `anulada` and its delivery notes become free to be invoiced again,
  already corrected. Numbers are never reused.
- **Payment.** An issued invoice gets marked as paid (date and method).
- **VAT by rate.** Bases with the same percentage get added up and that
  group's amount is rounded **once** (half a cent rounds up, symmetric for
  negatives), like on a Spanish invoice. It's the same rule
  (`app/importes.py`) for delivery notes and invoices, so a delivery note
  and its invoice match to the cent. Base, VAT and total are **derived**
  from the lines (not stored).

Who can do what: `admin_sistema` manages rates, corrections, invoices,
payments and voidings; `admin_cliente` only **sees** its rates, delivery
notes and invoices (*Delivery notes* and *Invoices* tabs); `normal` sees
none of this.

What's **not** there (on purpose): equivalence surcharge and per-customer
VAT exemptions, periodic/automatic invoicing, partial payments or
remittances, emailing the invoice, configurable invoice series and
accounting exports (SII, Facturae). Each one can be added on top of this
model.

### Packages with their own price (2026-09-20)

A package can have **its own price** (`Paquete.precio_centimos`, per
package and without VAT, with its own `iva_porcentaje`); empty = **no own
price** and the sum of its products is charged, each at its own rate.

- **With its own price**, the delivery note and the invoice carry **one
  package line** (`tipo = paquete`, with a package quantity and price) and
  below it, **with no price**, what it contains (`tipo = componente`). A
  priced package's products come out at €0 on the order on purpose: the
  price lives on the package and neither the delivery note nor the invoice
  rejects those lines ("€0 lines"). The components' VAT is the package's,
  so the breakdown doesn't produce an empty VAT row.
- **With no own price**, the lines are the usual ones (`tipo = normal`)
  but carry `paquete_pedido_id` and the package's name, to group them when
  displaying them.
- **`PedidoPaquete`** (`pedidos_paquete`) is ONE ordered package: how many,
  and its price and source (`paquete_general`, `paquete_cliente` or
  `manual`) **frozen** when ordered. Its products are normal orders with
  `paquete_pedido_id`. Changing the package's price afterwards doesn't
  touch what's already ordered.
- **Per-customer rate for packages** (`tarifas_cliente_paquete`, *Rates*
  tab), just like the one for products. Every package price change is kept
  in `historial_precios` (`paquete_general`, `paquete_cliente`,
  `pedido_paquete`; they carry `paquete_id` instead of `subproducto_id`).
- **Corrections:** an ordered package's price, not yet delivered, is
  corrected with `PATCH /pedidos-paquete/{id}/precio`; a loose product's,
  as always. A priced package's product isn't corrected separately (409).
  On a delivery note, the package's line gets corrected
  (`PATCH /repartos/lineas/{id}/precio`); a component's gives 400.
- An invoice's credit note for a package is exactly its negative, package
  lines included.

**When updating an old database:** this change makes
`historial_precios.subproducto_id` and
`reparto_lineas.pedido_id/subproducto_id` nullable, and SQLite doesn't
allow dropping a `NOT NULL` with `ALTER`. `migraciones.py` detects this and
**warns in the log**, but the fix is recreating the database
(`data/taller.db`): it gets refilled with the customers from the starting
file. A database that no longer accepts those NULLs only fails when
setting a package price or delivering a package with its own price.

### Migrations

There's no Alembic. On startup, `app/migraciones.py` compares each table
against the model and runs `ALTER TABLE ... ADD COLUMN` for **new**
columns, so an additive change to the model no longer forces deleting
`data/taller.db`. It only adds (never renames, never changes types, never
deletes) and a `NOT NULL` column needs a default value; whatever it can't
do gets logged as a warning. The seed's sample values (prices, issuer) are
only seeded into an **empty** database.

## Roles

- `admin_sistema`: everything. The only one who manages products,
  customers, the warehouse, diagnostics and the audit log.
- `admin_cliente`: manages its own company (its own users, assigned
  catalogue, its company's orders).
- `normal`: places orders and sees its own.

The master password (`TALLER_MASTER_PASSWORD`, `1111` by default) always
works to log in as a `normal` user — meant so that anyone who just wants to
"play" with the panel doesn't need to be given an account. For
`admin_sistema`/`admin_cliente` the master password **only** works if
`TALLER_DEV_MODE=true` (on in our local `docker-compose.yml`); without that
flag the account's real password is needed. The seeded `admin` user always
has a real password (`admin` by default), so it works with or without
`TALLER_DEV_MODE`.

## `POST /taller/cubo_clasificado`

The event the cell sends every time a cube reaches its box. It **always**
responds `200` and adds 1 to that colour's stock. If automatic delivery is
on (the only switch for assignment), it also **assigns** that unit to a
pending order (it ends up as a *ready* piece for it): the one named in
`pedido_id` if it's still open, otherwise the most urgent and oldest order
for that product. With `expedicion_automatica` on, if that piece completes
the order it goes out on its own with its delivery note; if not, it stays
`listo`, waiting in Delivery. (Earlier versions of this document said it
returned 404 if there was no pending order: that's false, it always
returns 200 with `pedido: null` in that case.)

**It never hands out stock to orders on its own initiative** outside this
rule: `/almacen/repartir` (assigning stock) and `/reparto/expedir`
(delivering) are the operator's decisions.

## Endpoints

See `/docs` (Swagger generated by FastAPI) for the full list with input and
output schemas.

## Automated tests (2026-09-11, extended 2026-09-19)

261 tests with pytest + FastAPI's `TestClient`, covering login/roles,
products, customers/users and their permission boundaries, orders
(creating, scope per role, cancelling, **reprocessing**), warehouse
(`reparto_automatico` as the only gate, `cubo_clasificado`, FIFO delivery
of `stock_disponible`, adjusting/removing stock), processing times,
diagnostics and the audit log, and (`tests/test_reparto.py`) the
ready → delivered cycle, delivery notes, frozen prices and VAT, and
(`tests/test_contabilidad.py`, `tests/test_migraciones.py`) rates,
history, corrections, invoices, credit notes, payments, permissions and
the column migration.

**Never touch `data/taller.db`**: `tests/conftest.py` sets
`TALLER_DB_PATH` to a temporary file *before* importing anything from
`app` (the variable is read at import time in `database.py`), and every
test starts with a clean, freshly seeded database.

```bash
docker exec taller_admin_api pip install -r requirements-dev.txt   # once
docker exec -w /workspace taller_admin_api python -m pytest -v
```

Two of the tests document real regressions from the 2026-09-11 session so
they don't happen again unnoticed: the error message when cancelling a
non-pending order (it broke to `"c/p ya fabricadas"` during a rewrite) and
the silent behaviour of `POST /usuarios` when an `admin_cliente` tries to
slip a user into another company (it doesn't give 403: it ignores the
`cliente_id` it received and forces its own).
