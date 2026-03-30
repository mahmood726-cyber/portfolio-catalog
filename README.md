# PortfolioCatalog

PortfolioCatalog is a standalone public catalog layer for the C-drive research portfolio.

## Why this exists

The portfolio now has registry, FAIR, triage, drive-telemetry, provenance, RO-Crate, and FHIR layers, but it still lacked one public discovery surface that search engines and metadata harvesters can read directly.

## What it does

- fuses bundled portfolio, operations, drive, and FAIR snapshots
- generates one public landing page for every indexed project
- exports a DCAT 3 catalog in `catalog.jsonld`
- exports a Schema.org graph in `schema-catalog.jsonld`
- ships `data.json` and `data.js` for the static dashboard
- writes `sitemap.xml` for GitHub Pages indexing

## Outputs

- `catalog-records.json` - sanitized public records for all indexed projects
- `catalog.jsonld` - DCAT 3 catalog export
- `schema-catalog.jsonld` - Schema.org catalog export
- `projects/` - generated public landing pages
- `data.json` and `data.js` - dashboard payloads
- `e156-submission/` - paper, protocol, metadata, and reader page

## Rebuild

Run:

`python C:\Users\user\PortfolioCatalog\scripts\build_portfolio_catalog.py`

## Scope note

This project improves public discovery and machine readability. It does not certify scientific quality, legal release status, or external repository availability for every underlying project.
