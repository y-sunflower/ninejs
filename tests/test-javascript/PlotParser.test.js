import { describe, expect, test } from "bun:test";
import { JSDOM } from "jsdom";
import { select } from "d3-selection";

import PlotSVGParser from "../../ninejs/static/PlotParser.js";

function makeParser(svgMarkup, tooltipXShift = 0, tooltipYShift = 0) {
  const dom = new JSDOM(svgMarkup);
  const window = dom.window;
  const document = window.document;
  const svg = select(document).select("svg");
  const tooltipNode = document.createElement("div");
  document.body.appendChild(tooltipNode);
  const tooltip = select(tooltipNode);
  const parser = new PlotSVGParser(svg, tooltip, tooltipXShift, tooltipYShift);

  return { document, parser, svg, tooltip, window };
}

function hasClass(document, id, className) {
  return document.querySelector(`#${id}`).classList.contains(className);
}

function dispatchMouseEvent(window, node, type, pageX, pageY) {
  node.dispatchEvent(
    new window.MouseEvent(type, {
      bubbles: true,
      pageX: pageX,
      pageY: pageY,
      clientX: pageX,
      clientY: pageY,
    }),
  );
}

function makeHoverFixture(showTooltip = "block") {
  const { document, parser, svg, tooltip, window } = makeParser(
    `
      <svg>
        <path id="point-a" class="plot-element"></path>
        <path id="point-b" class="plot-element"></path>
        <path id="point-c" class="plot-element"></path>
      </svg>
    `,
    10,
    -5,
  );
  const plotElements = svg.selectAll("path.plot-element");
  const labels = ["Alpha label", "Beta label", "Second alpha label"];
  const groups = ["alpha", "beta", "alpha"];

  parser.setHoverEffect(plotElements, labels, groups, showTooltip);

  return { document, plotElements, tooltip, window };
}

describe("PlotSVGParser element discovery", () => {
  test("findPoints discovers point paths in the requested axes", () => {
    const { document, parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="PathCollection_1">
            <path id="point-a"></path>
            <path id="point-b"></path>
          </g>
          <g id="PathCollection_extra">
            <path id="point-c"></path>
          </g>
          <g id="NotPathCollection_1">
            <path id="not-a-point"></path>
          </g>
        </g>
        <g id="axes_2">
          <g id="PathCollection_2">
            <path id="other-axes-point"></path>
          </g>
        </g>
      </svg>
    `);

    const points = parser.findPoints(svg, "axes_1", [
      "group-a",
      "group-b",
      "group-c",
    ]);

    expect(points.size()).toBe(3);
    expect(points.nodes().map((node) => node.id)).toEqual([
      "point-a",
      "point-b",
      "point-c",
    ]);
    expect(points.nodes().map((node) => node.getAttribute("class"))).toEqual([
      "point plot-element",
      "point plot-element",
      "point plot-element",
    ]);
    expect(
      points.nodes().map((node) => node.getAttribute("data-group")),
    ).toEqual(["group-a", "group-b", "group-c"]);
    expect(
      document.querySelector("#not-a-point").getAttribute("class"),
    ).toBeNull();
    expect(
      document.querySelector("#other-axes-point").getAttribute("class"),
    ).toBeNull();
  });

  test("findLines discovers plot lines and ignores Matplotlib axis lines", () => {
    const { document, parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="line2d_1">
            <path id="line-a"></path>
          </g>
          <g id="matplotlib.axis_1">
            <g id="line2d_2">
              <path id="axis-tick"></path>
            </g>
          </g>
          <g id="line2d_function">
            <path id="function-line"></path>
          </g>
        </g>
        <g id="axes_2">
          <g id="line2d_3">
            <path id="other-axes-line"></path>
          </g>
        </g>
      </svg>
    `);

    const lines = parser.findLines(svg, "axes_1");

    expect(lines.size()).toBe(2);
    expect(lines.nodes().map((node) => node.id)).toEqual([
      "line-a",
      "function-line",
    ]);
    expect(lines.nodes().map((node) => node.getAttribute("class"))).toEqual([
      "line plot-element",
      "line plot-element",
    ]);
    expect(
      document.querySelector("#axis-tick").getAttribute("class"),
    ).toBeNull();
    expect(
      document.querySelector("#other-axes-line").getAttribute("class"),
    ).toBeNull();
  });

  test("findBars discovers bar paths in the requested axes", () => {
    const { document, parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="PolyCollection_1">
            <path id="bar-a"></path>
            <path id="bar-b"></path>
          </g>
          <g id="PolyCollection_2">
            <path id="bar-c"></path>
          </g>
          <g id="NotPolyCollection_1">
            <path id="not-a-bar"></path>
          </g>
        </g>
        <g id="axes_2">
          <g id="PolyCollection_3">
            <path id="other-axes-bar"></path>
          </g>
        </g>
      </svg>
    `);

    const bars = parser.findBars(svg, "axes_1");

    expect(bars.size()).toBe(3);
    expect(bars.nodes().map((node) => node.id)).toEqual([
      "bar-a",
      "bar-b",
      "bar-c",
    ]);
    expect(bars.nodes().map((node) => node.getAttribute("class"))).toEqual([
      "bar plot-element",
      "bar plot-element",
      "bar plot-element",
    ]);
    expect(
      document.querySelector("#not-a-bar").getAttribute("class"),
    ).toBeNull();
    expect(
      document.querySelector("#other-axes-bar").getAttribute("class"),
    ).toBeNull();
  });

  test("findAreas discovers area paths in the requested axes", () => {
    const { document, parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="FillBetweenPolyCollection_1">
            <path id="area-a"></path>
            <path id="area-b"></path>
          </g>
          <g id="PolyCollection_1">
            <path id="bar-path"></path>
          </g>
          <g id="NotFillBetweenPolyCollection_1">
            <path id="not-an-area"></path>
          </g>
        </g>
        <g id="axes_2">
          <g id="FillBetweenPolyCollection_2">
            <path id="other-axes-area"></path>
          </g>
        </g>
      </svg>
    `);

    const areas = parser.findAreas(svg, "axes_1");

    expect(areas.size()).toBe(2);
    expect(areas.nodes().map((node) => node.id)).toEqual(["area-a", "area-b"]);
    expect(areas.nodes().map((node) => node.getAttribute("class"))).toEqual([
      "area plot-element",
      "area plot-element",
    ]);
    expect(
      document.querySelector("#bar-path").getAttribute("class"),
    ).toBeNull();
    expect(
      document.querySelector("#not-an-area").getAttribute("class"),
    ).toBeNull();
    expect(
      document.querySelector("#other-axes-area").getAttribute("class"),
    ).toBeNull();
  });
});

describe("PlotSVGParser parse diagnostics", () => {
  test("getSvgSummary returns a readable sentence", () => {
    const { parser, svg } = makeParser(`
      <svg width="640pt" height="480pt" viewBox="0 0 640 480">
        <g id="axes_1"></g>
        <g id="axes_2"></g>
        <g id="legend_1"></g>
      </svg>
    `);

    const summary = parser.getSvgSummary(svg, { axes_1: {} });

    expect(summary).toBe(
      "SVG 640pt x 480pt; viewBox 0 0 640 480. " +
        "Found 2 plot areas (axes_1, axes_2) and 1 legend. " +
        "Will process 1 plot area (axes_1). " +
        "Will ignore 1 unconfigured plot area (axes_2).",
    );
  });

  test("getAxesSummary counts geoms, axes, and ticks", () => {
    const { parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="matplotlib.axis_1">
            <g id="xtick_1"></g>
            <g id="xtick_2"></g>
          </g>
          <g id="matplotlib.axis_2">
            <g id="ytick_1"></g>
          </g>
          <g id="line2d_1">
            <path id="line-a"></path>
          </g>
          <g id="PathCollection_1">
            <path id="point-a"></path>
            <path id="point-b"></path>
          </g>
          <g id="PolyCollection_1">
            <path id="bar-a"></path>
          </g>
          <g id="FillBetweenPolyCollection_1">
            <path id="area-a"></path>
            <path id="area-b"></path>
            <path id="area-c"></path>
          </g>
        </g>
      </svg>
    `);

    const points = parser.findPoints(svg, "axes_1", ["a", "b"]);
    const lines = parser.findLines(svg, "axes_1");
    const bars = parser.findBars(svg, "axes_1");
    const areas = parser.findAreas(svg, "axes_1");

    const summary = parser.getAxesSummary(svg, "axes_1", {
      points: points,
      lines: lines,
      bars: bars,
      areas: areas,
    });

    expect(summary.axesClass).toBe("axes_1");
    expect(summary.plotElements).toEqual({
      points: 2,
      lines: 1,
      bars: 1,
      areas: 3,
    });
    expect(summary.matplotlibAxes).toBe(2);
    expect(summary.xTicks).toBe(2);
    expect(summary.yTicks).toBe(1);
  });

  test("logParseSummary writes structured diagnostics to console", () => {
    const { parser } = makeParser("<svg></svg>");
    const originalConsole = globalThis.console;
    const calls = [];

    globalThis.console = {
      groupCollapsed: (...args) => calls.push(["groupCollapsed", args]),
      log: (...args) => calls.push(["log", args]),
      table: (...args) => calls.push(["table", args]),
      groupEnd: (...args) => calls.push(["groupEnd", args]),
    };

    try {
      parser.logParseSummary("SVG 640pt x 480pt; found 1 plot area.", [
        {
          axesClass: "axes_1",
          plotElements: { points: 2, lines: 1, bars: 0, areas: 0 },
          matplotlibAxes: 2,
          xTicks: 3,
          yTicks: 4,
        },
      ]);
    } finally {
      globalThis.console = originalConsole;
    }

    expect(calls[0]).toEqual(["groupCollapsed", ["[ninejs] parsed chart"]]);
    expect(calls[1]).toEqual([
      "log",
      ["[ninejs] SVG 640pt x 480pt; found 1 plot area."],
    ]);
    expect(calls[2]).toEqual([
      "table",
      [
        [
          {
            axes: "axes_1",
            points: 2,
            lines: 1,
            bars: 0,
            areas: 0,
            matplotlibAxes: 2,
            xTicks: 3,
            yTicks: 4,
          },
        ],
      ],
    ]);
    expect(calls).toHaveLength(4);
    expect(calls.at(-1)).toEqual(["groupEnd", []]);
  });
});

describe("PlotSVGParser hover effects", () => {
  test("mouseover highlights the matching group and updates tooltip state", () => {
    const { document, tooltip, window } = makeHoverFixture();

    dispatchMouseEvent(
      window,
      document.querySelector("#point-a"),
      "mouseover",
      100,
      200,
    );

    expect(hasClass(document, "point-a", "hovered")).toBe(true);
    expect(hasClass(document, "point-a", "not-hovered")).toBe(false);
    expect(hasClass(document, "point-c", "hovered")).toBe(true);
    expect(hasClass(document, "point-c", "not-hovered")).toBe(false);
    expect(hasClass(document, "point-b", "hovered")).toBe(false);
    expect(hasClass(document, "point-b", "not-hovered")).toBe(true);
    expect(tooltip.style("display")).toBe("block");
    expect(tooltip.html()).toBe("Alpha label");
    expect(tooltip.style("left")).toBe("110px");
    expect(tooltip.style("top")).toBe("195px");
  });

  test("mouseout clears hover classes and hides the tooltip", () => {
    const { document, plotElements, tooltip, window } = makeHoverFixture();
    const pointA = document.querySelector("#point-a");

    dispatchMouseEvent(window, pointA, "mouseover", 100, 200);
    dispatchMouseEvent(window, pointA, "mouseout", 100, 200);

    for (const node of plotElements.nodes()) {
      expect(node.classList.contains("hovered")).toBe(false);
      expect(node.classList.contains("not-hovered")).toBe(false);
    }
    expect(tooltip.style("display")).toBe("none");
  });

  test("mouseover can update tooltip content while keeping it hidden", () => {
    const { document, tooltip, window } = makeHoverFixture("none");

    dispatchMouseEvent(
      window,
      document.querySelector("#point-b"),
      "mouseover",
      50,
      75,
    );

    expect(tooltip.style("display")).toBe("none");
    expect(tooltip.html()).toBe("Beta label");
    expect(tooltip.style("left")).toBe("60px");
    expect(tooltip.style("top")).toBe("70px");
  });
});
