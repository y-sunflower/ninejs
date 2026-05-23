import * as d3 from "d3";
import {
  applyHoverRecord,
  clearHoverEffects,
  positionTooltip,
  setHoverEffect,
  setTooltipContent,
} from "./PlotParserHover.js";
import {
  clearActiveNearestHover,
  closestPlotElement,
  ensureNearestHoverPanel,
  getDirectHoverRecord,
  getHoverRecords,
  getNearestAnchors,
  setNearestHoverEffect,
  updateNearestHover,
} from "./PlotParserNearestHover.js";
import {
  clientPointToSvg,
  clientPointToSvgFromViewBox,
  eventToSvgPoint,
  getAttributeBBox,
  getAxesClipBounds,
  getBBoxAnchorPoints,
  getClipPathId,
  getNodeAnchorPoints,
  getNodeBBox,
  getPanelBounds,
  getPathSamplePoints,
  getSvgViewBox,
  isFiniteBBox,
  isFinitePoint,
  nodePointToSvg,
  numberAttribute,
  pointInBounds,
} from "./PlotParserGeometry.js";

export default class PlotSVGParser {
  constructor(svg, tooltip, tooltip_x_shift, tooltip_y_shift, sanitizer) {
    this.svg = svg;
    this.tooltip = tooltip;
    this.tooltip_x_shift = tooltip_x_shift;
    this.tooltip_y_shift = tooltip_y_shift;
    this.sanitizer = sanitizer ?? globalThis.DOMPurify;
    this.tooltip_sanitize_config = { USE_PROFILES: { html: true } };
    this.path_sample_spacing = 12;
    this.max_path_samples = 48;
  }

  findBars(svg, axes_class, tooltip_groups = []) {
    const bars = svg.selectAll(`g#${axes_class} g[id^="PolyCollection_"] path`);

    let barIndex = 0;
    bars.each(function () {
      d3.select(this).attr("data-group", tooltip_groups[barIndex]);
      barIndex += 1;
    });

    bars.attr("class", "bar plot-element");
    return bars;
  }

  findPoints(svg, axes_class, tooltip_groups) {
    const pointCollections = svg.selectAll(
      `g#${axes_class} g[id^="PathCollection"]`,
    );
    let points = pointCollections.selectAll("use");

    if (points.empty()) {
      points = pointCollections.selectAll("path");
    }

    let pointIndex = 0;
    points.each(function () {
      d3.select(this).attr("data-group", tooltip_groups[pointIndex]);
      pointIndex += 1;
    });
    points.attr("class", "point plot-element");
    return points;
  }

  findLines(svg, axes_class) {
    const lines = svg
      .selectAll(`g#${axes_class} g[id^="line2d"] path`)
      .filter(function () {
        return !this.closest('g[id^="matplotlib.axis"]');
      });

    lines.attr("class", "line plot-element");
    return lines;
  }

  findAreas(svg, axes_class) {
    const areas = svg.selectAll(
      `g#${axes_class} g[id^="FillBetweenPolyCollection"] path`,
    );
    areas.attr("class", "area plot-element");
    return areas;
  }

  findPolygons(svg, axes_class) {
    const polygons = svg.selectAll(
      `g#${axes_class} g[id^="PatchCollection_"] path`,
    );
    polygons.attr("class", "polygon plot-element");

    return polygons;
  }

  getSvgSummary(svg, axes_config) {
    const axes_nodes = svg.selectAll('g[id^="axes_"]').nodes();
    const plot_area_ids = axes_nodes.map((node) => node.id);
    const configured_plot_area_ids = Object.keys(axes_config || {});
    const unconfigured_plot_area_ids = plot_area_ids.filter((id) => {
      return !configured_plot_area_ids.includes(id);
    });
    const dimensions =
      [svg.attr("width"), svg.attr("height")].filter(Boolean).join(" x ") ||
      "unknown size";

    const summary_parts = [
      `SVG ${dimensions};`,
      `Found ${this._formatCount(plot_area_ids.length, "plot area")} ${this._formatIds(plot_area_ids)}.`,
    ];

    if (unconfigured_plot_area_ids.length > 0) {
      summary_parts.push(
        `Will ignore ${this._formatCount(unconfigured_plot_area_ids.length, "unconfigured plot area")} ${this._formatIds(unconfigured_plot_area_ids)}.`,
      );
    }

    return summary_parts.join(" ");
  }

  getAxesSummary(axes_class, plot_elements) {
    return {
      axesClass: axes_class,
      plotElements: {
        points: this._selectionSize(plot_elements.points),
        lines: this._selectionSize(plot_elements.lines),
        bars: this._selectionSize(plot_elements.bars),
        areas: this._selectionSize(plot_elements.areas),
        polygons: this._selectionSize(plot_elements.polygons),
      },
    };
  }

  logParseSummary(svg_summary, axes_summaries) {
    if (typeof console === "undefined") {
      return;
    }

    if (typeof console.groupCollapsed === "function") {
      console.groupCollapsed("[ninejs] parsed chart");
    } else {
      console.log("[ninejs] parsed chart");
    }

    console.log(`[ninejs] ${svg_summary}`);

    const table_rows = axes_summaries.map((summary) => {
      return {
        axes: summary.axesClass,
        points: summary.plotElements.points,
        lines: summary.plotElements.lines,
        bars: summary.plotElements.bars,
        areas: summary.plotElements.areas,
        polygons: summary.plotElements.polygons,
      };
    });

    console.table(table_rows);
    console.groupEnd();
  }

  _selectionSize(selection) {
    if (!selection || typeof selection.size !== "function") {
      return 0;
    }

    return selection.size();
  }

  _formatCount(count, noun) {
    if (count === 1) {
      return `1 ${noun}`;
    }

    return `${count} ${noun}s`;
  }

  _formatIds(ids) {
    if (ids.length === 0) {
      return "(none)";
    }

    return `(${ids.join(", ")})`;
  }

  setTooltipContent(label) {
    return setTooltipContent(this, label);
  }

  clearHoverEffects(hover_configs) {
    return clearHoverEffects(hover_configs);
  }

  positionTooltip(event, show_tooltip) {
    return positionTooltip(this, event, show_tooltip);
  }

  applyHoverRecord(record, event, hover_configs) {
    return applyHoverRecord(this, record, event, hover_configs);
  }

  setHoverEffect(
    plot_element,
    tooltip_labels,
    tooltip_groups,
    show_tooltip,
    reverse_hover = false,
  ) {
    return setHoverEffect(
      this,
      plot_element,
      tooltip_labels,
      tooltip_groups,
      show_tooltip,
      reverse_hover,
    );
  }

  setNearestHoverEffect(svg, axes_class, hover_configs) {
    return setNearestHoverEffect(this, svg, axes_class, hover_configs);
  }

  updateNearestHover(event, state) {
    return updateNearestHover(this, event, state);
  }

  ensureNearestHoverPanel(axes_node, panel_bounds) {
    return ensureNearestHoverPanel(axes_node, panel_bounds);
  }

  clearActiveNearestHover(state) {
    return clearActiveNearestHover(this, state);
  }

  getHoverRecords(hover_configs) {
    return getHoverRecords(hover_configs);
  }

  getNearestAnchors(records, bounds = null) {
    return getNearestAnchors(this, records, bounds);
  }

  getDirectHoverRecord(event, state) {
    return getDirectHoverRecord(this, event, state);
  }

  closestPlotElement(node, axes_node) {
    return closestPlotElement(node, axes_node);
  }

  getNodeAnchorPoints(node) {
    return getNodeAnchorPoints(this, node);
  }

  getPathSamplePoints(node) {
    return getPathSamplePoints(this, node);
  }

  getBBoxAnchorPoints(node, include_corners) {
    return getBBoxAnchorPoints(this, node, include_corners);
  }

  getNodeBBox(node) {
    return getNodeBBox(this, node);
  }

  getAttributeBBox(node) {
    return getAttributeBBox(node);
  }

  numberAttribute(node, name) {
    return numberAttribute(node, name);
  }

  getPanelBounds(axes_class) {
    return getPanelBounds(this, axes_class);
  }

  getAxesClipBounds(axes_class) {
    return getAxesClipBounds(this, axes_class);
  }

  getClipPathId(clip_path) {
    return getClipPathId(clip_path);
  }

  eventToSvgPoint(event) {
    return eventToSvgPoint(this, event);
  }

  clientPointToSvg(client_x, client_y) {
    return clientPointToSvg(this, client_x, client_y);
  }

  clientPointToSvgFromViewBox(client_x, client_y) {
    return clientPointToSvgFromViewBox(this, client_x, client_y);
  }

  getSvgViewBox(svg_node, rect) {
    return getSvgViewBox(svg_node, rect);
  }

  nodePointToSvg(node, x, y) {
    return nodePointToSvg(this, node, x, y);
  }

  isFinitePoint(point) {
    return isFinitePoint(point);
  }

  isFiniteBBox(bbox) {
    return isFiniteBBox(bbox);
  }

  pointInBounds(point, bounds) {
    return pointInBounds(point, bounds);
  }
}
