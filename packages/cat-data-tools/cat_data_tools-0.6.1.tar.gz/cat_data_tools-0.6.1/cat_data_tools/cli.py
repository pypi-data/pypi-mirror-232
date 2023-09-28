from cat_data_tools.filter_data_by_month import (
    summarize_effort_captures_and_add_trappers,
    summarize_effort_captures,
)
from cat_data_tools.filter_data_between_years import filter_data_between_years
import cat_data_tools as cdt
import pandas as pd
import typer


app = typer.Typer()


@app.command(help="Write monthly summary from weekly summary without trappers")
def write_monthly_summary_without_trappers(weekly_data_path: str = "", output_path: str = ""):
    effort_data = pd.read_csv(weekly_data_path)
    monthly_data = summarize_effort_captures(effort_data)
    monthly_data.to_csv(output_path, index=False)


@app.command(help="Write monthly summary from weekly summary")
def write_monthly_summary(
    weekly_data_path: str = "", monthly_trappers_path: str = "", output_path: str = ""
):
    effort_data = pd.read_csv(weekly_data_path)
    monthly_trappers = pd.read_csv(monthly_trappers_path)
    monthly_data = summarize_effort_captures_and_add_trappers(monthly_trappers, effort_data)
    monthly_data.to_csv(output_path, index=False, na_rep="NA")


@app.command(help="Filter monthly summary between years")
def filter_monthly_summary(
    monthly_data_path: str = "",
    output_path: str = "",
    initial_year: int = 2014,
    final_year: int = 2019,
):
    dataframe = pd.read_csv(monthly_data_path)
    filtered_dataframe = filter_data_between_years(dataframe, initial_year, final_year)
    filtered_dataframe.to_csv(output_path, index=False, na_rep="NA")


@app.command()
def version():
    print(cdt.__version__)
