import glob
import json
import os
from pathlib import Path
import polars as pl
import sys
import typer
from typing import List, Optional

import apm4py
import apm4py.log_grower

app = typer.Typer()


@app.command()
def upload(
    data_folder: str = typer.Argument(help="Folder where data sets are stored"),
    name: Optional[str] = typer.Option(None, help="Name of the event log"),
    profile: str = typer.Option("default", help="Profile of the Process Mining host"),
    chunk_size: int = typer.Option(
        250000, help="Number of lines to upload in one chunk"
    ),
):
    profile_config = get_profile_config(profile)
    api = apm4py.create_api(**profile_config)
    event_path = get_file_by_pattern(data_folder, "*[eE]vent*.csv")
    event_semantics = get_file_by_pattern(data_folder, "*[eE]vent*.json")
    case_file = get_file_by_pattern(data_folder, "*[cC]ase*.csv")
    case_semantics = get_file_by_pattern(data_folder, "*[cC]ase*.json")

    name = name if name is not None else Path(event_path).stem
    api.upload_event_log_file(
        name=name,
        event_file_path=event_path,
        event_semantics_path=event_semantics,
        case_file_path=case_file,
        case_semantics_path=case_semantics,
        chunk_size=chunk_size,
        show_progress=True,
    )


@app.command()
def list_logs(
    profile: str = typer.Option("default", help="Profile of the Process Mining host"),
):
    profile_config = get_profile_config(profile)
    api = apm4py.create_api(**profile_config)
    logs = api.list_logs()

    if len(logs) > 0:
        pl.Config.set_fmt_str_lengths(100)
        print(
            pl.from_dicts(logs)
            .with_columns(pl.from_epoch("insertedAt", time_unit="ms"))
            .select(["id", "name", "insertedAt"])
            .sort("insertedAt", descending=True)
        )

    else:
        print("No logs available")


def get_profile_config(profile: str):
    apm_dir = os.path.join(os.environ.get("HOME"), ".apm")
    apm_profile_path = os.path.join(os.environ.get("HOME"), ".apm", profile)
    if not os.path.exists(apm_profile_path):
        if not os.path.exists(apm_dir):
            os.mkdir(apm_dir)

        print(f"Profile {profile} does not exists. Please create a profile first.")
        profile = typer.prompt("Name of your profile", default="default")
        if profile == "":
            profile = "default"

        host = typer.prompt("Hostname")
        scheme = typer.prompt("Scheme", default="https")
        port = typer.prompt("Port", default="auto")
        token = typer.prompt("API Token", default="None")
        instance = typer.prompt("Instance", default=2)

        profile_config = {"host": host, "scheme": scheme, "instance": instance}

        if port != "auto":
            profile_config["port"] = port

        if token != "None":
            profile_config["token"] = token

        apm_profile_path = os.path.join(os.environ.get("HOME"), ".apm", profile)
        with open(apm_profile_path, "w") as profile_file:
            json.dump(profile_config, profile_file)

    else:
        with open(apm_profile_path, "r") as profile_file:
            profile_config = json.loads(profile_file.read())

    return profile_config


def get_file_by_pattern(dir: str, file_pattern: str) -> Optional[str]:
    files = glob.glob(os.path.join(dir, file_pattern))
    if len(files) == 0:
        return None

    if len(files) > 1:
        raise (f"There should be only 1 file matching '{file_pattern}'")

    return files[0]


@app.command()
def grow_log(
    orig_data_folder: str = typer.Argument(help="Folder for the original dataset"),
    dataset_collection: str = typer.Option(
        None, help="Name of the dataset collection (P2P_Benchmark|)"
    ),
    output_csv: bool = typer.Option(False, help="Output CSV files instead of parquet"),
    output_feather: bool = typer.Option(
        False, help="Output feather files instead of parquet"
    ),
    feather_compression: str = typer.Option(
        "uncompressed", help="uncompressed|lz4|zstd"
    ),
    compression_level: int = typer.Option(None, help="File compression level"),
    data_folder: str = typer.Option("./data", help="Output folder for datasets"),
    dataset: Optional[List[str]] = typer.Option(
        None, help="Only build a specific dataset from collection"
    ),
    partitions: int = typer.Option(
        None, help="Overwrite num partitions with given number"
    ),
    use_internal_format: bool = typer.Option(
        False, help="Use the internally used format with numerical Case IDs"
    ),
    csv_separator: str = typer.Option(","),
    growth_factor: int = typer.Option(
        None,
        help="Frequency of appending the log to itself. Only used when no dataset collection is selected.",
    ),
):
    event_path = get_file_by_pattern(orig_data_folder, "*[eE]vent*.csv")
    if event_path is not None:
        event_semantics_path = get_file_by_pattern(orig_data_folder, "*[eE]vent*.json")

        if event_semantics_path is None:
            print(
                "Event CSV import requires an event semantics JSON file in the same directory"
            )
            raise typer.Abort()

        with open(event_semantics_path, "r") as event_semantics_file:
            event_semantics = json.load(event_semantics_file)

        events_case_id = [
            s["name"] for s in event_semantics if s["semantic"] == "Case ID"
        ][0]
        events_original = pl.read_csv(event_path, separator=csv_separator)

    else:
        event_path = get_file_by_pattern(orig_data_folder, "*[eE]vent*.parquet")
        if event_path is None:
            print("Couldn't find any event file in the dataset directory")
            raise typer.Abort()

    cases_path = get_file_by_pattern(orig_data_folder, "*[cC]ase*.csv")
    if cases_path is not None:
        case_semantics_path = get_file_by_pattern(orig_data_folder, "*[cC]ase*.json")
        if case_semantics_path is None:
            print(
                "Case CSV import requires an event semantics JSON file in the same directory"
            )
            raise typer.Abort()

        with open(case_semantics_path, "r") as case_semantics_file:
            case_semantics = json.load(case_semantics_file)

        cases_case_id = [
            s["name"] for s in case_semantics if s["semantic"] == "Case ID"
        ][0]
        cases_original = pl.read_csv(cases_path, separator=csv_separator)

    variants_original = None
    if use_internal_format:
        variants_original = pl.read_parquet(
            os.path.join(orig_data_folder, "variants.parquet")
        )

    apm4py.log_grower.grow_log(
        events_original=events_original,
        events_case_id=events_case_id,
        cases_original=cases_original,
        cases_case_id=cases_case_id,
        variants_original=variants_original,
        dataset_collection=dataset_collection,
        output_csv=output_csv,
        output_feather=output_feather,
        feather_compression=feather_compression,
        compression_level=compression_level,
        data_folder=data_folder,
        dataset=dataset,
        partitions=partitions,
        use_internal_format=use_internal_format,
        growth_factor=growth_factor,
    )


def main():
    sys.exit(app())


if __name__ == "__main__":
    main()
