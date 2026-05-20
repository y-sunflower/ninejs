import { describe, expect, test } from "bun:test";
import { JSDOM } from "jsdom";
import { select } from "d3-selection";
import createDOMPurify from "dompurify";

import PlotSVGParser from "../../ninejs/static/PlotParser.js";

function makeParser(svgMarkup, tooltipXShift = 0, tooltipYShift = 0) {
  const dom = new JSDOM(svgMarkup);
  const window = dom.window;
  const document = window.document;
  const svg = select(document).select("svg");
  const tooltipNode = document.createElement("div");
  document.body.appendChild(tooltipNode);
  const tooltip = select(tooltipNode);
  const sanitizer = createDOMPurify(window);
  const parser = new PlotSVGParser(
    svg,
    tooltip,
    tooltipXShift,
    tooltipYShift,
    sanitizer,
  );

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

  test("findPoints discovers rendered point uses before marker definitions", () => {
    const { document, parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="PathCollection_1">
            <defs>
              <path id="marker-shape"></path>
            </defs>
            <g>
              <use id="point-a" href="#marker-shape"></use>
              <use id="point-b" href="#marker-shape"></use>
            </g>
          </g>
        </g>
      </svg>
    `);

    const points = parser.findPoints(svg, "axes_1", ["group-a", "group-b"]);

    expect(points.size()).toBe(2);
    expect(points.nodes().map((node) => node.id)).toEqual([
      "point-a",
      "point-b",
    ]);
    expect(points.nodes().map((node) => node.getAttribute("class"))).toEqual([
      "point plot-element",
      "point plot-element",
    ]);
    expect(
      points.nodes().map((node) => node.getAttribute("data-group")),
    ).toEqual(["group-a", "group-b"]);
    expect(
      document.querySelector("#marker-shape").getAttribute("class"),
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

  test("mouseover sanitizes tooltip HTML before rendering", () => {
    const { document, parser, svg, tooltip, window } = makeParser(`
      <svg>
        <path id="point-a" class="plot-element"></path>
      </svg>
    `);
    const plotElements = svg.selectAll("path.plot-element");
    const label =
      '<b>hello</b> <span onclick="alert(1)">world</span><script>alert(2)</script>';

    parser.setHoverEffect(plotElements, [label], ["alpha"], "block");
    dispatchMouseEvent(
      window,
      document.querySelector("#point-a"),
      "mouseover",
      100,
      200,
    );

    expect(tooltip.node().querySelector("b").textContent).toBe("hello");
    expect(tooltip.node().querySelector("span").textContent).toBe("world");
    expect(
      tooltip.node().querySelector("span").getAttribute("onclick"),
    ).toBeNull();
    expect(tooltip.node().querySelector("script")).toBeNull();
  });
});
