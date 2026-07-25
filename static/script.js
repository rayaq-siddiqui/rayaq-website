document.addEventListener("DOMContentLoaded", () => {
  const section = document.getElementById("chart-section");
  const cityNameEl = document.getElementById("chart-city-name");
  const canvas = document.getElementById("chart-canvas");
  let chart = null;
  let selectedIndex = null;

  function renderChart(index) {
    const city = window.CITY_WEATHER[index];
    cityNameEl.textContent = `${city.name} — Today`;
    section.classList.add("open");

    const data = {
      labels: city.hourly.map((h) => h.label),
      datasets: [
        {
          label: "Temp (°C)",
          data: city.hourly.map((h) => h.temp_c),
          borderColor: "#4da3ff",
          backgroundColor: "rgba(77, 163, 255, 0.15)",
          tension: 0.35,
          fill: true,
          pointRadius: 3,
        },
      ],
    };

    if (chart) {
      chart.data = data;
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
                afterLabel: (ctx) => city.hourly[ctx.dataIndex].emoji,
              },
            },
          },
          scales: {
            x: { ticks: { color: "#a3a3a3" }, grid: { color: "#2a2a2e" } },
            y: { ticks: { color: "#a3a3a3" }, grid: { color: "#2a2a2e" } },
          },
        },
      });
    }
  }

  document.querySelectorAll(".city-card").forEach((card) => {
    card.addEventListener("click", () => {
      const index = card.dataset.index;
      const city = window.CITY_WEATHER[index];
      if (!city.hourly || city.hourly.length === 0) return;

      document
        .querySelectorAll(".city-card")
        .forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
      selectedIndex = index;
      renderChart(index);
      section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });
});
