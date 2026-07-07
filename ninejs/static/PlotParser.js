/**
 * Plot parser implementation.
 * @module PlotParser
 */

import * as d3 from "d3";

/**
 * Parses a Matplotlib-generated SVG and labels plot elements for ninejs
 * interactions.
 */
export default class PlotSVGParser {
  /**
   * Create a parser for one SVG plot.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {d3.Selection} tooltip - Tooltip container selection.
   * @param {object} sanitizer - Optional DOMPurify-compatible sanitizer.
   * @param {number} nearest_sample_spacing - Pixel spacing for nearest-hover sampling.
   * @param {number} nearest_max_samples - Maximum samples used for path hit-testing.
   */
  constructor(
    svg,
    tooltip,
    sanitizer = globalThis.DOMPurify,
    nearest_sample_spacing = 12,
    nearest_max_samples = 48,
  ) {
    this.svg = svg;
    this.tooltip = tooltip;
    this.sanitizer = sanitizer;
    this.tooltip_sanitize_config = { USE_PROFILES: { html: true } };
    this.nearest_sample_spacing = nearest_sample_spacing;
    this.nearest_max_samples = nearest_max_samples;
  }

  /**
   * Find bar paths in an axes group and assign tooltip group identifiers.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {string} axes_class - Matplotlib axes group id.
   * @param {Array<string>} tooltip_groups - Tooltip group id per bar.
   * @returns {d3.Selection} Bar element selection.
   */
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

  /**
   * Find boxplot glyphs in an axes group and assign tooltip group identifiers.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {string} axes_class - Matplotlib axes group id.
   * @param {Array<string>} tooltip_groups - Tooltip group id per box.
   * @returns {d3.Selection} Box element selection.
   */
  findBoxes(svg, axes_class, tooltip_groups = []) {
    const boxes = svg.selectAll(`g#${axes_class} g[id^="PolyCollection_"] use`);

    let boxIndex = 0;
    boxes.each(function () {
      d3.select(this).attr("data-group", tooltip_groups[boxIndex]);
      boxIndex += 1;
    });

    boxes.attr("class", "box plot-element");
    return boxes;
  }

  /**
   * Find point markers in an axes group and assign tooltip group identifiers.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {string} axes_class - Matplotlib axes group id.
   * @param {Array<string>} tooltip_groups - Tooltip group id per point.
   * @returns {d3.Selection} Point element selection.
   */
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

  /**
   * Find line paths in an axes group while excluding axis decoration lines.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {string} axes_class - Matplotlib axes group id.
   * @returns {d3.Selection} Line element selection.
   */
  findLines(svg, axes_class) {
    const lines = svg
      .selectAll(`g#${axes_class} g[id^="line2d"] path`)
      .filter(function () {
        return !this.closest('g[id^="matplotlib.axis"]');
      });

    lines.attr("class", "line plot-element");
    return lines;
  }

  /**
   * Find area fill paths in an axes group.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {string} axes_class - Matplotlib axes group id.
   * @returns {d3.Selection} Area element selection.
   */
  findAreas(svg, axes_class) {
    const areas = svg.selectAll(
      `g#${axes_class} g[id^="FillBetweenPolyCollection"] path`,
    );
    areas.attr("class", "area plot-element");
    return areas;
  }

  /**
   * Find polygon paths in an axes group.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {string} axes_class - Matplotlib axes group id.
   * @returns {d3.Selection} Polygon element selection.
   */
  findPolygons(svg, axes_class) {
    const polygons = svg.selectAll(
      `g#${axes_class} g[id^="PatchCollection_"] path`,
    );
    polygons.attr("class", "polygon plot-element");

    return polygons;
  }

  /**
   * Build a short parse summary for all axes groups in the SVG.
   *
   * @param {d3.Selection} svg - SVG root selection.
   * @param {object} axes_config - Parser configuration keyed by axes id.
   * @returns {string} Human-readable SVG summary.
   */
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

  /**
   * Summarize detected plot elements for one axes group.
   *
   * @param {string} axes_class - Matplotlib axes group id.
   * @param {object} plot_elements - Element selections keyed by geom type.
   * @returns {object} Axes summary object.
   */
  getAxesSummary(axes_class, plot_elements) {
    return {
      axesClass: axes_class,
      plotElements: {
        points: this._selectionSize(plot_elements.points),
        lines: this._selectionSize(plot_elements.lines),
        bars: this._selectionSize(plot_elements.bars),
        boxes: this._selectionSize(plot_elements.boxes),
        areas: this._selectionSize(plot_elements.areas),
        polygons: this._selectionSize(plot_elements.polygons),
      },
    };
  }

  /**
   * Log the SVG and axes parse summaries to the browser console.
   *
   * @param {string} svg_summary - Human-readable SVG summary.
   * @param {Array<object>} axes_summaries - Per-axes summary objects.
   */
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
        boxes: summary.plotElements.boxes,
        areas: summary.plotElements.areas,
        polygons: summary.plotElements.polygons,
      };
    });

    console.table(table_rows);
    console.groupEnd();
  }

  /**
   * Count the elements in a D3 selection.
   *
   * @param {d3.Selection} selection - Selection to count.
   * @returns {number} Number of selected elements.
   */
  _selectionSize(selection) {
    if (!selection || typeof selection.size !== "function") {
      return 0;
    }

    return selection.size();
  }

  /**
   * Format a count and noun with simple pluralization.
   *
   * @param {number} count - Count to format.
   * @param {string} noun - Singular noun.
   * @returns {string} Formatted count.
   */
  _formatCount(count, noun) {
    if (count === 1) {
      return `1 ${noun}`;
    }

    return `${count} ${noun}s`;
  }

  /**
   * Format a list of SVG ids for log output.
   *
   * @param {Array<string>} ids - SVG ids to format.
   * @returns {string} Parenthesized ids or a none marker.
   */
  _formatIds(ids) {
    if (ids.length === 0) {
      return "(none)";
    }

    return `(${ids.join(", ")})`;
  }
}
