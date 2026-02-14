computeSales.py
===============

A command line program that computes the total cost for all sales based on a price catalogue and a sales record.

Usage
-----

python computeSales.py priceCatalogue.json salesRecord.json

The program reads two JSON files:
- A price catalogue containing product information (title, price, etc.)
- A sales record containing individual sale entries (product, quantity, etc.)

It computes the total cost per sale and a grand total, then displays the results on screen and saves them to SalesResults.txt.


Input File Formats
------------------

Price catalogue: a JSON array of objects, each with at least a "title" and "price" field.

```json
[
  {"title": "Brown eggs", "price": 28.1, ...},
  {"title": "Asparagus", "price": 18.95, ...}
]
```

Sales record: a JSON array of objects with "SALE_ID", "Product", and "Quantity" fields.

```json
[
  {"SALE_ID": 1, "SALE_Date": "01/12/23", "Product": "Brown eggs", "Quantity": 3},
  {"SALE_ID": 1, "SALE_Date": "01/12/23", "Product": "Asparagus", "Quantity": 1}
]
```


Output Format
-------------

```
Sale 1: $83.39
Sale 2: $67.57
Sale 3: $144.74
...

GRAND TOTAL: $2,481.86
Elapsed Time: 0.002974 seconds
```

Results are also saved to SalesResults.txt.


Error Handling
--------------

The program handles invalid data gracefully and continues execution:

- Products in the sales record not found in the catalogue are skipped with an error message.
- Negative quantities are treated as returns/refunds (they subtract from the total) and a warning is logged.
- Malformed JSON files produce an error message and the program exits early.
- Missing required fields in individual records are skipped with an error message.

Example output:

    Product 'Elotes' not found in catalogue (sale 6, index 21)
    Negative quantity -35 for product 'Fresh blueberries' (sale 8), treated as a return/refund
