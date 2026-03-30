(function () {
  const data = window.PORTFOLIO_CATALOG_DATA;
  if (!data) {
    return;
  }

  const state = {
    search: "",
    tier: "",
    band: "",
    sort: "score",
  };

  const metricGrid = document.getElementById("metric-grid");
  const gapGrid = document.getElementById("gap-grid");
  const tierTable = document.getElementById("tier-table");
  const projectGrid = document.getElementById("project-grid");
  const resultsCopy = document.getElementById("results-copy");
  const exportLinks = document.getElementById("export-links");

  function formatPercent(value) {
    return `${Number(value).toFixed(1)}%`;
  }

  function renderMetrics() {
    const metrics = [
      {
        value: data.metrics.trackedProjects,
        label: "Indexed projects",
        note: `${data.metrics.landingPages} landing pages generated`,
      },
      {
        value: data.metrics.meanDiscoverability.toFixed(1),
        label: "Mean discoverability",
        note: `${data.metrics.highDiscoverabilityCount} high-band records`,
      },
      {
        value: formatPercent(data.metrics.resolvedStatusPercent),
        label: "Resolved status coverage",
        note: `${data.metrics.resolvedStatusCount} of ${data.metrics.trackedProjects} projects`,
      },
      {
        value: formatPercent(data.metrics.strongPublicRecordPercent),
        label: "Strong public records",
        note: `${data.metrics.strongPublicRecordCount} records with status, signal, and score`,
      },
    ];

    metricGrid.innerHTML = metrics.map((item) => `
      <article class="metric-card">
        <span class="metric-value">${item.value}</span>
        <span class="metric-label">${item.label}</span>
        <span class="metric-note">${item.note}</span>
      </article>
    `).join("");
  }

  function renderExports() {
    const links = [
      { href: data.project.links.catalogJsonld, title: "DCAT 3 Export", text: "Machine-readable public catalog" },
      { href: data.project.links.schemaJsonld, title: "Schema.org Graph", text: "Search-engine friendly metadata graph" },
      { href: data.project.links.sitemap, title: "Sitemap", text: "Project landing pages for Pages indexing" },
      { href: data.project.links.e156, title: "E156 Submission", text: "Paper, protocol, metadata, and reader" },
      { href: data.project.links.repo, title: "GitHub Repo", text: "Full code and bundled snapshots" },
    ];
    exportLinks.innerHTML = links.map((item) => `
      <a class="export-link" href="${item.href}">
        <strong>${item.title}</strong>
        <span>${item.text}</span>
      </a>
    `).join("");
  }

  function renderGaps() {
    gapGrid.innerHTML = data.gapBreakdown.map((item) => `
      <article class="chip">
        <strong>${item.label}</strong>
        <p>${item.count} projects</p>
      </article>
    `).join("");
  }

  function renderTiers() {
    tierTable.innerHTML = data.tiers.map((tier) => `
      <tr>
        <td>${tier.tier}</td>
        <td>${tier.count}</td>
        <td>${tier.meanDiscoverability.toFixed(1)}</td>
        <td>${tier.strongRecords}</td>
      </tr>
    `).join("");
  }

  function filteredProjects() {
    const search = state.search.trim().toLowerCase();
    const projects = data.projects.filter((project) => {
      if (state.tier && project.tier !== state.tier) {
        return false;
      }
      if (state.band && project.discoverabilityBand !== state.band) {
        return false;
      }
      if (!search) {
        return true;
      }
      return [
        project.name,
        project.type,
        project.tier,
        project.resolvedStatus,
        project.targetJournal,
        project.primaryGap,
        project.description,
      ].join(" ").toLowerCase().includes(search);
    });

    const sorters = {
      score: (a, b) => b.discoverabilityScore - a.discoverabilityScore || b.readinessScore - a.readinessScore || a.name.localeCompare(b.name),
      readiness: (a, b) => b.readinessScore - a.readinessScore || b.discoverabilityScore - a.discoverabilityScore || a.name.localeCompare(b.name),
      name: (a, b) => a.name.localeCompare(b.name),
    };
    return projects.sort(sorters[state.sort]);
  }

  function renderProjects() {
    const projects = filteredProjects();
    resultsCopy.textContent = `${projects.length} records shown`;
    projectGrid.innerHTML = projects.map((project) => `
      <a class="project-card" href="projects/${project.slug}.html">
        <div class="card-topline">
          <span class="pill ${project.discoverabilityBand}">${project.discoverabilityBand} discoverability</span>
          <span class="pill">${project.tier}</span>
          <span class="pill">${project.resolvedStatus}</span>
        </div>
        <div>
          <h3>${project.name}</h3>
          <p class="hero-text">${project.description}</p>
        </div>
        <div class="card-score">${project.discoverabilityScore}</div>
        <div class="pill-row">
          <span class="pill">Readiness ${project.readinessScore}</span>
          <span class="pill">FAIR ${project.fairTotal}</span>
          <span class="pill">${project.type}</span>
        </div>
        <div class="project-meta">
          <span>Storage: ${project.storageClass}</span>
          <span>Activity: ${project.activityBand}</span>
          <span>Primary gap: ${project.primaryGap}</span>
        </div>
      </a>
    `).join("");
  }

  function fillTierOptions() {
    const tierSelect = document.getElementById("tier-select");
    data.tiers.forEach((tier) => {
      const option = document.createElement("option");
      option.value = tier.tier;
      option.textContent = tier.tier;
      tierSelect.appendChild(option);
    });
  }

  function bindEvents() {
    document.getElementById("search-input").addEventListener("input", (event) => {
      state.search = event.target.value;
      renderProjects();
    });

    document.getElementById("tier-select").addEventListener("change", (event) => {
      state.tier = event.target.value;
      renderProjects();
    });

    document.getElementById("band-select").addEventListener("change", (event) => {
      state.band = event.target.value;
      renderProjects();
    });

    document.getElementById("sort-select").addEventListener("change", (event) => {
      state.sort = event.target.value;
      renderProjects();
    });
  }

  fillTierOptions();
  bindEvents();
  renderExports();
  renderMetrics();
  renderGaps();
  renderTiers();
  renderProjects();
}());
