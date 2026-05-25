import { describe, expect, test } from "bun:test";
import { JSDOM } from "jsdom";
import { select } from "d3-selection";
import createDOMPurify from "dompurify";

import PlotSVGParser from "../../ninejs/static/PlotParser.js";

function makeParser(svgMarkup) {
  const dom = new JSDOM(svgMarkup);
  const window = dom.window;
  window.requestAnimationFrame = (callback) => callback();
  const document = window.document;
  const svg = select(document).select("svg");
  const tooltipNode = document.createElement("div");
  document.body.appendChild(tooltipNode);
  const tooltip = select(tooltipNode);
  const sanitizer = createDOMPurify(window);
  const parser = new PlotSVGParser(svg, tooltip, sanitizer);

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
      view: window,
    }),
  );
}

function setClickHandlers(handlers) {
  globalThis.ninejs = {
    ...(globalThis.ninejs || {}),
    clickHandlers: handlers,
  };
}

function makeHoverFixture(showTooltip = "block", reverseHover = false) {
  const { document, parser, svg, tooltip, window } = makeParser(
    `
      <svg>
        <path id="point-a" class="plot-element"></path>
        <path id="point-b" class="plot-element"></path>
        <path id="point-c" class="plot-element"></path>
      </svg>
    `,
  );
  const plotElements = svg.selectAll("path.plot-element");
  const labels = ["Alpha label", "Beta label", "Second alpha label"];
  const groups = ["alpha", "beta", "alpha"];

  parser.setHoverEffect(
    plotElements,
    labels,
    groups,
    showTooltip,
    reverseHover,
  );

  return { document, plotElements, tooltip, window };
}

function makeNearestHoverFixture(
  labels = ["Alpha label", "Beta label", "Second alpha label"],
  reverseHover = false,
) {
  const { document, parser, svg, tooltip, window } = makeParser(
    `
      <svg>
        <defs>
          <clipPath id="panel-clip">
            <rect x="0" y="0" width="200" height="200"></rect>
          </clipPath>
        </defs>
        <g id="axes_1">
          <circle
            id="point-a"
            class="point plot-element"
            cx="20"
            cy="20"
            r="5"
            clip-path="url(#panel-clip)"
          ></circle>
          <circle
            id="point-b"
            class="point plot-element"
            cx="150"
            cy="20"
            r="5"
            clip-path="url(#panel-clip)"
          ></circle>
          <circle
            id="point-c"
            class="point plot-element"
            cx="35"
            cy="35"
            r="5"
            clip-path="url(#panel-clip)"
          ></circle>
        </g>
      </svg>
    `,
  );
  const plotElements = svg.selectAll("circle.plot-element");
  const groups = ["alpha", "beta", "alpha"];

  parser.setNearestHoverEffect(svg, "axes_1", [
    {
      plotElements: plotElements,
      tooltipLabels: labels,
      tooltipGroups: groups,
      showTooltip: labels.length === 0 ? "none" : "block",
      reverseHover: reverseHover,
    },
  ]);

  return { document, plotElements, svg, tooltip, window };
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

  test("findBars assigns data groups when provided", () => {
    const { parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="PolyCollection_1">
            <path id="bar-a"></path>
            <path id="bar-b"></path>
          </g>
        </g>
      </svg>
    `);

    const bars = parser.findBars(svg, "axes_1", ["group-a", "group-b"]);

    expect(bars.nodes().map((node) => node.getAttribute("data-group"))).toEqual(
      ["group-a", "group-b"],
    );
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

  test("findPolygons discovers map paths in the requested axes", () => {
    const { document, parser, svg } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="PatchCollection_1">
            <path id="polygon-a"></path>
            <path id="polygon-b"></path>
          </g>
          <g id="NotPatchCollection_1">
            <path id="not-a-polygon"></path>
          </g>
        </g>
        <g id="axes_2">
          <g id="PatchCollection_2">
            <path id="other-axes-polygon"></path>
          </g>
        </g>
      </svg>
    `);

    const polygons = parser.findPolygons(svg, "axes_1");

    expect(polygons.size()).toBe(2);
    expect(polygons.nodes().map((node) => node.id)).toEqual([
      "polygon-a",
      "polygon-b",
    ]);
    expect(polygons.nodes().map((node) => node.getAttribute("class"))).toEqual([
      "polygon plot-element",
      "polygon plot-element",
    ]);
    expect(
      document.querySelector("#not-a-polygon").getAttribute("class"),
    ).toBeNull();
    expect(
      document.querySelector("#other-axes-polygon").getAttribute("class"),
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
    expect(tooltip.style("left")).toBe("100px");
    expect(tooltip.style("top")).toBe("200px");
  });

  test("mouseover can reverse hover by dimming the matching group", () => {
    const { document, tooltip, window } = makeHoverFixture("block", true);

    dispatchMouseEvent(
      window,
      document.querySelector("#point-a"),
      "mouseover",
      100,
      200,
    );

    expect(hasClass(document, "point-a", "not-hovered")).toBe(true);
    expect(hasClass(document, "point-a", "hovered")).toBe(false);
    expect(hasClass(document, "point-c", "not-hovered")).toBe(true);
    expect(hasClass(document, "point-c", "hovered")).toBe(false);
    expect(hasClass(document, "point-b", "not-hovered")).toBe(false);
    expect(hasClass(document, "point-b", "hovered")).toBe(false);
    expect(tooltip.style("display")).toBe("block");
    expect(tooltip.html()).toBe("Alpha label");
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
    expect(tooltip.style("left")).toBe("50px");
    expect(tooltip.style("top")).toBe("75px");
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

  test("mouseover repeats exact duplicated collection labels and groups", () => {
    const { document, parser, svg, tooltip, window } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="PatchCollection_1">
            <path id="polygon-a-copy-1"></path>
            <path id="polygon-b-copy-1"></path>
          </g>
          <g id="PatchCollection_2">
            <path id="polygon-a-copy-2"></path>
            <path id="polygon-b-copy-2"></path>
          </g>
        </g>
      </svg>
    `);
    const polygons = parser.findPolygons(svg, "axes_1");

    parser.setHoverEffect(polygons, ["Alpha", "Beta"], ["a", "b"], "block");
    dispatchMouseEvent(
      window,
      document.querySelector("#polygon-b-copy-2"),
      "mouseover",
      100,
      200,
    );

    expect(tooltip.html()).toBe("Beta");
    expect(hasClass(document, "polygon-b-copy-1", "hovered")).toBe(true);
    expect(hasClass(document, "polygon-b-copy-2", "hovered")).toBe(true);
    expect(hasClass(document, "polygon-a-copy-1", "not-hovered")).toBe(true);
    expect(hasClass(document, "polygon-a-copy-2", "not-hovered")).toBe(true);
  });

  test("click runs the matching registered handler with event and element context", () => {
    const { document, parser, svg, window } = makeParser(`
      <svg>
        <path id="point-a" class="plot-element"></path>
        <path id="point-b" class="plot-element"></path>
      </svg>
    `);
    const plotElements = svg.selectAll("path.plot-element");

    setClickHandlers({
      setEventType(event) {
        this.setAttribute("data-clicked", event.type);
      },
      setElementId() {
        this.setAttribute("data-clicked", this.id);
      },
    });
    parser.setHoverEffect(plotElements, [], [], "none", false, [
      "setEventType",
      "setElementId",
    ]);
    dispatchMouseEvent(
      window,
      document.querySelector("#point-b"),
      "click",
      100,
      200,
    );

    expect(
      document.querySelector("#point-a").getAttribute("data-clicked"),
    ).toBe(null);
    expect(
      document.querySelector("#point-b").getAttribute("data-clicked"),
    ).toBe("point-b");
    expect(hasClass(document, "point-a", "clickable")).toBe(true);
    expect(hasClass(document, "point-b", "clickable")).toBe(true);
  });

  test("click ignores empty and missing handlers", () => {
    const { document, parser, svg, window } = makeParser(`
      <svg>
        <path id="point-a" class="plot-element"></path>
        <path id="point-b" class="plot-element"></path>
        <path id="point-c" class="plot-element"></path>
      </svg>
    `);
    const plotElements = svg.selectAll("path.plot-element");

    parser.setClickEffect(plotElements, ["", null, NaN]);
    for (const node of plotElements.nodes()) {
      dispatchMouseEvent(window, node, "click", 100, 200);
    }

    for (const node of plotElements.nodes()) {
      expect(node.getAttribute("data-clicked")).toBeNull();
      expect(node.classList.contains("clickable")).toBe(false);
    }
  });

  test("click does not evaluate unregistered string handlers", () => {
    const { document, parser, svg, window } = makeParser(`
      <svg>
        <path id="point-a" class="plot-element"></path>
      </svg>
    `);
    const plotElements = svg.selectAll("path.plot-element");

    setClickHandlers({});
    parser.setClickEffect(plotElements, [
      "this.setAttribute('data-clicked', 'raw code')",
    ]);
    dispatchMouseEvent(
      window,
      document.querySelector("#point-a"),
      "click",
      100,
      200,
    );

    expect(
      document.querySelector("#point-a").getAttribute("data-clicked"),
    ).toBe(null);
    expect(hasClass(document, "point-a", "clickable")).toBe(true);
  });

  test("click repeats exact duplicated collection handlers", () => {
    const { document, parser, svg, window } = makeParser(`
      <svg>
        <g id="axes_1">
          <g id="PatchCollection_1">
            <path id="polygon-a-copy-1"></path>
            <path id="polygon-b-copy-1"></path>
          </g>
          <g id="PatchCollection_2">
            <path id="polygon-a-copy-2"></path>
            <path id="polygon-b-copy-2"></path>
          </g>
        </g>
      </svg>
    `);
    const polygons = parser.findPolygons(svg, "axes_1");

    setClickHandlers({
      setAlpha() {
        this.setAttribute("data-clicked", "Alpha");
      },
      setBeta() {
        this.setAttribute("data-clicked", "Beta");
      },
    });
    parser.setClickEffect(polygons, ["setAlpha", "setBeta"]);
    dispatchMouseEvent(
      window,
      document.querySelector("#polygon-b-copy-2"),
      "click",
      100,
      200,
    );

    expect(
      document.querySelector("#polygon-b-copy-2").getAttribute("data-clicked"),
    ).toBe("Beta");
  });

  test("mousemove highlights the nearest element and updates tooltip state", () => {
    const { document, svg, tooltip, window } = makeNearestHoverFixture();

    dispatchMouseEvent(window, svg.node(), "mousemove", 30, 30);

    expect(hasClass(document, "point-a", "hovered")).toBe(true);
    expect(hasClass(document, "point-c", "hovered")).toBe(true);
    expect(hasClass(document, "point-b", "not-hovered")).toBe(true);
    expect(tooltip.style("display")).toBe("block");
    expect(tooltip.html()).toBe("Second alpha label");
    expect(tooltip.style("left")).toBe("30px");
    expect(tooltip.style("top")).toBe("30px");
  });

  test("mousemove can reverse nearest hover by dimming the matching group", () => {
    const { document, svg, tooltip, window } = makeNearestHoverFixture(
      ["Alpha label", "Beta label", "Second alpha label"],
      true,
    );

    dispatchMouseEvent(window, svg.node(), "mousemove", 30, 30);

    expect(hasClass(document, "point-a", "not-hovered")).toBe(true);
    expect(hasClass(document, "point-a", "hovered")).toBe(false);
    expect(hasClass(document, "point-c", "not-hovered")).toBe(true);
    expect(hasClass(document, "point-c", "hovered")).toBe(false);
    expect(hasClass(document, "point-b", "not-hovered")).toBe(false);
    expect(hasClass(document, "point-b", "hovered")).toBe(false);
    expect(tooltip.style("display")).toBe("block");
    expect(tooltip.html()).toBe("Second alpha label");
  });

  test("mousemove hides nearest tooltip outside the panel bounds", () => {
    const { document, svg, tooltip, window } = makeNearestHoverFixture();

    dispatchMouseEvent(window, svg.node(), "mousemove", 30, 30);
    dispatchMouseEvent(window, svg.node(), "mousemove", 250, 250);

    expect(hasClass(document, "point-a", "hovered")).toBe(false);
    expect(hasClass(document, "point-c", "hovered")).toBe(false);
    expect(tooltip.style("display")).toBe("none");
  });

  test("mousemove can update nearest hover while keeping tooltip hidden", () => {
    const { document, svg, tooltip, window } = makeNearestHoverFixture([]);

    dispatchMouseEvent(window, svg.node(), "mousemove", 140, 20);

    expect(hasClass(document, "point-b", "hovered")).toBe(true);
    expect(tooltip.style("display")).toBe("none");
  });

  test("mouseleave prevents a queued nearest hover update from reopening the tooltip", () => {
    const { document, parser, svg, tooltip, window } = makeParser(`
      <svg>
        <defs>
          <clipPath id="panel-clip">
            <rect x="0" y="0" width="200" height="200"></rect>
          </clipPath>
        </defs>
        <g id="axes_1">
          <circle
            id="point-a"
            class="point plot-element"
            cx="20"
            cy="20"
            r="5"
            clip-path="url(#panel-clip)"
          ></circle>
        </g>
      </svg>
    `);
    let queuedFrame = null;
    window.requestAnimationFrame = (callback) => {
      queuedFrame = callback;
      return 1;
    };
    window.cancelAnimationFrame = () => {
      queuedFrame = null;
    };
    const plotElements = svg.selectAll("circle.plot-element");

    parser.setNearestHoverEffect(svg, "axes_1", [
      {
        plotElements: plotElements,
        tooltipLabels: ["Alpha label"],
        tooltipGroups: ["alpha"],
        showTooltip: "block",
      },
    ]);

    dispatchMouseEvent(window, svg.node(), "mousemove", 20, 20);
    const staleFrame = queuedFrame;
    dispatchMouseEvent(window, svg.node(), "mouseleave", 0, 0);
    staleFrame();

    expect(hasClass(document, "point-a", "hovered")).toBe(false);
    expect(tooltip.style("display")).toBe("none");
  });
});
