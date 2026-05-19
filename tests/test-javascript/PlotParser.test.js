import { describe, expect, test } from "bun:test";
import { JSDOM } from "jsdom";
import { select } from "d3-selection";

import PlotSVGParser from "../../ninejs/static/PlotParser.js";

function makeParser(svgMarkup) {
  const dom = new JSDOM(svgMarkup);
  const document = dom.window.document;
  const svg = select(document).select("svg");
  const tooltip = select(document.createElement("div"));
  const parser = new PlotSVGParser(svg, tooltip, 0, 0);

  return { document, parser, svg };
}

function selectedIds(selection) {
  return selection.nodes().map((node) => node.id);
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
    expect(selectedIds(points)).toEqual(["point-a", "point-b", "point-c"]);
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
    expect(selectedIds(lines)).toEqual(["line-a", "function-line"]);
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
    expect(selectedIds(bars)).toEqual(["bar-a", "bar-b", "bar-c"]);
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
    expect(selectedIds(areas)).toEqual(["area-a", "area-b"]);
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
