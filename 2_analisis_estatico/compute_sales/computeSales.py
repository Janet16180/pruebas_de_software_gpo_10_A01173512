"""Compute total sales cost from a price catalogue and a sales record."""

import argparse
import json
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the sales computation program.

    Returns:
        argparse.Namespace: Parsed arguments containing both file paths.
    """
    parser = argparse.ArgumentParser(
        prog="computeSales.py",
        description="Compute the total cost for all sales based on a "
        "price catalogue and a sales record.",
        epilog="Example: python computeSales.py priceCatalogue.json salesRecord.json",
    )

    parser.add_argument(
        "price_catalogue",
        type=Path,
        help="Path to the JSON file containing the product price catalogue",
    )

    parser.add_argument(
        "sales_record",
        type=Path,
        help="Path to the JSON file containing the sales record",
    )

    return parser.parse_args()


def load_json_file(file_path: Path) -> list[dict]:
    """
    Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        list: Parsed JSON data as a list of dictionaries.
    """
    if not file_path.exists():
        logger.error("File '%s' does not exist", file_path)
        return []

    if not file_path.is_file():
        logger.error("'%s' is not a file", file_path)
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in '%s': %s", file_path, e)
        return []

    if not isinstance(data, list):
        logger.error("Expected a JSON array in '%s'", file_path)
        return []

    return data


def build_price_catalogue(products: list[dict]) -> dict[str, float]:
    """
    Build a dictionary mapping product titles to their prices.

    Args:
        products: List of product dictionaries from the catalogue.

    Returns:
        dict: Mapping of product title to price.
    """
    catalogue = {}

    for i, product in enumerate(products):
        if not isinstance(product, dict):
            logger.error("Invalid product entry at index %d", i)
            continue

        title = product.get("title")
        price = product.get("price")

        if title is None or price is None:
            logger.error("Missing 'title' or 'price' at index %d", i)
            continue

        if not isinstance(title, str):
            logger.error("Invalid title type at index %d", i)
            continue

        try:
            price = float(price)
        except (ValueError, TypeError):
            logger.error("Invalid price '%s' for product '%s'", price, title)
            continue

        catalogue[title] = price

    return catalogue


def compute_sales(
    catalogue: dict[str, float], sales: list[dict]
) -> tuple[dict[int, float], float]:
    """
    Compute the total cost per sale and the grand total.

    Args:
        catalogue: Mapping of product title to price.
        sales: List of sale record dictionaries.

    Returns:
        tuple: A dictionary with sale totals by SALE_ID and the grand total.
    """
    sale_totals: dict[int, float] = {}
    grand_total = 0.0

    for i, record in enumerate(sales):
        if not isinstance(record, dict):
            logger.error("Invalid sale entry at index %d", i)
            continue

        sale_id = record.get("SALE_ID")
        product = record.get("Product")
        quantity = record.get("Quantity")

        if sale_id is None or product is None or quantity is None:
            logger.error("Missing required fields at index %d", i)
            continue

        if product not in catalogue:
            logger.error(
                "Product '%s' not found in catalogue (sale %s, index %d)",
                product,
                sale_id,
                i,
            )
            continue

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            logger.error(
                "Invalid quantity '%s' for product '%s' (sale %s)",
                quantity,
                product,
                sale_id,
            )
            continue

        if quantity < 0:
            logger.warning(
                "Negative quantity %d for product '%s' (sale %s), "
                "treated as a return/refund",
                quantity,
                product,
                sale_id,
            )

        item_cost = catalogue[product] * quantity
        grand_total += item_cost

        if sale_id not in sale_totals:
            sale_totals[sale_id] = 0.0
        sale_totals[sale_id] += item_cost

    return sale_totals, grand_total


def format_results(
    sale_totals: dict[int, float], grand_total: float, elapsed_time: float
) -> str:
    """
    Format the sales results as a readable string.

    Args:
        sale_totals: Dictionary with total cost per SALE_ID.
        grand_total: The overall total cost.
        elapsed_time: Time taken for computation.

    Returns:
        str: Formatted results string.
    """
    lines = []

    for sale_id in sorted(sale_totals.keys()):
        lines.append(f"Sale {sale_id}: ${sale_totals[sale_id]:,.2f}")

    lines.append("")
    lines.append(f"GRAND TOTAL: ${grand_total:,.2f}")
    lines.append(f"Elapsed Time: {elapsed_time:.6f} seconds")

    return "\n".join(lines)


def write_results_to_file(results: str, output_file: str = "SalesResults.txt") -> None:
    """
    Write the results to a file.

    Args:
        results: Formatted results string.
        output_file: Name of the output file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(results)
        f.write("\n")


def main() -> None:
    """Main function to orchestrate the sales computation."""
    start_time = time.time()

    args = parse_args()

    products = load_json_file(args.price_catalogue)
    if not products:
        logger.error("No products loaded from catalogue")
        return

    catalogue = build_price_catalogue(products)
    if not catalogue:
        logger.error("No valid products in catalogue")
        return

    sales = load_json_file(args.sales_record)
    if not sales:
        logger.error("No sales loaded from record")
        return

    sale_totals, grand_total = compute_sales(catalogue, sales)

    end_time = time.time()
    elapsed_time = end_time - start_time

    results = format_results(sale_totals, grand_total, elapsed_time)

    logger.info(results)
    write_results_to_file(results)
    logger.info("Results also saved to: SalesResults.txt")


if __name__ == "__main__":
    main()
