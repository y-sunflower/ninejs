import * as d3 from "d3";

// Visual (magnifying-glass) zoom and pan for the whole rendered chart.
//
// This applies a d3 zoom/pan transform to the matplotlib figure group, so
// everything — data, axes, ticks, and labels — scales together. It does not
// rescale the data against fixed axes; it simply magnifies the picture. The
// outer <svg> clips content panned beyond its bounds.
//
// Hover/click hit-testing keeps working without changes because the parser
// maps pointer and node coordinates through getScreenCTM(), which already
// accounts for the applied transform.
export function setZoomEffect(svg, options = {}) {
  const svg_node = svg.node();
  if (!svg_node || typeof d3.zoom !== "function") {
    return null;
  }

  // The figure group holds all rendered content. matplotlib leaves it
  // without its own transform, so it is safe to drive directly from zoom.
  let zoom_target = svg.select('g[id^="figure_"]');
  if (zoom_target.empty()) {
    zoom_target = svg.select("g");
  }
  if (zoom_target.empty()) {
    return null;
  }

  const min_scale = options.minScale ?? 1;
  const max_scale = options.maxScale ?? 8;

  const zoom = d3
    .zoom()
    .scaleExtent([min_scale, max_scale])
    .on("zoom", (event) => {
      zoom_target.attr("transform", event.transform);
      svg.classed("zoomed", event.transform.k !== 1);
    });

  svg.call(zoom);
  svg.classed("zoomable", true);

  // Double-click resets to the original view instead of zooming further in.
  svg.on("dblclick.zoom", null);
  svg.on("dblclick.zoom-reset", () => {
    svg.transition().duration(200).call(zoom.transform, d3.zoomIdentity);
  });

  return zoom;
}
