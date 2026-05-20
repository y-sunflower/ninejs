import * as d3 from "d3-selection";

export default class PlotSVGParser {
  constructor(svg, tooltip, tooltip_x_shift, tooltip_y_shift, sanitizer) {
    this.svg = svg;
    this.tooltip = tooltip;
    this.tooltip_x_shift = tooltip_x_shift;
    this.tooltip_y_shift = tooltip_y_shift;
    this.sanitizer = sanitizer ?? globalThis.DOMPurify;
    this.tooltip_sanitize_config = { USE_PROFILES: { html: true } };
  }

  findBars(svg, axes_class) {
    const bars = svg.selectAll(`g#${axes_class} g[id^="PolyCollection_"] path`);

    bars.attr("class", "bar plot-element");
    return bars;
  }

  findPoints(svg, axes_class, tooltip_groups) {
    const points = svg.selectAll(
      `g#${axes_class} g[id^="PathCollection"] path`,
    );

    points.each(function (_, i) {
      d3.select(this).attr("data-group", tooltip_groups[i]);
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
    const value = label == null ? "" : String(label);

    if (!this.sanitizer || typeof this.sanitizer.sanitize !== "function") {
      this.tooltip.text(value);
      return;
    }

    this.tooltip.html(
      this.sanitizer.sanitize(value, this.tooltip_sanitize_config),
    );
  }

  setHoverEffect(plot_element, tooltip_labels, tooltip_groups, show_tooltip) {
    const self = this;
    plot_element
      .on("mouseover", function (event, d) {
        const nodes = plot_element.nodes();
        let i = nodes.indexOf(this);

        const hovered_group = tooltip_groups[i];
        plot_element.classed("not-hovered", true);
        plot_element
          .filter((_, j) => {
            return tooltip_groups[j] === hovered_group;
          })
          .classed("not-hovered", false)
          .classed("hovered", true);

        self.tooltip
          .style("display", show_tooltip)
          .style("left", event.pageX + self.tooltip_x_shift + "px")
          .style("top", event.pageY + self.tooltip_y_shift + "px");
        self.setTooltipContent(tooltip_labels[i]);
      })
      .on("mouseout", function () {
        plot_element.classed("not-hovered", false).classed("hovered", false);
        self.tooltip.style("display", "none");
      });
  }
}
