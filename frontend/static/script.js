document.addEventListener("DOMContentLoaded", () => {
  const section = document.getElementById("chart-section");
  const cityNameEl = document.getElementById("chart-city-name");
  const canvas = document.getElementById("chart-canvas");
  let chart = null;
  let selectedIndex = null;
  let currentCity = null;

  const TEMP_PADDING = 2;

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
          borderColor: "#4da3ff",
          backgroundColor: "rgba(77, 163, 255, 0.15)",
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
      chart.update();
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
            x: { ticks: { color: "#a3a3a3" }, grid: { color: "#2a2a2e" } },
            y: {
              ticks: { color: "#a3a3a3" },
              grid: { color: "#2a2a2e" },
              suggestedMin,
              suggestedMax,
            },
          },
        },
      });
    }
  }

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
