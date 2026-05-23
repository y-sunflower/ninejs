const plotData = JSON.parse(document.getElementById("plot-data").textContent);
const areas = plotData.axes?.axes_1?.areas ?? {};
const labels = areas.tooltip_labels ?? [];
const groups = areas.tooltip_groups ?? [];

document.querySelectorAll(".area").forEach((area, i) => {
  const label = String(labels[i] ?? "");
  const group = String(groups[i] ?? "");
  area.classList.add(label === group ? "aggregate-layer" : "detail-layer");
});
