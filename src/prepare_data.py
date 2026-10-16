"""Build the one table the Tableau dashboard reads: one row per inbound lead.

    python src/prepare_data.py

Reads the two Olist Marketing Funnel files from data/raw and writes
data/olist_leads_2018.csv. Only leads whose first contact was in January to May
2018 are kept: the first deal in the data was won on 5 Dec 2017, so leads from
2017 had almost no chance to close.
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "olist_leads_2018.csv"

CHANNELS = {
    "organic_search": "Organic search",
    "paid_search": "Paid search",
    "social": "Social",
    "unknown": "Unknown",
    "direct_traffic": "Direct traffic",
    "email": "Email",
    "referral": "Referral",
    "other": "Other",
    "display": "Display",
    "other_publicities": "Other ads",
}

SQL = f"""
SELECT
    l.mql_id                                                   AS lead_id,
    l.first_contact_date,
    l.origin,
    'LP-' || left(l.landing_page_id, 6)                        AS landing_page,
    (d.mql_id IS NOT NULL)::INT                                AS won,
    d.won_date::DATE                                           AS won_date,
    -- greatest() skips NULLs, so leads that were never won need their own branch;
    -- one deal is dated two days before its first contact and counts as same-day
    CASE WHEN d.mql_id IS NOT NULL
         THEN greatest(date_diff('day', l.first_contact_date, d.won_date::DATE), 0)
    END                                                        AS days_to_close,
    d.business_segment,
    d.lead_type,
    d.business_type,
    'Rep ' || left(d.sr_id, 4)                                 AS sales_rep
FROM read_csv('{RAW / "olist_marketing_qualified_leads_dataset.csv"}', header = true) AS l
LEFT JOIN read_csv('{RAW / "olist_closed_deals_dataset.csv"}', header = true) AS d
    USING (mql_id)
WHERE l.first_contact_date >= DATE '2018-01-01'
ORDER BY l.first_contact_date, l.mql_id
"""

SPEED = [(7, "1. Within a week"), (14, "2. 8-14 days"), (30, "3. 15-30 days"),
         (60, "4. 31-60 days"), (90, "5. 61-90 days")]


def label(text):
    """'home_decor' -> 'Home decor'."""
    return text.replace("_", " ").capitalize() if isinstance(text, str) else text


def speed(days):
    if days != days:          # NaN: the lead was never won
        return None
    for limit, name in SPEED:
        if days <= limit:
            return name
    return "6. Over 90 days"


def top_n(df, column, n, other, by_leads=False):
    """Keep the n biggest values of a column (by leads or by won deals), lump the rest."""
    size = df.groupby(column).size() if by_leads else df.groupby(column)["won"].sum()
    keep = set(size.sort_values(ascending=False, kind="stable").head(n).index)
    return df[column].where(df[column].isin(keep) | df[column].isna(), other)


def main():
    df = duckdb.sql(SQL).df()
    df["channel"] = df.pop("origin").map(CHANNELS).fillna("Not set")
    for col in ("business_segment", "lead_type", "business_type"):
        df[col] = df[col].map(label)
    df["close_speed"] = df["days_to_close"].map(speed)
    df["days_to_close"] = df["days_to_close"].astype("Int64")
    # The dashboard shows a top-N list for three fields. Fixing the lists here
    # keeps them stable when someone clicks a filter.
    df["landing_page_top"] = top_n(df, "landing_page", 10, "Other pages", by_leads=True)
    df["segment_top"] = top_n(df, "business_segment", 8, "Other segments")
    df["rep_top"] = top_n(df, "sales_rep", 10, "Other reps")
    columns = ["lead_id", "first_contact_date", "channel", "landing_page", "landing_page_top",
               "won", "won_date", "days_to_close", "close_speed", "business_segment",
               "segment_top", "lead_type", "business_type", "sales_rep", "rep_top"]
    df[columns].to_csv(OUT, index=False)
    print(f"wrote {OUT.name}: {len(df):,} leads, {df.won.sum():,} won ({df.won.mean():.1%})")


if __name__ == "__main__":
    main()
