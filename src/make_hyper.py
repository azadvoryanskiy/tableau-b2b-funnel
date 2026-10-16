"""Turn data/olist_leads_2018.csv into a Tableau extract, data/olist_leads_2018.hyper.

Tableau Public only publishes workbooks whose data is an extract. Connecting the
workbook straight to a .hyper file (as Tableau's own sample workbooks do) means
nobody has to switch Live to Extract by hand before publishing.

    python src/make_hyper.py   (needs the tableauhyperapi package)
"""
from pathlib import Path

from tableauhyperapi import (Connection, CreateMode, HyperProcess, Nullability, SqlType,
                             TableDefinition, TableName, Telemetry, escape_string_literal)

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "olist_leads_2018.csv"
HYPER = ROOT / "data" / "olist_leads_2018.hyper"

TEXT, DATE, INT = SqlType.text(), SqlType.date(), SqlType.big_int()
COLUMNS = [
    ("lead_id", TEXT), ("first_contact_date", DATE), ("channel", TEXT), ("landing_page", TEXT),
    ("landing_page_top", TEXT), ("won", INT), ("won_date", DATE), ("days_to_close", INT),
    ("close_speed", TEXT), ("business_segment", TEXT), ("segment_top", TEXT), ("lead_type", TEXT),
    ("business_type", TEXT), ("sales_rep", TEXT), ("rep_top", TEXT),
]

table = TableDefinition(
    TableName("Extract", "Extract"),
    [TableDefinition.Column(name, sql_type, Nullability.NULLABLE) for name, sql_type in COLUMNS],
)

with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
    with Connection(hyper.endpoint, str(HYPER), CreateMode.CREATE_AND_REPLACE) as con:
        con.catalog.create_schema("Extract")
        con.catalog.create_table(table)
        rows = con.execute_command(
            f"COPY {table.table_name} FROM {escape_string_literal(str(CSV))} "
            "WITH (format csv, NULL '', delimiter ',', header)")
        won = con.execute_scalar_query(f"SELECT SUM(won) FROM {table.table_name}")
print(f"wrote {HYPER.name}: {rows:,} rows, {won:,} won")
