import * as d3 from "d3-selection";

export default class PlotSVGParser {
  constructor(svg, tooltip, tooltip_x_shift, tooltip_y_shift) {
    this.svg = svg;
    this.tooltip = tooltip;
    this.tooltip_x_shift = tooltip_x_shift;
    this.tooltip_y_shift = tooltip_y_shift;
  }

  findBars(svg, axes_class) {
    // select all #patch within the specific axes
    const bars = svg.selectAll(`g#${axes_class} g[id^="PolyCollection_"] path`);

    bars.attr("class", "bar plot-element");
    return bars;
  }

  findPoints(svg, axes_class, tooltip_groups) {
    const self = this;
    const points = svg.selectAll(
      `g#${axes_class} g[id^="PathCollection"] path`
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
    // select all <path> of FillBetweenPolyCollection elements within the specific axes
    const areas = svg.selectAll(
      `g#${axes_class} g[id^="FillBetweenPolyCollection"] path`
    );
    areas.attr("class", "area plot-element");
    return areas;
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
          .style("top", event.pageY + self.tooltip_y_shift + "px")
          .html(tooltip_labels[i]);
      })
      .on("mouseout", function () {
        plot_element.classed("not-hovered", false).classed("hovered", false);
        self.tooltip.style("display", "none");
      });
  }
}
