# Data-dense and map screens

Tools such as dashboards, admin views, validators and GIS apps are used repeatedly by people who know the
domain. Optimize for scanning and speed, not first impressions: tighter spacing (a compact density scale),
smaller type for data, and fewer decorative elements.

## Tables

- A sticky header. Numbers right-aligned in `font-variant-numeric: tabular-nums`, and text left-aligned.
- Units in the header (`Powierzchnia [ha]`), not repeated in every cell.
- Sort, filter and pagination state lives in the URL. Show active filters as removable chips.
- Row actions sit at the row end or in a context menu. Put bulk actions in a bar that appears on selection.
- More than ~200 rows: virtualize (TanStack Virtual) or paginate on the server.
- An empty result for a filter is different from no data at all. Offer "clear filters".

## Dashboards and statistics

- Order: KPIs (3–5 numbers with a delta and a period) → trends (line or bar charts) → a detail table.
- Every number has its period and unit next to it. Don't show a KPI without comparison context.
- Chart colors come from the tokens. Categorical palettes must be colorblind-safe (ColorBrewer, Okabe-Ito).
- Choropleth or sequential data: a sequential palette (viridis, or ColorBrewer Greens for forestry
  data). Diverging data: a diverging palette with a meaningful midpoint.

## Map screens

- Layout: the map fills the viewport. Filters and layers go in a collapsible side panel (desktop), and details
  for the selected feature go in a second panel or a popover. On mobile, use a **bottom sheet** instead of side panels,
  and keep the map at least 50% visible.
- Selection is shared: clicking on the map highlights the row in the list and vice versa. It also goes into the URL.
- Every styled layer has a legend. Show symbols or patterns plus labels, not color alone.
- Controls (zoom, layers, locate, measure) sit in consistent corners, are keyboard-reachable and have labels.
- Loading tiles or data: a subtle progress indicator on the map, never blocking interaction.
- Validation results (validator web service): severity colors from semantic tokens
  (`--color-danger`, `--color-warning`, `--color-info`), a count per severity always visible, and
  a list ↔ map sync (see the web-maps skill).

## Forms

- Labels above inputs. Placeholders are not labels.
- Validate on blur or submit, and put the message under the field. The summary at the top for long forms links to fields.
- Group long forms into sections with headings. Mark optional fields rather than required ones if most are required.
- Geometry input (drawing on a map, uploading a file): show the result on a mini-map before submitting.
