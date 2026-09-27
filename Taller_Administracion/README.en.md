# Our orders website

If this is the first time you're seeing it: this is **the workshop's office**. Here
pieces get ordered, what's being made gets logged, what's left over gets kept
in the warehouse, it's handed over to the customer with its delivery note and
invoiced. The cell's robots (Loader and Sorter) are the real **workshop**;
this website is what tells them what's needed and logs what they're making.
You don't need to know anything about computing to follow this page: it's
told through a sample order, step by step.

> If this website is off, the cell keeps working exactly the same. The only
> thing that happens is that nobody logs the production against any order.

## An order's journey, start to finish

**🛒 It's ordered** → **🏭 It's obtained** (from the warehouse or by making it) → **✅ It's ready** → **🚚 It's delivered** (delivery note) → **🧾 It's invoiced**

An example: the company *Astilleros Murueta* needs 20 screws, 10 nuts and a
package of assorted pieces, and its Bilbao branch places the order.

### 1. Ordered with the basket 🛒

**Who orders.** A **user from a customer** places the order. Each customer
(for example, Astilleros Murueta) has an admin user and, if it wants, one per
**branch** (Bilbao, Barcelona, Madrid...). Whoever needs pieces opens the
website in their browser (in another tab or on another computer, it doesn't
matter), presses **Sign in** and enters their username and password; in the
example, Astilleros Murueta's `mur-bilbao` user. Once logged in they only see
the **Orders** tab, and the dropdown only shows the pieces their company is
allowed to order. Every order logs **which customer ordered it and which
user placed it**; the company's admin sees the ones from all its branches,
and the delivery note and invoice are issued to the **customer**, not the
branch.

It's like a shop: you pick a product **or a whole package**, say how many,
and put it in the basket. Once the basket is how you want it, you press
**Order the basket**. Everything in a basket travels together and comes out
**in a single delivery note**. An order for a single item is simply a
one-line basket.

![The Orders screen: at the top you pick the product or package, in the middle is the basket with three lines and below are the orders already under way, each with its status](img/web_1_pedir_cesta.png)

Below the basket, each order keeps changing state: *pending* (not started
yet), *in progress* (the pieces are being obtained), *ready for delivery*
(all of them are there, waiting to go out) and *delivered* (already handed
over).

### 2. It's obtained: from the warehouse or by making it 🏭

The first thing the system does is check the **warehouse**. If pieces are
already stored there, they get assigned to the order right away and nothing
needs to be made. If not, whatever's missing gets logged in **Workshop
Orders**, which is the robots' shopping list: the cell keeps making those
pieces and, as it finishes each one, notifies the website and the order
moves forward on its own.

![The Workshop Orders tab showing what's missing to make: 6 nuts and 10 washers](img/web_2_fabricar.png)

Here you can decide which machine makes each order, mark it as **urgent** or
cancel it.

![The two Panda robots working in the cell: the Loader on the left placing cubes on the belt, the Sorter above sorting them by colour](img/webots_cell.jpg)

Our production line, the one that makes those pieces, is explained in
[Our production line](/manual/panda).

### 3. It's ready and gets delivered 🚚

Once **all** the pieces of the order (of a basket, all of the basket's) are
there, the second stage arrives: **Delivery**. It's handed over to the
customer and logged with a **delivery note**, which is the proof of what was
delivered. It has two switches: one so stock only gets assigned to orders,
and another so whatever's already ready only gets delivered on its own.
With that second one off, everything waits here until someone presses
**Deliver**.

![The Delivery tab: the switches, the ready pieces waiting to be delivered and the delivery notes already issued](img/web_3_reparto.png)

A **package** is always delivered whole: if even a single piece is missing,
the package waits. And a basket waits until it's complete, so the customer
gets **a single delivery note** instead of three.

### 4. The delivery note 📄

This is the sheet that goes with the delivery. A package comes out as **one
package** (with its price) and below it, in small print, what's inside.

![Delivery notes issued: the top one carries two products and a package with its three components](img/web_4_albaran_emitido.png)

It can be viewed and printed (or saved as a PDF) with the company's logo,
the details of who's delivering and who's receiving, and the amount with its
VAT.

![The delivery note as printed: header with the logo, customer, the lines with their price and the total](img/web_5_albaran_papel.png)

### 5. It's invoiced 🧾

At the end of the month (or whenever it's due), a customer's delivery notes
that still haven't been billed get gathered into an **invoice**. You can tick
everything, tick a customer's, or pick delivery note by delivery note. If
there's a mistake, the invoice isn't edited: it's voided with another
**credit note** and the delivery notes become free to be invoiced again,
already corrected. You can invoice from several companies, each with its own
numbering.

![The Invoicing tab: each customer's delivery notes pending invoicing, with checkboxes to choose which ones to invoice](img/web_6_facturar.png)

## Who can do what

| Who logs in | What they see |
|---|---|
| **Normal user** (a customer's employee) | Only the **Orders** tab: orders with the basket and sees how theirs are going |
| **A customer company's admin** | The above for their whole company, plus their delivery notes and invoices |
| **System admin** (the workshop) | Everything: production, accounting and the base data (products, customers, prices...) |

## Things worth knowing

- **Prices freeze when you order.** If the rate changes tomorrow, orders
  already placed keep the price from when they were placed. Each customer
  can have their own prices.
- **Nothing gets deleted behind your back.** Any price or status change is
  logged: who, when and from how much to how much.
- **Stock isn't handed out behind your back.** There's an *automatic
  delivery* switch: on, stored pieces get assigned on their own to the
  orders that need them; off, they stay put until someone presses
  **Assign stock**.
- **You can play without worrying**: this is a learning project. The demo
  data is made up and the sample users' password is `1111`.

### Try it with the sample users

| You sign in as… | Password | You are… |
|---|---|---|
| `admin` | `admin` | The workshop: sees everything, sends orders to be made, delivers and invoices. It does not place orders. |
| `ere-admin` | `1111` | A sample customer: places orders and sees its own. |

### Adding parts to the warehouse by hand

In the **Warehouse** tab (workshop only), each product has the buttons
**«Add to stock»** and **«Remove from stock»**, for parts that do not come
from the robots: bought elsewhere, stock counts, returns. Each one is
recorded in *Movements* as «ajuste_manual» (manual adjustment). With
automatic delivery on, they are given by themselves to the orders they can
complete in full; if they only cover part of one, they wait for the robots
or for the **«Assign stock»** button in the **Delivery** tab.

---

**Want to know how it is built inside?** (routes, database, start-up, each
panel tab, automated tests…): it is in
[DETALLE_TECNICO.en.md](DETALLE_TECNICO.en.md).
