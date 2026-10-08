document.addEventListener("DOMContentLoaded", () => {
  const section = document.getElementById("chart-section");
  const cityNameEl = document.getElementById("chart-city-name");
  const canvas = document.getElementById("chart-canvas");
  let chart = null;
  let selectedIndex = null;
  let currentCity = null;

  const TEMP_PADDING = 2;
  const colorScheme = window.matchMedia("(prefers-color-scheme: light)");

  function themeColors() {
    const style = getComputedStyle(document.body);
    const token = (name) => style.getPropertyValue(name).trim();
    return {
      accent: token("--site-accent"),
      muted: token("--site-muted"),
      border: token("--site-border"),
    };
  }

  function applyTheme() {
    if (!chart) return;
    const colors = themeColors();
    const dataset = chart.data.datasets[0];
    dataset.borderColor = colors.accent;
    dataset.backgroundColor = `${colors.accent}26`;
    for (const axis of [chart.options.scales.x, chart.options.scales.y]) {
      axis.ticks.color = colors.muted;
      axis.grid.color = colors.border;
    }
    chart.update();
  }

  function openChart(index) {
    currentCity = window.CITY_WEATHER[index];
    cityNameEl.textContent = `${currentCity.name} — Today`;
    section.classList.add("open");

    const temps = currentCity.hourly.map((h) => h.temp_c);
    const data = {
      labels: currentCity.hourly.map((h) => h.label),
      datasets: [
        {
          label: "Temp (°C)",
          data: temps,
          tension: 0.35,
          fill: true,
          pointRadius: 3,
        },
      ],
    };
    const suggestedMin = Math.min(...temps) - TEMP_PADDING;
    const suggestedMax = Math.max(...temps) + TEMP_PADDING;

    if (chart) {
      chart.data = data;
      chart.options.scales.y.suggestedMin = suggestedMin;
      chart.options.scales.y.suggestedMax = suggestedMax;
    } else {
      chart = new Chart(canvas, {
        type: "line",
        data,
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: (ctx) => currentCity.hourly[ctx.dataIndex].emoji,
              },
            },
          },
          scales: {
            x: { ticks: {}, grid: {} },
            y: {
              ticks: {},
              grid: {},
              suggestedMin,
              suggestedMax,
            },
          },
        },
      });
    }
    applyTheme();
  }

  colorScheme.addEventListener("change", applyTheme);

  function closeChart() {
    section.classList.remove("open");
    document
      .querySelectorAll(".city-card")
      .forEach((c) => c.classList.remove("selected"));
    selectedIndex = null;
  }

  document.querySelectorAll(".city-card").forEach((card) => {
    card.addEventListener("click", () => {
      const index = card.dataset.index;
      const city = window.CITY_WEATHER[index];
      if (!city.hourly || city.hourly.length === 0) return;

      if (selectedIndex === index) {
        closeChart();
        return;
      }

      document
        .querySelectorAll(".city-card")
        .forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
      selectedIndex = index;
      openChart(index);
      section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });
});
