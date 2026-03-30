Mahmood Ahmad
Tahir Heart Institute
author@example.com

Protocol: PortfolioCatalog - DCAT and Schema.org Discovery Build

This protocol describes a snapshot-first cataloging study over the bundled `ResearchConstellation`, `DrivePulse`, `PortfolioOps`, and `FAIRPortfolio` artifacts. Eligible records are all indexed portfolio projects preserved in those bundled snapshots. The primary estimand is the proportion of indexed projects reaching high discoverability coverage, defined as a discoverability score of at least 70/100 after combining lifecycle resolution, live evidence, public Pages signals, code signals, manuscript artifacts, and FAIR-style maturity. Secondary outputs will report mean discoverability, strong public records, evidence-rich records, gap counts, tier-level discoverability means, a DCAT 3 export, a Schema.org graph, a sitemap, and public landing pages for every indexed project. The build process will emit `catalog-records.json`, `catalog.jsonld`, `schema-catalog.jsonld`, `data.json`, `data.js`, `projects/`, and a static dashboard. Anticipated limitations include heuristic weighting, snapshot lag, incomplete public URLs outside this repo, and the risk that discoverability does not equal scientific validity.

Outside Notes

Type: protocol
Primary estimand: proportion of indexed projects reaching high discoverability coverage
App: PortfolioCatalog v0.1
Code: repository root, scripts/build_portfolio_catalog.py, catalog.jsonld, schema-catalog.jsonld, and data-source/
Date: 2026-03-30
Validation: DRAFT

References

1. W3C. Data Catalog Vocabulary (DCAT) Version 3. W3C Recommendation. 2024.
2. Schema.org. DataCatalog. Accessed 2026-03-30.
3. Wilkinson MD, Dumontier M, Aalbersberg IJJ, et al. The FAIR Guiding Principles for scientific data management and stewardship. Sci Data. 2016;3:160018.

AI Disclosure

This protocol was drafted from versioned local artifacts and deterministic build logic. AI was used as a drafting and implementation assistant under author supervision, with the author retaining responsibility for scope, methods, and reporting choices.
