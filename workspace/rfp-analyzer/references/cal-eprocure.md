# Cal eProcure research

How this skill turns a link (or a dropped folder) into a complete source set under `00-source/`.

## URL shapes

Accept any of:

- `https://caleprocure.ca.gov/event/{business-unit}/{event-id}`
- `https://caleprocure.ca.gov/pages/Events-BS3/event-details.aspx?EventID={event-id}`
- A pasted Event ID (digits, often 10 characters like `0000037577`)
- A local folder of already-downloaded event-package files

`{business-unit}` is a 4-digit department code (e.g. `4265`). `{event-id}` is the Event ID. Use Event ID as the folder name directly under the Git working folder.

If the user pastes a BidNet, PlanetBids, HigherGov, or email link, resolve back to the Cal eProcure event before proceeding. Do not invent an Event ID from the title. Third-party blurbs (HigherGov, BidBanana, GovTribe, Government Navigator) can hint Event Version or contact; they are never the Event Package. An old Part 1 PDF on those sites is often a superseded original.

## Portal

Cal eProcure is InFlight NLX wrapping PeopleSoft Strategic Sourcing (`psfpd1`, portal `SUPPLIER/ERP`). `/event/{BU}/{event-id}` 302s to:

```
/pages/Events-BS3/event-details.aspx?Page=AUC_RESP_INQ_DTL&Action=U&AUC_ID={id}&AUC_ROUND=1&BIDDER_ID=BID0000001&BIDDER_LOC=1&BIDDER_SETID=STATE&BIDDER_TYPE=B&BUSINESS_UNIT={BU}
```

`BID0000001` is the guest public-inquiry identity. Public events do not need a vendor login. File bytes still need a live InFlight/PeopleSoft session.

| Piece | Value |
|---|---|
| Component | `AUC_MANAGE_BIDS.AUC_RESP_INQ_DTL.GBL` |
| View Event Package | `ICAction=RESP_INQ_DL0_WK_AUC_DOWNLOAD_PB` |
| Per-file View | `PV_ATTACH_WRK_SCM_DOWNLOAD$0` … `$N` |
| Attachments page | `/pages/Events-BS3/event-bid-comments.aspx` |
| PeopleSoft via InFlight | `/nlx3/psc/psfpd1/SUPPLIER/ERP/c/AUC_MANAGE_BIDS.AUC_RESP_INQ_DTL.GBL` |

## Do not use as primary

| Attempt | Result |
|---|---|
| Bare curl (no browser UA) | 403 from AWS ELB |
| `curl` / `web_fetch` / `browse_page` of `/event/{BU}/{id}` with a Chrome UA | 200 ~32 KB InFlight SPA shell, title “California eProcurement Portal”. No event title, dates, or files. Do not analyze from it. |
| Chrome for Testing / Playwright headless (`--headless=new`) | 403 (WAF fingerprints headless/CfT). Not the download browser. |
| PeopleSoft GBL GET without `-L` | 302 HTML ~787 bytes “document has moved”. Always follow redirects. |
| POST `ICAction=PV_ATTACH_WRK_SCM_DOWNLOAD$N` including the button HTML `value="View"` | PeopleSoft 126,141: field is 1 character; `"View"` is 4. Do not serialize `type=button` values onto that field. |
| `curl` a signed `/psc/psfpd1/view/{token}/filename.zip` or `/viewredirect/{token}/…` without the live Chrome session | 302 `?cmd=login&errorPg=ckreq` or 403. Token is session-bound, not a CDN link. |
| Third-party solicitation pages | Not the Event Package. Latest addendum wins. |

## Event details (header fields only)

`curl` can fill `event-meta.yaml` (not files) if you: (a) browser UA, (b) cookie jar from a GET of `/event/{BU}/{id}`, (c) GET with `-L`:

```
https://caleprocure.ca.gov/psc/psfpd1/SUPPLIER/ERP/c/AUC_MANAGE_BIDS.AUC_RESP_INQ_DTL.GBL?AUC_ID={id}&AUC_ROUND=1&AUC_VERSION={n}&BIDDER_ID=BID0000001&BIDDER_LOC=1&BIDDER_SETID=STATE&BIDDER_TYPE=B&BUSINESS_UNIT={BU}&PAGE=AUC_RESP_INQ_DTL&NoCrumbs=yes
```

Returns ~70 KB PeopleSoft HTML as Guest / Default Bidder: Event Name, Event Version, Published Date, Event End Date, contact, UNSPSC, “View Event Package”. Set `AUC_VERSION` from the listing if known; try the highest version that loads (a low version can still show a superseded solicitation ID). A follow-up POST of hidden fields (`ICSID`, `ICStateNum`, `ICAction=RESP_INQ_DL0_WK_AUC_DOWNLOAD_PB`) can list attachment names; downloading those bytes still needs the Chrome path below.

Record in `00-source/event-meta.yaml`:

```yaml
event_id: "0000037577"
business_unit: "8660"
title: ""
solicitation_id: ""          # as printed on the documents; may differ from event_id
format_type: ""              # RFx, RFP, IFB, RFI, ...
department: ""
event_version: 1
published_at: ""
end_at: ""                   # Event Details header End Date (timezone). May be stale vs addenda.
package_due_at: ""           # Key Action Date from the latest addendum / Part 1. Source of truth for submission.
contact:
  name: ""
  phone: ""
  email: ""
pre_bid:
  mandatory: false
  datetime: ""
  location: ""
unspsc: []
source_url: ""
solicitation_vehicle: ""     # open_rfp | ifb | cmas | lpa | sb_dvbe_option | rfq | other
```

The header End Date can lag the Event Package (addenda change Table 2.3.1 KADs while the header still shows the original). Record both; the Event Package / latest addendum is source of truth, not the header. Call the mismatch out as a process risk. Event Version often equals attachment count; absence of a later addendum in the package means it was not posted.

Also note vendor ads and award details if historical.

## Event package (files)

The listing page is not the RFP. Download **every** Event Package file into `00-source/package/` (solicitation body, exhibits, forms, addenda, Q&A, cost workbooks, fillable PDFs). Preserve original Cal eProcure filenames. Write `00-source/manifest.md` (file, size, one-line description after opening).

Ordered path:

1. Parse `{BU}` and `{event-id}` from the URL.
2. Pull header fields via the PeopleSoft GBL GET above. Write `event-meta.yaml`.
3. Download every attachment with **headed real Google Chrome + CDP** (not Chrome for Testing, not headless) into `00-source/package/`.
4. Open the latest addendum zip first. Comments on the attachments page are the changelog. Unzip as needed; the latest addendum zip is the working set.
5. Only if Chrome/CDP is unavailable or the event is login-walled: say so plainly and ask the user to drop the package. Still do not analyze from the blurb or the SPA shell.

### Headed Chrome + CDP download

Launch a **unique** `--user-data-dir` (do not steal the user’s daily profile):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/tmp/chrome-cale-dbg \
  --no-first-run --no-default-browser-check --disable-popup-blocking \
  "https://caleprocure.ca.gov/event/{BU}/{event-id}"
```

`--remote-allow-origins=*` is required; without it the CDP websocket handshake is 403 (“Rejected an incoming WebSocket connection”).

CDP: enable Page, Runtime, Network, Browser. Set:

```
Browser.setDownloadBehavior({ behavior: "allowAndName", downloadPath: "<event>/00-source/package", eventsEnabled: true })
```

`allowAndName` saves GUID names. Always rename from the URL/filename after each download.

In a real browser the InFlight SPA renders Event Details. Click the button whose visible text is exactly **View Event Package**. That navigates to `/pages/Events-BS3/event-bid-comments.aspx`.

Each attachment row has `id="PV_ATTACH_WRK_SCM_DOWNLOAD$N"`. `#downloadButton` (“Download Attachment”) starts as `#` / empty. Per file:

1. Click `PV_ATTACH_WRK_SCM_DOWNLOAD$N`.
2. Wait (~2–4 s) for InFlight XHR to `/nlx3/psc/.../AUC_RESP_INQ_DTL.GBL`. JSON `CaptureResults.attachmentWrapper[].Children.attachmentLink[].Properties.href` is the signed `/psc/psfpd1/view/{V2}…/Original_Filename.zip`. `#downloadButton.href` becomes the `viewredirect` twin.
3. Wait until `#downloadButton.href` **contains the expected filename** before clicking. Clicking too soon re-downloads the previous file.
4. Click `#downloadButton` (`target=_blank`). Chrome downloads via the live session.
5. Rename the GUID file using the filename from the href.

Repeat for every row (`1 of N` on the grid). Download all of them.

Python CDP: `websocket-client` against `ws://127.0.0.1:9222/devtools/page/...` with `origin="http://127.0.0.1:9222"`. Homebrew Python is PEP 668 — use a throwaway venv. Kill only the debug Chrome (`user-data-dir` process). Do not `pkill -f` a pattern that also matches the shell wrapper.

## Reading order

1. Latest addendum first — it amends dates, scoring, and required forms.
2. Bidder instructions / Part 1 — submission, mandatory fails, scoring, key staff.
3. Statement of work / Exhibit A — what is being bought.
4. Requirements workbook / Exhibit B — line-item requirements.
5. Cost worksheets / Exhibit C — what must be priced, sealed-separately rules.
6. Deliverables / Exhibit D — if present.
7. Everything else (attachments, sample contracts, SLA exhibits).

When addenda conflict with the base RFP **or** with the Event Details header, the addendum wins. Note the addendum number on any checklist item it changes.

## Public context (optional, cited)

Use web search / agency pages only to explain named systems, statutes, or the buying org’s mission **as they relate to this SOW**. Cite the URL in the analysis Sources. Skip generic “about the department” padding.

## CMAS / vehicle detection

From the documents (not from the user’s CMAS card), classify the **solicitation vehicle**:

| Vehicle | Typical signals |
|---|---|
| Open competitive RFP/IFB | PCC 6611, CDT STP, sealed cost, evaluation weights, “submit a proposal” |
| CMAS order / LPA | CMAS number requested, GSPD or CMAS terms, schedule user instructions |
| SB/DVBE option | Restricted to certified SB or DVBE |
| Informal RFQ | Dollar threshold language, simplified quote |

Write `solicitation_vehicle` into `event-meta.yaml` and `master-checklist.yaml`. Later skills use it to decide whether CMAS is enough to prime.
