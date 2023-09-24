import polars as pl
import sqlite3 as sql
import pytest
from pathlib import Path
import os
import sys

sys.path.append(os.path.abspath("../.."))
from qprofiler import DataProfiler

DATA_PATH = "datasets/loan-perf.csv"
TEST_DATA_PATH = "datasets/loan-perf-test.csv"


@pytest.fixture
def profiler() -> DataProfiler:
    return DataProfiler()


def test_profiler_cwd_attribute(profiler: DataProfiler) -> None:
    assert profiler.cwd == Path(os.getcwd())


def test_profiler_path_attribute(profiler: DataProfiler) -> None:
    assert profiler.profiler_path == Path(os.getcwd())


def test_dprofiler_creation(profiler: DataProfiler) -> None:
    assert profiler.profiler_config.exists() == True


def test_dataset_profile_creation(profiler: DataProfiler) -> None:
    ref = profiler.scan_csv_file(DATA_PATH, unique_identifier="customerid")
    profiler.create_profile(ref, "reference")
    assert (
        len(os.listdir(os.path.join(os.getcwd(), ".dprofiler", "in_use", "reference")))
        == 1
    )


def test_dataset_profile_archieves(profiler: DataProfiler) -> None:
    ref = profiler.scan_csv_file(DATA_PATH, unique_identifier="customerid")
    profiler.update_profile(ref, "reference")
    assert (
        len(os.listdir(os.path.join(os.getcwd(), ".dprofiler", "archive", "reference")))
        == 1
    )


def test_filesystem_when_delete_profile(profiler: DataProfiler) -> None:
    profiler.del_profile("reference")
    assert (
        Path(os.path.join(os.getcwd(), ".dprofiler", "archive", "reference")).exists()
        == False
    )


def test_exception_if_profile_not_exist(profiler: DataProfiler) -> None:
    with pytest.raises(FileNotFoundError):
        profiler.del_profile("reference")


def test_metadata_no_of_records(profiler: DataProfiler) -> None:
    ref = profiler.scan_csv_file(DATA_PATH, unique_identifier="customerid")
    profiler.create_profile(ref, "reference")
    test = profiler.scan_csv_file(TEST_DATA_PATH, unique_identifier="customerid")
    profiler.create_profile(test, "test_reference")
    q = """
        SELECT profile_name,
               MAX(created_at) AS last_creation_date,
               MAX(archieved_at) AS last_archieving_date,
               COUNT(*) AS no_of_archieves
        FROM archieved
        GROUP BY 1;
    """
    conn = sql.connect(profiler.profiler_config.joinpath("metadata.db"))
    df = pl.read_database(query=q, connection=conn)
    conn.close()
    assert df.height == 2


def test_formating_profiler(profiler: DataProfiler) -> None:
    profiler.format_profiler()
    assert Path(os.path.join(os.getcwd(), ".dprofiler")).exists() == False
