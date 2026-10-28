# Office Point – Invoice Generator

A free invoice app for Office Point (Sim Distributors Ltd) that runs entirely in your web browser.
It makes A4 VAT invoices as PDFs, either one at a time (**Manual entry**) or in bulk from a CSV
export of your Amazon, eBay, TikTok Shop, Temu, OnBuy, Etsy, Tesco, Joybuy or website orders
(**CSV bulk upload**).

Nothing is uploaded anywhere. Your orders stay on your computer. The app is a single file; it needs an internet
connection when the page opens so it can load its PDF and ZIP libraries from a public CDN.

```
invoice-app/
├── index.html          ← the whole app (open this)
├── sample-orders.csv   ← example CSV in the right format
└── README.md
```

---

## 1. How to run it

1. Save `index.html` anywhere on your computer (or copy the code into a new text file and save it as `index.html`).
2. **Double-click `index.html`**. It opens in your default browser. Chrome, Edge, Firefox and Safari all work.
3. Optional: bookmark the page, or make a desktop shortcut to `index.html`.
4. Optional: in **Settings → Logo on invoices**, choose your Office Point logo image (PNG or JPG). Until you
   do, "Office Point" is written in the brand greens.

You don't need to install anything, run a server or have an account.

> **Tip:** if your browser asks where to save each download, turn on
> *Settings → Downloads → Save files without asking* (Chrome/Edge) so bulk downloads are one click.

---

## 2. Mode A – Manual entry

1. **Invoice details** – the invoice number fills in automatically (see *Settings*). Pick the date
   and type the Order ID. Choose a sales channel if you want it printed on the invoice.
2. **Bill to** – client name and billing address, one line per row. The optional *Notes* line
   is printed on the invoice (e.g. "Paid in full – thank you").
3. **Items** – description, quantity, unit price and VAT rate (20% by default; 5% and 0% are in the list).
   Click **Add item** for more rows. Each row shows its Net, VAT, unit price incl. VAT and line total
   as you type.
   - The **Excl. VAT / Incl. VAT** switch sets how the prices you type are read. Use *Incl. VAT* when
     you know what the customer paid; the VAT is then worked out backwards.
4. **Shipping** – the shipping price and its VAT rate (20% by default, as for UK delivery of standard-rated goods).
5. Check the live preview on the right, then click **Download PDF**.

**New invoice** clears the form and moves on to the next number. Your work in progress is saved in the
browser, so closing the tab doesn't lose it.

## 3. Mode B – CSV bulk upload

1. Open the **CSV bulk upload** tab.
2. Drag your CSV onto the box, or click it to choose the file.
3. Set the three options:
   - **Prices in my CSV are** – *Excl. VAT* or *Incl. VAT*. Marketplace exports (Amazon, eBay, TikTok,
     Etsy …) normally show the price the customer paid, which **includes VAT**.
   - **Shipping column is** – *Per order* (the order's shipping appears once, or the same value is on every
     row) or *Per item row* (each row has its own shipping charge, as in Amazon order reports; they are
     added up).
   - **Channel** – printed on every invoice when the CSV has no Channel column.
4. Check the list. Click any order, or use **‹ ›** or the ← → keys, to preview it. Orders marked **⚠** have
   something to look at, such as a missing name or a price that isn't a number. The reason is shown above the list.
5. Download:
   - **Download all (ZIP)** – one PDF per order in a single ZIP file.
   - **One PDF for printing** – every invoice in one PDF, each starting on a new page.
   - **This PDF** – just the order you're looking at.
   - **Edit this one** – copies the order into Manual entry so you can change it before downloading.

Orders without an invoice number in the CSV are numbered automatically, carrying on from your last number.

---

## 4. CSV format – the exact column headers

Use **one row per item**. Give every row of a multi-item order the same Order ID, and the rows become one invoice.

### Required columns

```
Order ID,Customer Name,Address,Item,Qty,Price,Shipping
```

| Column | What to put in it |
|---|---|
| `Order ID` | The marketplace order number. Rows with the same Order ID become one invoice. |
| `Customer Name` | Name printed under **Bill To**. |
| `Address` | Full billing address. Separate lines with commas and wrap the whole thing in "double quotes" (Excel does this for you). |
| `Item` | Item description. |
| `Qty` | Quantity. Blank = 1. |
| `Price` | **Unit price** (price for one item). Excl. or incl. VAT according to the switch in the app. |
| `Shipping` | Shipping charge for the order. Put it on the first row; leave later rows blank or the same. |

### Optional columns (add any you have)

```
VAT Rate,Invoice Number,Invoice Date,Channel,Notes,Address 2,City,County,Postcode,Country,Line Total
```

| Column | What it does |
|---|---|
| `VAT Rate` | `20`, `5`, `0` (or `20%` / `0.2`). Blank = default rate (20%). |
| `Invoice Number` | Use your own number instead of the automatic one. |
| `Invoice Date` | `2026-10-28` or `28/10/2026` (UK day/month order). Blank = today. |
| `Channel` | Amazon, eBay, TikTok Shop, Temu, OnBuy, Etsy, Tesco, Joybuy, Website … |
| `Notes` | Printed in the Notes box on the invoice. |
| `Address 2`, `City`, `County`, `Postcode`, `Country` | Added to the address as extra lines, for exports that split the address up. |
| `Line Total` | Price × Qty. Used only when there is no `Price` column; the unit price is then Line Total ÷ Qty. |

### Sample (`sample-orders.csv`)

```csv
Order ID,Customer Name,Address,Item,Qty,Price,Shipping,VAT Rate,Invoice Date,Channel
84724,Khia Mistry,"83 Baker Street, London, W1U 6AG, United Kingdom",Navigator Universal A4 Paper 80gsm Box (5 Reams),8,23.90,0,20,2026-10-27,Amazon
85069,Matt Mela (Boulevard Brasserie),"40 Wellington St, London, WC2E 7BD, United Kingdom",Color Copy A3 Printer Paper 250gsm Ream - 125 Sheets,20,14.574,4.99,20,2026-10-27,eBay
85070,Jane Doe,"Flat 2, 12 High Street, Reading, RG1 2AB, United Kingdom",HP 305 Black Original Ink Cartridge,2,12.49,3.95,20,2026-10-28,TikTok Shop
85070,Jane Doe,"Flat 2, 12 High Street, Reading, RG1 2AB, United Kingdom",Pukka Pad A4 Refill Pad 400 Pages,3,4.15,,20,2026-10-28,TikTok Shop
85071,Acme Dental Ltd,"Suite 4, The Courtyard, Bristol, BS1 4DJ, United Kingdom",Fellowes Shredder Oil 350ml,1,6.66,2.49,20,28/10/2026,Etsy
```

Order `85070` has two rows, so it becomes **one invoice with two items**. You can also click
**Sample CSV** in the app to download this file.

### Using a marketplace export directly

You don't have to rename columns. The app recognises many common names. Case, spaces, hyphens and
underscores are ignored, so `order-id`, `Order Number` and `ORDER_ID` all count as **Order ID**. Some examples:

| App field | Also recognised |
|---|---|
| Order ID | `order-id`, `Order Number`, `Order No`, `Amazon Order Id`, `Sales Record Number` |
| Customer Name | `buyer-name`, `Buyer Name`, `Recipient`, `recipient-name`, `Ship To Name`, `Ship Name`, `Post To Name`, `Full Name` |
| Address | `ship-address-1`, `Address Line 1`, `Shipping Address`, `Post To Address 1`, `Detail Address`, `Street` |
| Item | `product-name`, `Product Name`, `Item Title`, `Item Name`, `Title`, `Description` |
| Qty | `quantity-purchased`, `Quantity`, `Units` |
| Price | `Unit Price`, `Sold For`, `Sale Price`, `Price Each`, `SKU Unit Original Price` |
| Line Total | `item-price` (Amazon's price × qty), `Item Total`, `Total`, `Subtotal` |
| Shipping | `shipping-price`, `Postage And Packaging`, `Delivery Charge`, `Order Shipping`, `Shipping Fee After Discount` |
| Invoice Date | `purchase-date`, `Order Date`, `Sale Date`, `Paid Date` |
| City / Postcode / Country | `ship-city`, `Post To City`, `ship-postal-code`, `Zip`, `Postcode`, `ship-country` … |

Exports with a title line above the headers are fine. So are tab-separated `.txt` files (like Amazon order reports),
semicolon-separated files and files saved by Excel in Windows encoding. If a column isn't picked up,
rename its header to one of the required names above. Marketplace export layouts change from time to time,
so check the first file from each platform against the preview.

Suggested settings per platform:

| Platform export | Prices in CSV are | Shipping column is |
|---|---|---|
| Amazon order report (`.txt`) | Incl. VAT | Per item row |
| eBay orders CSV | Incl. VAT | Per order |
| TikTok Shop / Temu / Etsy / OnBuy | Incl. VAT | Per order |
| Your own sheet in the format above | Whichever you used | Per order |

---

## 5. How the numbers are worked out

All amounts are calculated in whole pence, so the totals always add up exactly.

- **Prices excl. VAT:** Net = Qty × Unit price (rounded to 1p) · VAT = Net × rate (rounded to 1p) · Gross = Net + VAT.
- **Prices incl. VAT:** Gross = Qty × Unit price · Net = Gross ÷ (1 + rate) (rounded to 1p) · VAT = Gross − Net.
  The invoice total matches what the customer paid to the penny.
- **Shipping** is charged VAT at its own rate (default 20%). It is shown excl. VAT in the totals, and its VAT is included in Total VAT.
- **Total Amount** = Subtotal + Shipping + Total VAT.
- When an invoice has more than one VAT rate, a **VAT summary** by rate is printed next to the totals.

Example: 20 × £14.574 → Net £291.48, VAT £58.30, Gross £349.78.

## 6. Settings

The **Settings** button sets:

- **Number prefix** – e.g. `OP{YYYY}-`, where `{YYYY}` becomes the current year (`{YY}` for two digits).
- **Next number** and **Digits** – e.g. next number 1 with 5 digits gives `OP2026-00001`.
  The number goes up by one each time you download an invoice that uses it.
- **Default VAT rate** for new items and CSV rows without a VAT rate.

Settings, the theme and your unfinished manual invoice are stored in this browser only (*localStorage*).
If you use the app on two computers, set **Next number** on each so the numbers don't clash.

## 7. Changing the company details

The company details are fixed near the top of the script in `index.html`:

```js
const COMPANY = {
  store: 'Office Point',
  slogan: 'Shopping made easier',
  name: 'Sim Distributors Ltd',
  addressLines: ['Unit 8, Heron Industrial Estate', 'Reading, RG7 1PJ', 'United Kingdom'],
  vatNumber: 'GB378692435',
};
```

Edit them in any text editor (Notepad, TextEdit, VS Code) and save. Edit the `CHANNELS` list on the line
below it to change the sales channels.

## 8. Technical notes

- Plain HTML, CSS and JavaScript in one file. No build step and no server.
- PDFs are made with [jsPDF](https://github.com/parallax/jsPDF) 2.5.2 and
  [jsPDF-AutoTable](https://github.com/simonbengtsson/jsPDF-AutoTable) 3.8.4. The text is real, selectable
  and searchable, not a screenshot. Long orders run onto more pages, and the table headers and page numbers repeat.
- ZIP files are made with [JSZip](https://stuk.github.io/jszip/) 3.10.1.
- Libraries load from the jsDelivr CDN, with unpkg as an automatic backup.
- PDFs use the standard Helvetica font, which covers Western European letters (é, ö, ñ, £, €). Letters outside
  it are simplified rather than printed as garbage (e.g. *Łukasz Żółć* → *Lukasz Zólc*).
- An uploaded logo is stored in the browser with the other settings.
- Page size: A4 portrait (210 × 297 mm).
