"""Unit tests for computeSales CLI tool."""

import subprocess
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPT = BASE_DIR / "computeSales.py"
RESOURCES = BASE_DIR / "resources"


def run_script(*args: str) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    # logging writes to stderr, combine both streams for assertion convenience
    result.output = result.stdout + result.stderr
    return result


class TestCLIArguments:
    def test_no_arguments(self):
        result = run_script()
        assert result.returncode != 0
        assert "usage" in result.stderr.lower()

    def test_one_argument(self):
        result = run_script(str(RESOURCES / "TC1.ProductList.json"))
        assert result.returncode != 0
        assert "usage" in result.stderr.lower()

    def test_nonexistent_catalogue(self):
        result = run_script("nonexistent.json", str(RESOURCES / "TC1.Sales.json"))
        assert "does not exist" in result.output

    def test_nonexistent_sales(self):
        result = run_script(str(RESOURCES / "TC1.ProductList.json"), "nonexistent.json")
        assert "does not exist" in result.output


class TestInvalidDataHandling:
    def test_invalid_json_catalogue(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json{{{")
        result = run_script(str(bad_file), str(RESOURCES / "TC1.Sales.json"))
        assert "Invalid JSON" in result.output

    def test_invalid_json_sales(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{broken")
        result = run_script(str(RESOURCES / "TC1.ProductList.json"), str(bad_file))
        assert "Invalid JSON" in result.output

    def test_product_not_in_catalogue(self):
        result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC3.Sales.json")
        )
        assert "not found in catalogue" in result.output
        assert "GRAND TOTAL" in result.output

    def test_negative_quantity_warns(self):
        result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC2.Sales.json")
        )
        assert "Negative quantity" in result.output
        assert "GRAND TOTAL" in result.output


class TestOutputResults:
    def test_results_file_created(self):
        results_file = BASE_DIR / "SalesResults.txt"
        if results_file.exists():
            results_file.unlink()

        run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC1.Sales.json")
        )
        assert results_file.exists()
        results_file.unlink()

    def test_results_file_content_matches_output(self):
        results_file = BASE_DIR / "SalesResults.txt"

        result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC1.Sales.json")
        )

        file_content = results_file.read_text(encoding="utf-8").strip()
        output_lines = result.output.strip().split("\n")
        output_content = "\n".join(
            line for line in output_lines if "Results also saved to" not in line
        ).strip()

        assert file_content == output_content
        results_file.unlink()

    def test_elapsed_time_in_output(self):
        result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC1.Sales.json")
        )
        assert "Elapsed Time:" in result.output
        assert "seconds" in result.output

    def test_grand_total_in_output(self):
        result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC1.Sales.json")
        )
        assert "GRAND TOTAL" in result.output


class TestIntegrationTC1:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC1.Sales.json")
        )

    def test_exit_code(self):
        assert self.result.returncode == 0

    def test_no_errors(self):
        assert "not found in catalogue" not in self.result.output
        assert "Negative quantity" not in self.result.output

    def test_all_sales_present(self):
        for sale_id in range(1, 11):
            assert f"Sale {sale_id}:" in self.result.output

    def test_grand_total(self):
        assert "$2,481.86" in self.result.output


class TestIntegrationTC2:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC2.Sales.json")
        )

    def test_exit_code(self):
        assert self.result.returncode == 0

    def test_negative_quantity_warnings(self):
        assert "Negative quantity" in self.result.output

    def test_execution_continues_after_warnings(self):
        assert "GRAND TOTAL" in self.result.output

    def test_grand_total(self):
        assert "$166,568.23" in self.result.output


class TestIntegrationTC3:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = run_script(
            str(RESOURCES / "TC1.ProductList.json"), str(RESOURCES / "TC3.Sales.json")
        )

    def test_exit_code(self):
        assert self.result.returncode == 0

    def test_unknown_product_errors(self):
        assert "Elotes" in self.result.output
        assert "Frijoles" in self.result.output

    def test_negative_quantity_warnings(self):
        assert "Negative quantity" in self.result.output

    def test_grand_total(self):
        assert "$165,235.37" in self.result.output
