# Where do we lose B2B leads?

An interactive Tableau dashboard on 5,998 real inbound B2B leads and the 781 that became
signed deals.

**Live dashboard on Tableau Public:** https://public.tableau.com/app/profile/artem.zadvoryanskiy/viz/lead-funnel/Funnel

**Skill on show: Tableau.** One large dashboard: KPI tiles, a volume-vs-quality bubble
chart with an average line, paired bars, a weekly stacked view, top-10 lists, level of
detail calculations, and click-to-filter actions across the whole page.

**The answer in one line:** 87% of leads never close. Social and email bring 23% of leads
but only 10% of deals, and a lead that hasn't closed in 30 days almost never does.

## Business problem

Olist runs a marketplace that small Brazilian shops join to sell online. Shops find it
through ads, search and social media, fill in a form, and become a lead. A sales team
then calls them and tries to sign them up. Olist makes money from the shops that sell
through it, so this is a classic B2B sales funnel.

The question for the marketing and sales teams: where do the leads drop out, and what
should change?

## Data

[Marketing Funnel by Olist](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist)
on Kaggle, CC BY-NC-SA 4.0. Two real files:

| File | One row is | Rows |
|---|---|---:|
| `olist_marketing_qualified_leads_dataset.csv` | a lead: first contact date, landing page, channel | 8,000 |
| `olist_closed_deals_dataset.csv` | a lead that became a deal: won date, segment, sales rep | 842 |

Each deal matches exactly one lead, so the funnel has two steps: lead, then deal.

**One caveat.** The first deal in the data is dated 5 December 2017, and leads from 2017
converted at about 3% against 13% from January 2018. So the dashboard uses leads with
first contact from January to May 2018: 5,998 leads, 781 deals.

There is no marketing spend in the data, so the dashboard can say which channels bring
good leads, but not which ones pay for themselves.

## Process

1. [`src/prepare_data.py`](src/prepare_data.py) joins the two files into one table, one
   row per lead, with days to close, a time-to-close bucket and fixed top-10 lists for
   landing pages, segments and sales reps.
2. [`src/make_hyper.py`](src/make_hyper.py) turns the table into a Tableau extract
   (`data/olist_leads_2018.hyper`) with Tableau's Hyper API. Tableau Public only publishes
   workbooks built on an extract, so the workbook connects to it directly.
3. `lead-funnel.twb` reads that extract. The key measures are plain counts and ratios:
   conversion = deals ÷ leads, and a channel's share of all leads or all deals uses an
   `EXCLUDE` level of detail calculation, so the shares stay right when a filter is
   applied.
4. Clicking a channel in either of the two top charts filters every other chart on the
   page.

## Insights

1. **13.0% of leads become deals.** 781 of 5,998. The other 87% are lost at the one step
   the data shows.
2. **Search carries the funnel.** Organic and paid search bring 48.6% of leads and 55.1%
   of deals, both converting at about 14.7%.
3. **Social and email bring volume, not deals.** Together they are 23.3% of leads but
   10.2% of deals: social converts at 6.3%, email at 4.0%.
4. **Deals close fast or not at all.** The median deal closes in 12 days and 70.7% close
   within 30 days. Of the leads still open after 30 days, only 4.2% close later.
5. **The landing page matters as much as the channel.** The top 10 pages bring 60% of
   leads. The best ones convert at 22–23%, the weakest at 3.5–5.5%.

## Recommendations

**1. Stop treating every lead the same.** Leads from social and email convert at a third of
the rate of search leads. I'd send them into an email nurture track first and give the
sales team's calls to search and direct leads.

**2. Give the sales team a 30-day rule.** Work every new lead hard for 30 days, then move
it to nurture: after that point only about 4 in 100 still close.

**3. Test the landing pages.** The gap between pages is as big as the gap between
channels. I'd send the traffic of a weak page (LP-58326e, 5.5%) to the layout of a strong
one (LP-22c298, 23.0%) as an A/B test.

**How I'd measure it.** For the landing page test, the main metric is the share of leads
that become a deal within 30 days, split at random by visitor. Guardrail: the number of
form submissions, so a page that converts better but collects far fewer leads doesn't win
by accident.

## Run it yourself

1. Download the two CSV files from Kaggle into `data/raw/`.
2. Run `python src/prepare_data.py`. It writes `data/olist_leads_2018.csv`.
3. Run `pip install tableauhyperapi` and `python src/make_hyper.py`. It writes
   `data/olist_leads_2018.hyper`.
4. Open `lead-funnel.twb` in Tableau Desktop or Tableau Public.
