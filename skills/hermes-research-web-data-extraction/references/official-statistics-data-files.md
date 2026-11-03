# Official Statistics: Take the Data File, Not the Release Page

Government statistical agencies publish the numbers twice: once as prose in a news
release, and once as a bulk machine-readable file. The release HTML is written for
journalists and carries only the highlights the agency chose to name ("ranging from
4.0 percent in New York to -2.3 percent in West Virginia"). It will not hold the
figure you actually need. Download the data file.

This applies across agencies: BEA (GDP, personal income, PCE), BLS (employment,
CPI), Census (population, business patterns), EIA (energy). The pattern is always
news release at `/news/...` for context, bulk file at an `apps.<agency>.gov/...zip`
or `/data/...csv` path for the numbers.

## Find the bulk file from the release page

Fetch the release page as HTML (not `.txt`), then pull its links:

```bash
scrapling extract fetch "https://www.bea.gov/news/<release-slug>" $SCRATCH/rel.html
# then grep the raw html for the hrefs, not the rendered text
```

The rendered text drops most data-file links. Grep `href="[^"]*"` on the raw HTML
then filter for `zip|xlsx|csv|tables`. A release page will typically yield several
`.xlsx` supplement files plus links into the agency's interactive-table app.

## BEA Regional GDP (worked example)

Two zip endpoints cover state GDP and neither is advertised on the release page in a
greppable form. Confirm them with a HEAD request before pulling:

```bash
curl -sI "https://apps.bea.gov/regional/zip/SAGDP.zip" | head -8   # annual
curl -sI "https://apps.bea.gov/regional/zip/SQGDP.zip" | head -8   # quarterly
```

`last-modified` on the zip is the real data vintage. Compare it against the release
date on the news page: if the zip's date trails the release, the file predates the
revision and the release article is the fresher source.

Inside each zip the useful member is the single `*__ALL_AREAS_*.csv`, which holds
every state and every region in one file. Per-state files also exist but need 50
requests worth of unzipping for the same rows.

| Table | Zip | Contents |
|---|---|---|
| SAGDP2 | SAGDP | Annual, current dollars (nominal) |
| SAGDP9 | SAGDP | Annual, chained 2017 dollars (real) |
| SQGDP1 | SQGDP | Quarterly, real + current-dollar headline lines |
| SQGDP2 | SQGDP | Quarterly by industry, current dollars (incl. state totals) |

## CSV shape

Fixed columns then one column per period:

```
GeoFIPS, GeoName, Region, TableName, LineCode, IndustryClassification,
Description, Unit, 1997, 1998, ... 2025          # annual files
... 2005:Q1, 2005:Q2, ... 2026:Q2                # quarterly files
```

- `LineCode == 1` is the all-industry total. Higher line codes are industries and
  sub-industries, so an unfiltered read mixes levels of aggregation into one list.
- Read period columns by name: `2025` for annual, `2026:Q2` for quarterly.
- `Unit` states whether the column is current dollars or chained dollars. Do not
  assume; the same LineCode means different things across table files.
- Quote CSV fields containing commas (`"All industry total "` has a trailing space);
  use `csv.DictReader(skipinitialspace=True)` and strip every value.

## Never rank a geo table before validating the FIPS key

This is the trap that produces a confidently wrong top-ten. BEA's `ALL_AREAS` file
interleaves the 50 states, DC, the US total, and the eight BEA regions, and the
regions are large. Sorting on value alone puts **Southeast** at #1 ahead of
California, with Far West, Mideast, and Great Lakes filling the next three slots.
Nothing about the sort errors; the rows are simply not all states.

Filter to valid state FIPS before sorting:

```python
VALID_STATE_FIPS = {'01','02','04','05','06','08','09','10','11','12','13','15','16',
 '17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32',
 '33','34','35','36','37','38','39','40','41','42','44','45','46','47','48','49',
 '50','51','53','54','55','56'}   # 51 codes: 50 states + DC 11000

for row in csv.DictReader(f, skipinitialspace=True):
    if str(row['LineCode']).strip() != '1':           continue
    fips = row['GeoFIPS'].strip()
    if len(fips) != 5 or not fips.isdigit():          continue
    if fips[:2] not in VALID_STATE_FIPS:              continue   # drops US 00000 and 9xxxx regions
    if fips[2:] != '000':                             continue   # drops counties / metros
```

Identifying features: US total is `00000`; BEA regions are `9xxxx` (`91000` New
England, `92000` Mideast, `93000` Great Lakes, `94000` Plains, `95000` Southeast,
`96000` Southwest, `97000` Rocky Mountain, `98000` Far West); state and county FIPS
always end in `000` for the state-level row. A count of the filtered list should be
**51**, not 60.

Sanity-check the result against a known constraint before reporting: the sum of the
51 rows should be the US total minus territories. The `00000` US row and the summed
states will not match exactly, and that gap is normal rather than an error.

## Report the basis, and check it holds in the newest period

"Largest economy" is ambiguous between nominal and real, and the two give different
orderings at the tail. Nominal (current dollars) is the default reading of "largest".
Real (chained dollars) reorders the bottom of the list: measured for 2025, Washington
ranks #9 and New Jersey #11 on real GDP, while the same two swap on nominal.

Rank on both, name the basis in the answer, and state the basis in the source line.

Then check whether the ranking survives into the newest quarter. Adjacent ranks are
routinely within a rounding error of each other and flip on revision. Measured, the
#10 and #11 slots in current dollars sat $59 million apart, so the annual file and the
newest quarter disagreed on which state held #10. That is not a reason to pick one and
stay quiet: report the annual ranking, then say in one line that the newest quarter
puts the other state ahead by a hair and that the slot will keep flipping. A user
asking for a top ten is asking about a live system, and a single clean list hides a
tie that the next revision will move.

## Pitfalls

- **Do not scrape the release page for the numbers.** It ranks only the extremes the
  agency chose, and it never contains the full table.
- **A region row is not a state row.** Filter by FIPS, never by name and never by
  value. Sorting first and filtering later produces the wrong ten in the right order.
- **LineCode 1 only.** Every other line code is an industry, and summing line codes
  double-counts.
- **Prefer `.txt` for scrapling output** (see the main SKILL.md). The `.md` path dies
  on a missing `markdownify` after the fetch has already succeeded.
- **State the vintage.** Government tables are revised on a published schedule; name
  the release date and the period so the answer is checkable later.
