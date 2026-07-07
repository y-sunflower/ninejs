/**
 * Get SVG-space anchor points for nearest-hover hit testing on a node.
 *
 * @param {object} parser - Plot parser instance.
 * @param {SVGElement} node - Plot element node.
 * @returns {Array<object>} Anchor points in SVG coordinates.
 */
export function getNodeAnchorPoints(parser, node) {
  if (node.classList?.contains("point")) {
    return getBBoxAnchorPoints(parser, node, false);
  }

  const path_points = getPathSamplePoints(parser, node);
  if (path_points.length > 0) {
    return path_points;
  }

  return getBBoxAnchorPoints(parser, node, true);
}

/**
 * Sample an SVG path into SVG-space points.
 *
 * @param {object} parser - Plot parser instance.
 * @param {SVGElement} node - Path-like SVG node.
 * @returns {Array<object>} Sampled points in SVG coordinates.
 */
export function getPathSamplePoints(parser, node) {
  if (
    typeof node.getTotalLength !== "function" ||
    typeof node.getPointAtLength !== "function"
  ) {
    return [];
  }

  let length;
  try {
    length = node.getTotalLength();
  } catch {
    return [];
  }

  if (!Number.isFinite(length) || length <= 0) {
    return [];
  }

  const sample_count = Math.max(
    1,
    Math.min(
      parser.nearest_max_samples,
      Math.ceil(length / parser.nearest_sample_spacing),
    ),
  );
  const points = [];

  for (let i = 0; i <= sample_count; i += 1) {
    try {
      const point = node.getPointAtLength((length * i) / sample_count);
      points.push(nodePointToSvg(parser, node, point.x, point.y));
    } catch {
      return points;
    }
  }

  return points;
}

/**
 * Get center and optional edge anchor points from a node bounding box.
 *
 * @param {object} parser - Plot parser instance.
 * @param {SVGElement} node - SVG node to inspect.
 * @param {boolean} include_corners - Whether to include corners and edge midpoints.
 * @returns {Array<object>} Anchor points in SVG coordinates.
 */
export function getBBoxAnchorPoints(parser, node, include_corners) {
  const bbox = getNodeBBox(parser, node);

  if (!bbox) {
    return [];
  }

  const center_x = bbox.x + bbox.width / 2;
  const center_y = bbox.y + bbox.height / 2;
  const local_points = [{ x: center_x, y: center_y }];

  if (include_corners) {
    local_points.push(
      { x: bbox.x, y: bbox.y },
      { x: bbox.x + bbox.width, y: bbox.y },
      { x: bbox.x, y: bbox.y + bbox.height },
      { x: bbox.x + bbox.width, y: bbox.y + bbox.height },
      { x: center_x, y: bbox.y },
      { x: center_x, y: bbox.y + bbox.height },
      { x: bbox.x, y: center_y },
      { x: bbox.x + bbox.width, y: center_y },
    );
  }

  return local_points.map((point) => {
    return nodePointToSvg(parser, node, point.x, point.y);
  });
}

/**
 * Get a finite bounding box for an SVG node.
 *
 * @param {object} parser - Plot parser instance.
 * @param {SVGElement} node - SVG node to inspect.
 * @returns {object|null} Bounding box or null when unavailable.
 */
export function getNodeBBox(parser, node) {
  if (typeof node.getBBox === "function") {
    try {
      const bbox = node.getBBox();
      if (isFiniteBBox(bbox)) {
        return bbox;
      }
    } catch {}
  }

  return getAttributeBBox(node);
}

/**
 * Build a bounding box from SVG position and size attributes.
 *
 * @param {SVGElement} node - SVG node to inspect.
 * @returns {object|null} Bounding box or null when attributes are incomplete.
 */
export function getAttributeBBox(node) {
  const x = numberAttribute(node, "x");
  const y = numberAttribute(node, "y");
  const width = numberAttribute(node, "width");
  const height = numberAttribute(node, "height");

  if (
    Number.isFinite(x) &&
    Number.isFinite(y) &&
    Number.isFinite(width) &&
    Number.isFinite(height)
  ) {
    return { x: x, y: y, width: width, height: height };
  }

  const cx = numberAttribute(node, "cx");
  const cy = numberAttribute(node, "cy");
  const r = numberAttribute(node, "r");

  if (Number.isFinite(cx) && Number.isFinite(cy) && Number.isFinite(r)) {
    return { x: cx - r, y: cy - r, width: r * 2, height: r * 2 };
  }

  return null;
}

/**
 * Read a numeric SVG attribute.
 *
 * @param {SVGElement} node - SVG node to inspect.
 * @param {string} name - Attribute name.
 * @returns {number} Numeric value, or NaN when missing or invalid.
 */
export function numberAttribute(node, name) {
  const attr = node.getAttribute(name);
  if (attr === null) {
    return NaN;
  }

  const value = Number(attr);
  return Number.isFinite(value) ? value : NaN;
}

/**
 * Get the interactive panel bounds for an axes group.
 *
 * @param {object} parser - Plot parser instance.
 * @param {string} axes_class - Matplotlib axes group id.
 * @returns {object|null} Panel bounds or null when unavailable.
 */
export function getPanelBounds(parser, axes_class) {
  const clip_bounds = getAxesClipBounds(parser, axes_class);

  if (clip_bounds) {
    return clip_bounds;
  }

  const axes_node = parser.svg.select(`g#${axes_class}`).node();
  if (!axes_node) {
    return null;
  }

  return getNodeBBox(parser, axes_node);
}

/**
 * Get bounds from the clip path attached to an axes group.
 *
 * @param {object} parser - Plot parser instance.
 * @param {string} axes_class - Matplotlib axes group id.
 * @returns {object|null} Clip bounds or null when unavailable.
 */
export function getAxesClipBounds(parser, axes_class) {
  const axes_node = parser.svg.select(`g#${axes_class}`).node();
  const clipped_node = axes_node?.querySelector("[clip-path]");
  const clip_path = clipped_node?.getAttribute("clip-path");
  const clip_id = getClipPathId(clip_path);

  if (!clip_id) {
    return null;
  }

  const clip_node = parser.svg.node().ownerDocument.getElementById(clip_id);
  const rect = clip_node?.querySelector("rect");

  if (!rect) {
    return null;
  }

  return getAttributeBBox(rect);
}

/**
 * Extract the id referenced by an SVG clip-path value.
 *
 * @param {string|null} clip_path - SVG clip-path attribute value.
 * @returns {string|null} Clip path id or null when absent.
 */
export function getClipPathId(clip_path) {
  if (!clip_path) {
    return null;
  }

  const match = /url\(["']?#([^)"']+)["']?\)/.exec(clip_path);
  return match ? match[1] : null;
}

/**
 * Convert a pointer event position to SVG coordinates.
 *
 * @param {object} parser - Plot parser instance.
 * @param {Event} event - Pointer or mouse event.
 * @returns {object|null} SVG point or null when coordinates are invalid.
 */
export function eventToSvgPoint(parser, event) {
  const client_x = event.clientX ?? event.pageX;
  const client_y = event.clientY ?? event.pageY;

  if (!Number.isFinite(client_x) || !Number.isFinite(client_y)) {
    return null;
  }

  return clientPointToSvg(parser, client_x, client_y);
}

/**
 * Convert viewport client coordinates to SVG coordinates.
 *
 * @param {object} parser - Plot parser instance.
 * @param {number} client_x - Client x coordinate.
 * @param {number} client_y - Client y coordinate.
 * @returns {object} SVG point.
 */
export function clientPointToSvg(parser, client_x, client_y) {
  const svg_node = parser.svg.node();

  if (
    svg_node &&
    typeof svg_node.createSVGPoint === "function" &&
    typeof svg_node.getScreenCTM === "function"
  ) {
    try {
      const ctm = svg_node.getScreenCTM();

      if (ctm) {
        const point = svg_node.createSVGPoint();
        point.x = client_x;
        point.y = client_y;
        return point.matrixTransform(ctm.inverse());
      }
    } catch {}
  }

  return clientPointToSvgFromViewBox(parser, client_x, client_y);
}

/**
 * Convert client coordinates to SVG coordinates using the SVG viewBox.
 *
 * @param {object} parser - Plot parser instance.
 * @param {number} client_x - Client x coordinate.
 * @param {number} client_y - Client y coordinate.
 * @returns {object} SVG point.
 */
export function clientPointToSvgFromViewBox(parser, client_x, client_y) {
  const svg_node = parser.svg.node();

  if (!svg_node || typeof svg_node.getBoundingClientRect !== "function") {
    return { x: client_x, y: client_y };
  }

  const rect = svg_node.getBoundingClientRect();
  const view_box = getSvgViewBox(svg_node, rect);

  if (
    !view_box ||
    !Number.isFinite(rect.width) ||
    !Number.isFinite(rect.height) ||
    rect.width === 0 ||
    rect.height === 0
  ) {
    return { x: client_x, y: client_y };
  }

  return {
    x: view_box.x + ((client_x - rect.left) * view_box.width) / rect.width,
    y: view_box.y + ((client_y - rect.top) * view_box.height) / rect.height,
  };
}

/**
 * Resolve an SVG viewBox from baseVal, attributes, or rendered bounds.
 *
 * @param {SVGSVGElement} svg_node - SVG root node.
 * @param {DOMRect} rect - Rendered SVG bounds.
 * @returns {object|null} ViewBox-like bounds or null when unavailable.
 */
export function getSvgViewBox(svg_node, rect) {
  const view_box = svg_node.viewBox?.baseVal;

  if (view_box && view_box.width > 0 && view_box.height > 0) {
    return view_box;
  }

  const attr = svg_node.getAttribute("viewBox");
  if (attr) {
    const values = attr
      .trim()
      .split(/[\s,]+/)
      .map((value) => Number(value));
    if (
      values.length === 4 &&
      values.every((value) => Number.isFinite(value)) &&
      values[2] > 0 &&
      values[3] > 0
    ) {
      return {
        x: values[0],
        y: values[1],
        width: values[2],
        height: values[3],
      };
    }
  }

  if (rect.width > 0 && rect.height > 0) {
    return { x: 0, y: 0, width: rect.width, height: rect.height };
  }

  return null;
}

/**
 * Convert a node-local point to SVG root coordinates.
 *
 * @param {object} parser - Plot parser instance.
 * @param {SVGElement} node - SVG node containing the point.
 * @param {number} x - Node-local x coordinate.
 * @param {number} y - Node-local y coordinate.
 * @returns {object} SVG point.
 */
export function nodePointToSvg(parser, node, x, y) {
  const svg_node = parser.svg.node();

  if (
    svg_node &&
    typeof svg_node.createSVGPoint === "function" &&
    typeof svg_node.getScreenCTM === "function" &&
    typeof node.getScreenCTM === "function"
  ) {
    try {
      const node_ctm = node.getScreenCTM();
      const svg_ctm = svg_node.getScreenCTM();

      if (node_ctm && svg_ctm) {
        const point = svg_node.createSVGPoint();
        point.x = x;
        point.y = y;
        return point
          .matrixTransform(node_ctm)
          .matrixTransform(svg_ctm.inverse());
      }
    } catch {}
  }

  if (
    svg_node &&
    typeof svg_node.createSVGPoint === "function" &&
    typeof svg_node.getCTM === "function" &&
    typeof node.getCTM === "function"
  ) {
    try {
      const node_ctm = node.getCTM();
      const svg_ctm = svg_node.getCTM();

      if (node_ctm && svg_ctm) {
        const point = svg_node.createSVGPoint();
        point.x = x;
        point.y = y;
        return point
          .matrixTransform(node_ctm)
          .matrixTransform(svg_ctm.inverse());
      }
    } catch {}
  }

  return { x: x, y: y };
}

/**
 * Check whether a point has finite x and y coordinates.
 *
 * @param {object|null} point - Point to inspect.
 * @returns {boolean} Whether the point is finite.
 */
export function isFinitePoint(point) {
  return point && Number.isFinite(point.x) && Number.isFinite(point.y);
}

/**
 * Check whether a bounding box has finite position and size values.
 *
 * @param {object|null} bbox - Bounding box to inspect.
 * @returns {boolean} Whether the bounding box is finite.
 */
export function isFiniteBBox(bbox) {
  return (
    bbox &&
    Number.isFinite(bbox.x) &&
    Number.isFinite(bbox.y) &&
    Number.isFinite(bbox.width) &&
    Number.isFinite(bbox.height)
  );
}

/**
 * Check whether a point lies within rectangular bounds.
 *
 * @param {object} point - Point to inspect.
 * @param {object} bounds - Rectangular bounds.
 * @returns {boolean} Whether the point is inside the bounds.
 */
export function pointInBounds(point, bounds) {
  return (
    point.x >= bounds.x &&
    point.x <= bounds.x + bounds.width &&
    point.y >= bounds.y &&
    point.y <= bounds.y + bounds.height
  );
}
