import * as d3 from "d3";
import PlotSVGParser from "./PlotParser.js";
import { normalizeHoverConfigs } from "./PlotParserHover.js";

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
  const axes_hover_sets = [];
  const linked_hover_configs = [];

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

    const plot_elements = {};
    const hover_configs = [];
    const configured_geom_kinds = getConfiguredGeomKinds(axe_data, geom_kinds);
    for (const geom_kind of configured_geom_kinds) {
      const config_data = axe_data[geom_kind] || axe_data;
      const labels = config_data["tooltip_labels"];
      const groups = config_data["tooltip_groups"];
      const keys = config_data["hover_keys"];
      const clicks = config_data["click_handlers"];
      const elements = geom_finders[geom_kind](axes_class, groups);

      plot_elements[geom_kind] = elements;
      hover_configs.push({
        plotElements: elements,
        tooltipLabels: labels,
        tooltipGroups: groups,
        hoverKeys: keys,
        clickHandlers: clicks,
        showTooltip: labels.length === 0 ? "none" : "block",
        reverseHover: reverse_hover,
      });
    }

    normalizeHoverConfigs(hover_configs);
    axes_summaries.push(plotParser.getAxesSummary(axes_class, plot_elements));
    axes_hover_sets.push({
      axesClass: axes_class,
      hoverConfigs: hover_configs,
    });

    for (const hover_config of hover_configs) {
      if ((hover_config.hoverKeys || []).length > 0) {
        linked_hover_configs.push(hover_config);
      }
    }
  }

  for (const axes_hover_set of axes_hover_sets) {
    if (hover_nearest) {
      for (const hover_config of axes_hover_set.hoverConfigs) {
        plotParser.setClickEffect(
          hover_config.plotElements,
          hover_config.clickHandlers,
        );
      }
      plotParser.setNearestHoverEffect(
        svg,
        axes_hover_set.axesClass,
        axes_hover_set.hoverConfigs,
        linked_hover_configs,
      );
    } else {
      for (const hover_config of axes_hover_set.hoverConfigs) {
        const hover_scope =
          (hover_config.hoverKeys || []).length > 0
            ? linked_hover_configs
            : [hover_config];
        plotParser.setHoverEffect(
          hover_config.plotElements,
          hover_config.tooltipLabels,
          hover_config.tooltipGroups,
          hover_config.showTooltip,
          hover_config.reverseHover,
          hover_config.clickHandlers,
          hover_config.hoverKeys,
          hover_scope,
        );
      }
    }
  }

  if (zoomable) {
    plotParser.setZoomEffect(svg);
  }

  plotParser.logParseSummary(svg_summary, axes_summaries);
}

function getConfiguredGeomKinds(axe_data, geom_kinds) {
  const configured_geom_kinds = geom_kinds.filter((geom_kind) => {
    return Object.prototype.hasOwnProperty.call(axe_data, geom_kind);
  });

  return configured_geom_kinds.length > 0 ? configured_geom_kinds : geom_kinds;
}
