from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DATA_SOURCE = ROOT / "data-source"
PROJECTS_DIR = ROOT / "projects"
SITE_URL = "https://mahmood726-cyber.github.io/portfolio-catalog/"
REPO_URL = "https://github.com/mahmood726-cyber/portfolio-catalog"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def optional_text(text: str) -> str:
    value = compact(text)
    if value in {"-", "--", "---", "—", "n/a", "N/A"}:
        return ""
    return value


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "record"


def record_key(record_id: str, name: str, path: str) -> str:
    return "::".join([compact(record_id).lower(), compact(name).lower(), compact(path).lower()])


def percent(count: int, total: int) -> float:
    return round((count / total) * 100, 1) if total else 0.0


def storage_class(path: str) -> str:
    value = compact(path).lower()
    if not value or value.startswith("("):
        return "Generic reference"
    if value.startswith("c:\\models\\"):
        return "Models tree"
    if value.startswith("c:\\projects\\"):
        return "Projects tree"
    if value.startswith("c:\\html apps\\"):
        return "HTML apps tree"
    if value.startswith("c:\\users\\user\\"):
        return "User workspace"
    if re.fullmatch(r"c:\\[^\\]+\\?", value):
        return "Root-level C drive"
    return "Specific local path"


def public_tier_name(value: str) -> str:
    return compact(re.sub(r"\s*\(C:\\[^)]*\)", "", value))


def schema_kind(project_type: str, tier: str) -> str:
    type_text = compact(project_type).lower()
    if tier == "Tier 8":
        return "LearningResource"
    if "dataset" in type_text:
        return "Dataset"
    if any(token in type_text for token in ("app", "site", "pipeline", "package", "model", "dashboard", "project")):
        return "SoftwareSourceCode"
    return "CreativeWork"


def fair_points(total: int) -> int:
    if total >= 70:
        return 20
    if total >= 60:
        return 15
    if total >= 50:
        return 10
    if total >= 40:
        return 7
    if total > 0:
        return 4
    return 0


def discoverability_score(
    status_resolved: bool,
    has_live: bool,
    publish_signal: bool,
    code_signal: bool,
    has_paper: bool,
    has_protocol: bool,
    fair_total: int,
) -> int:
    score = 0
    score += 20 if status_resolved else 0
    score += 15 if has_live else 0
    score += 15 if publish_signal else 0
    score += 10 if code_signal else 0
    score += 10 if has_paper else 0
    score += 10 if has_protocol else 0
    score += fair_points(fair_total)
    return min(score, 100)


def discoverability_band(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def primary_gap(record: dict) -> str:
    if not record["statusResolved"]:
        return "Resolve lifecycle label"
    if not record["publishSignal"]:
        return "Add public Pages delivery"
    if record["fairTotal"] < 60:
        return "Raise FAIR metadata"
    if not (record["hasPaper"] and record["hasProtocol"]):
        return "Complete manuscript bundle"
    if not record["codeSignal"]:
        return "Add code or test surface"
    return "Maintain current record"


def build_schema_record(record: dict) -> dict:
    return {
        "@type": record["schemaType"],
        "@id": record["recordUrl"] + "#record",
        "name": record["name"],
        "url": record["recordUrl"],
        "description": record["description"],
        "identifier": record["id"],
        "keywords": record["keywords"],
        "creativeWorkStatus": record["resolvedStatus"],
        "dateModified": record["generatedAt"],
        "isPartOf": {"@type": "DataCatalog", "@id": SITE_URL + "#catalog"},
    }


def project_page(record: dict) -> str:
    schema_json = json.dumps(build_schema_record(record), indent=2)
    reasons = "".join(f"<li>{escape(reason)}</li>" for reason in record["reasons"])
    keywords = "".join(f"<span class=\"pill\">{escape(keyword)}</span>" for keyword in record["keywords"])
    evidence = [
        f"Live evidence: {'Yes' if record['hasLiveEvidence'] else 'No'}",
        f"Public Pages signal: {'Yes' if record['publishSignal'] else 'No'}",
        f"Code signal: {'Yes' if record['codeSignal'] else 'No'}",
        f"Tests signal: {'Yes' if record['hasTests'] else 'No'}",
        f"Paper artifact: {'Yes' if record['hasPaper'] else 'No'}",
        f"Protocol artifact: {'Yes' if record['hasProtocol'] else 'No'}",
        f"Triage label: {record['triageLabel'] or 'None'}",
        f"Triage confidence: {record['triageConfidence'] or 'None'}",
    ]
    evidence_html = "".join(f"<li>{escape(item)}</li>" for item in evidence)
    fact_rows = [
        ("Discoverability score", str(record["discoverabilityScore"])),
        ("Readiness score", str(record["readinessScore"])),
        ("FAIR proxy", str(record["fairTotal"])),
        ("Resolution source", record["resolutionSource"]),
        ("Storage class", record["storageClass"]),
        ("Activity band", record["activityBand"]),
        ("Last touch", record["lastTouch"] or "Not preserved"),
        ("Target journal", record["targetJournal"] or "Not preserved"),
        ("Primary gap", record["primaryGap"]),
    ]
    facts = "".join(
        f"<article class=\"fact-card\"><span class=\"metric-label\">{escape(label)}</span><strong>{escape(value)}</strong></article>"
        for label, value in fact_rows
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(record['name'])} | PortfolioCatalog</title>
  <meta name="description" content="{escape(record['description'])}">
  <link rel="stylesheet" href="../styles.css">
  <script type="application/ld+json">
{schema_json}
  </script>
</head>
<body>
  <div class="record-shell">
    <header class="hero record-header">
      <div>
        <p class="eyebrow">Catalog Record</p>
        <h1 class="record-title">{escape(record['name'])}</h1>
        <p class="hero-text">{escape(record['description'])}</p>
        <div class="pill-row">
          <span class="pill {escape(record['discoverabilityBand'])}">{escape(record['discoverabilityBand'])} discoverability</span>
          <span class="pill">{escape(record['tier'])}</span>
          <span class="pill">{escape(record['resolvedStatus'])}</span>
          <span class="pill">{escape(record['type'])}</span>
        </div>
      </div>
      <div class="fact-grid">
        <article class="fact-card"><span class="metric-label">Discoverability</span><strong>{record['discoverabilityScore']}</strong></article>
        <article class="fact-card"><span class="metric-label">Readiness</span><strong>{record['readinessScore']}</strong></article>
        <article class="fact-card"><span class="metric-label">FAIR proxy</span><strong>{record['fairTotal']}</strong></article>
      </div>
    </header>
    <main class="record-grid">
      <section class="panel">
        <div class="section-head"><p class="eyebrow">Snapshot Summary</p><h2>Metadata</h2></div>
        <div class="fact-grid">{facts}</div>
      </section>
      <section class="panel">
        <div class="section-head"><p class="eyebrow">Signals</p><h2>Evidence Surface</h2></div>
        <ul class="fact-list">{evidence_html}</ul>
      </section>
      <section class="panel">
        <div class="section-head"><p class="eyebrow">Description</p><h2>Snapshot Detail</h2></div>
        <p class="hero-text">{escape(record['detail'])}</p>
        <p class="status-note">Source note: {escape(record['statusNote'])}</p>
      </section>
      <section class="panel">
        <div class="section-head"><p class="eyebrow">Reasons</p><h2>Why This Score</h2></div>
        <ul class="reason-list">{reasons}</ul>
      </section>
      <section class="panel panel-wide">
        <div class="section-head"><p class="eyebrow">Keywords</p><h2>Discovery Terms</h2></div>
        <div class="pill-row">{keywords}</div>
      </section>
    </main>
    <footer class="panel">
      <div class="footer-links">
        <a class="mini-link" href="../index.html"><strong>Back to catalog</strong><span>Return to the root dashboard.</span></a>
        <a class="mini-link" href="../catalog.jsonld"><strong>DCAT record set</strong><span>Machine-readable catalog export.</span></a>
        <a class="mini-link" href="../schema-catalog.jsonld"><strong>Schema graph</strong><span>Structured metadata graph.</span></a>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    portfolio = load_json(DATA_SOURCE / "portfolio-data.snapshot.json")
    drive = load_json(DATA_SOURCE / "folder-scan.snapshot.json")
    ops = load_json(DATA_SOURCE / "ops-readiness.snapshot.json")
    fair = load_json(DATA_SOURCE / "fair-scores.snapshot.json")

    scan_map = {compact(scan["path"]).lower(): scan for scan in drive["scans"]}
    ops_map = {record_key(item["id"], item["name"], item["path"]): item for item in ops["projects"]}
    fair_map = {record_key(item["id"], item["name"], item["path"]): item for item in fair["scores"]}

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    for html_file in PROJECTS_DIR.glob("*.html"):
        html_file.unlink()

    records = []
    dcat_datasets = []
    schema_graph = [
        {
            "@type": "DataCatalog",
            "@id": SITE_URL + "#catalog",
            "name": "PortfolioCatalog",
            "url": SITE_URL,
            "description": "Public discovery catalog for the indexed C-drive research portfolio.",
        }
    ]

    for item in portfolio["portfolio"]:
        key = record_key(item["id"], item["name"], item["path"])
        ops_item = ops_map.get(key, {})
        fair_item = fair_map.get(key, {})
        scan_item = scan_map.get(compact(item["path"]).lower(), {})

        resolved_status = compact(ops_item.get("resolvedStatus") or item.get("statusLabel") or "Needs triage")
        status_resolved = bool(ops_item.get("statusResolved", item.get("statusExplicit", False)))
        fair_total = int(ops_item.get("fairTotal") or fair_item.get("scores", {}).get("total", 0))
        has_live = bool(ops_item.get("hasLivePath", scan_item.get("exists", False)))
        publish_signal = bool(ops_item.get("publishSignal", scan_item.get("hasIndexHtml", False) and scan_item.get("hasE156Bundle", False)))
        code_signal = bool(ops_item.get("codeSignal", scan_item.get("hasTestsMarker", False) or scan_item.get("hasManifest", False)))
        has_paper = bool(ops_item.get("hasPaper", scan_item.get("hasPaperArtifact", False)))
        has_protocol = bool(ops_item.get("hasProtocol", scan_item.get("hasProtocolArtifact", False)))
        has_tests = bool(ops_item.get("hasTests", scan_item.get("hasTestsMarker", False)))
        readiness = int(ops_item.get("readinessScore", 0))
        score = discoverability_score(status_resolved, has_live, publish_signal, code_signal, has_paper, has_protocol, fair_total)
        slug = f"{slugify(item['name'])}-{slugify(item['id'])}"
        record_url = SITE_URL + f"projects/{slug}.html"
        target_journal = optional_text(item.get("row", {}).get("Target Journal", ""))
        last_touch = optional_text(item.get("row", {}).get("Last Touch", ""))

        record = {
            "id": item["id"],
            "name": item["name"],
            "slug": slug,
            "recordUrl": record_url,
            "tier": item["tierShortName"],
            "tierName": public_tier_name(item["tierName"]),
            "type": item["type"],
            "schemaType": schema_kind(item["type"], item["tierShortName"]),
            "statusExplicit": bool(item.get("statusExplicit", False)),
            "statusNote": compact(item.get("statusNote", "")),
            "resolvedStatus": resolved_status,
            "statusResolved": status_resolved,
            "resolutionSource": compact(ops_item.get("resolutionSource", "explicit" if item.get("statusExplicit") else "unresolved")),
            "triageLabel": compact(ops_item.get("triageLabel", "")),
            "triageConfidence": compact(ops_item.get("triageConfidence", "")),
            "readinessScore": readiness,
            "fairTotal": fair_total,
            "fairBand": compact(ops_item.get("fairBand", fair_item.get("band", ""))),
            "discoverabilityScore": score,
            "discoverabilityBand": discoverability_band(score),
            "hasLiveEvidence": has_live,
            "publishSignal": publish_signal,
            "codeSignal": code_signal,
            "hasTests": has_tests,
            "hasPaper": has_paper,
            "hasProtocol": has_protocol,
            "activityBand": compact(ops_item.get("activityBand", scan_item.get("activityBand", "unknown"))),
            "storageClass": storage_class(item["path"]),
            "detail": compact(item.get("detail") or f"{item['type']} in {item['tierShortName']}."),
            "description": compact(
                f"{item['name']} is cataloged as {item['type']} in {item['tierShortName']} "
                f"with {resolved_status.lower()} status, discoverability score {score}/100, "
                f"and readiness score {readiness}/100."
            ),
            "lastTouch": last_touch,
            "targetJournal": target_journal,
            "reasons": ops_item.get("reasons", [compact(item.get("detail", "")) or "Snapshot-derived project record."]),
            "keywords": [
                keyword
                for keyword in [
                    item["tierShortName"],
                    compact(item["type"]),
                    resolved_status,
                    discoverability_band(score),
                    compact(ops_item.get("primaryAction", "")),
                    target_journal,
                ]
                if keyword
            ],
            "generatedAt": generated_at,
        }
        record["primaryGap"] = primary_gap(record)
        records.append(record)
        write_text(PROJECTS_DIR / f"{slug}.html", project_page(record))
        dcat_datasets.append(
            {
                "@id": record_url,
                "@type": "dcat:Dataset",
                "dct:identifier": record["id"],
                "dct:title": record["name"],
                "dct:description": record["description"],
                "dct:type": record["type"],
                "dct:modified": generated_at,
                "dcat:landingPage": {"@id": record_url},
                "dcat:keyword": record["keywords"],
            }
        )
        schema_graph.append(build_schema_record(record))

    records.sort(key=lambda item: (-item["discoverabilityScore"], -item["readinessScore"], item["name"].lower(), item["id"]))
    tracked_projects = len(records)
    high_discoverability = sum(item["discoverabilityScore"] >= 70 for item in records)
    resolved_status = sum(item["statusResolved"] for item in records)
    strong_public = sum(item["statusResolved"] and item["publishSignal"] and item["discoverabilityScore"] >= 70 for item in records)
    evidence_rich = sum(item["hasLiveEvidence"] and item["hasPaper"] and item["hasProtocol"] for item in records)

    gap_counter = Counter()
    tier_groups = defaultdict(list)
    type_groups = Counter()
    for record in records:
        tier_groups[record["tier"]].append(record)
        type_groups[record["type"]] += 1
        if not record["statusResolved"]:
            gap_counter["Needs resolved lifecycle label"] += 1
        if not record["publishSignal"]:
            gap_counter["Needs public Pages delivery"] += 1
        if record["fairTotal"] < 60:
            gap_counter["Needs FAIR metadata lift"] += 1
        if not (record["hasPaper"] and record["hasProtocol"]):
            gap_counter["Needs manuscript bundle"] += 1
        if not record["codeSignal"]:
            gap_counter["Needs code or test surface"] += 1

    tier_summary = []
    for tier, items in tier_groups.items():
        tier_summary.append(
            {
                "tier": tier,
                "count": len(items),
                "meanDiscoverability": round(mean(item["discoverabilityScore"] for item in items), 1),
                "strongRecords": sum(item["discoverabilityScore"] >= 70 for item in items),
                "resolvedStatuses": sum(item["statusResolved"] for item in items),
            }
        )
    tier_summary.sort(key=lambda item: (-item["meanDiscoverability"], item["tier"]))

    data = {
        "project": {
            "name": "PortfolioCatalog",
            "version": "0.1.0",
            "generatedAt": generated_at,
            "designBasis": [
                "DCAT 3 and Schema.org public metadata exports",
                "Static landing page generated for every indexed project",
                "Snapshot-first build over portfolio, drive, operations, and FAIR layers",
            ],
            "links": {
                "repo": REPO_URL,
                "site": SITE_URL,
                "catalogJsonld": SITE_URL + "catalog.jsonld",
                "schemaJsonld": SITE_URL + "schema-catalog.jsonld",
                "sitemap": SITE_URL + "sitemap.xml",
                "e156": SITE_URL + "e156-submission/",
            },
        },
        "metrics": {
            "trackedProjects": tracked_projects,
            "landingPages": tracked_projects,
            "dcatDatasets": tracked_projects,
            "schemaRecords": tracked_projects,
            "meanDiscoverability": round(mean(item["discoverabilityScore"] for item in records), 1),
            "highDiscoverabilityCount": high_discoverability,
            "highDiscoverabilityPercent": percent(high_discoverability, tracked_projects),
            "resolvedStatusCount": resolved_status,
            "resolvedStatusPercent": percent(resolved_status, tracked_projects),
            "strongPublicRecordCount": strong_public,
            "strongPublicRecordPercent": percent(strong_public, tracked_projects),
            "evidenceRichCount": evidence_rich,
            "evidenceRichPercent": percent(evidence_rich, tracked_projects),
        },
        "gapBreakdown": [{"label": label, "count": count} for label, count in gap_counter.most_common()],
        "tiers": tier_summary,
        "types": [{"type": label, "count": count} for label, count in type_groups.most_common()],
        "projects": records,
    }

    write_json(ROOT / "catalog-records.json", {"project": "PortfolioCatalog", "generatedAt": generated_at, "overview": data["metrics"], "records": records})
    write_json(ROOT / "data.json", data)
    write_text(ROOT / "data.js", "window.PORTFOLIO_CATALOG_DATA = " + json.dumps(data, indent=2) + ";\n")
    write_json(
        ROOT / "catalog.jsonld",
        {
            "@context": {"dcat": "http://www.w3.org/ns/dcat#", "dct": "http://purl.org/dc/terms/"},
            "@id": SITE_URL + "catalog.jsonld",
            "@type": "dcat:Catalog",
            "dct:title": "PortfolioCatalog",
            "dct:description": "Public discovery catalog for the indexed C-drive research portfolio.",
            "dct:modified": generated_at,
            "dcat:landingPage": {"@id": SITE_URL},
            "dcat:dataset": dcat_datasets,
        },
    )
    write_json(ROOT / "schema-catalog.jsonld", {"@context": "https://schema.org", "@graph": schema_graph})

    sitemap_urls = [
        SITE_URL,
        SITE_URL + "catalog.jsonld",
        SITE_URL + "schema-catalog.jsonld",
        SITE_URL + "e156-submission/",
        SITE_URL + "e156-submission/assets/dashboard.html",
    ] + [record["recordUrl"] for record in records]
    sitemap_lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
    ]
    for url in sitemap_urls:
        sitemap_lines.append("  <url>")
        sitemap_lines.append(f"    <loc>{escape(url)}</loc>")
        sitemap_lines.append(f"    <lastmod>{generated_at}</lastmod>")
        sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>")
    write_text(ROOT / "sitemap.xml", "\n".join(sitemap_lines) + "\n")

    print(
        "Built PortfolioCatalog "
        f"({tracked_projects} landing pages, "
        f"{data['metrics']['highDiscoverabilityPercent']:.1f}% high discoverability, "
        f"{data['metrics']['strongPublicRecordPercent']:.1f}% strong public records)."
    )


if __name__ == "__main__":
    main()
