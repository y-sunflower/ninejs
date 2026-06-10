import * as d3 from "d3";
import PlotSVGParser from "./PlotParser.js";

export default function initPlot() {
  const container = document.getElementById("plot-container");

  const tooltip = d3.select("#tooltip");
  const svg = d3.select(container).select("svg");

  const plot_data = JSON.parse(
    document.getElementById("plot-data").textContent,
  );
  const hover_nearest = plot_data["hover_nearest"] || false;
  const reverse_hover = plot_data["reverse_hover"] || false;
  const zoomable = plot_data["zoomable"] || false;
  const axes = plot_data["axes"];

  const plotParser = new PlotSVGParser(svg, tooltip);
  const svg_summary = plotParser.getSvgSummary(svg, axes);
  const axes_summaries = [];

  const geom_finders = {
    points: (axes_class, groups) =>
      plotParser.findPoints(svg, axes_class, groups),
    lines: (axes_class) => plotParser.findLines(svg, axes_class),
    bars: (axes_class, groups) => plotParser.findBars(svg, axes_class, groups),
    areas: (axes_class) => plotParser.findAreas(svg, axes_class),
    polygons: (axes_class) => plotParser.findPolygons(svg, axes_class),
  };
  const geom_kinds = Object.keys(geom_finders);

  for (const axes_class in axes) {
    if (!axes.hasOwnProperty(axes_class)) {
      continue;
    }

    const axe_data = axes[axes_class];
    const tooltip_labels = axe_data["tooltip_labels"];
    const tooltip_groups = axe_data["tooltip_groups"];
    const click_handlers = axe_data["click_handlers"] || [];

    const plot_elements = {};
    const hover_configs = [];
    for (const geom_kind of geom_kinds) {
      // A geom kind with its own config is authoritative (even when
      // empty); an absent one inherits the axes-level config.
      const geom_data = axe_data[geom_kind];
      const labels = geom_data
        ? geom_data["tooltip_labels"] || []
        : tooltip_labels;
      const groups = geom_data
        ? geom_data["tooltip_groups"] || []
        : tooltip_groups;
      const clicks = geom_data
        ? geom_data["click_handlers"] || []
        : click_handlers;
      const elements = geom_finders[geom_kind](axes_class, groups);

      plot_elements[geom_kind] = elements;
      hover_configs.push({
        plotElements: elements,
        tooltipLabels: labels,
        tooltipGroups: groups,
        clickHandlers: clicks,
        showTooltip: labels.length === 0 ? "none" : "block",
        reverseHover: reverse_hover,
      });
    }

    axes_summaries.push(plotParser.getAxesSummary(axes_class, plot_elements));

    if (hover_nearest) {
      for (const hover_config of hover_configs) {
        plotParser.setClickEffect(
          hover_config.plotElements,
          hover_config.clickHandlers,
        );
      }
      plotParser.setNearestHoverEffect(svg, axes_class, hover_configs);
    } else {
      for (const hover_config of hover_configs) {
        plotParser.setHoverEffect(
          hover_config.plotElements,
          hover_config.tooltipLabels,
          hover_config.tooltipGroups,
          hover_config.showTooltip,
          hover_config.reverseHover,
          hover_config.clickHandlers,
        );
      }
    }
  }

  if (zoomable) {
    plotParser.setZoomEffect(svg);
  }

  plotParser.logParseSummary(svg_summary, axes_summaries);
}
