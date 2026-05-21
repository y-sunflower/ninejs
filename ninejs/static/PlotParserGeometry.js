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
      parser.max_path_samples,
      Math.ceil(length / parser.path_sample_spacing),
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

export function numberAttribute(node, name) {
  const attr = node.getAttribute(name);
  if (attr === null) {
    return NaN;
  }

  const value = Number(attr);
  return Number.isFinite(value) ? value : NaN;
}

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

export function getClipPathId(clip_path) {
  if (!clip_path) {
    return null;
  }

  const match = /url\(["']?#([^)"']+)["']?\)/.exec(clip_path);
  return match ? match[1] : null;
}

export function eventToSvgPoint(parser, event) {
  const client_x = event.clientX ?? event.pageX;
  const client_y = event.clientY ?? event.pageY;

  if (!Number.isFinite(client_x) || !Number.isFinite(client_y)) {
    return null;
  }

  return clientPointToSvg(parser, client_x, client_y);
}

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

export function isFinitePoint(point) {
  return point && Number.isFinite(point.x) && Number.isFinite(point.y);
}

export function isFiniteBBox(bbox) {
  return (
    bbox &&
    Number.isFinite(bbox.x) &&
    Number.isFinite(bbox.y) &&
    Number.isFinite(bbox.width) &&
    Number.isFinite(bbox.height)
  );
}

export function pointInBounds(point, bounds) {
  return (
    point.x >= bounds.x &&
    point.x <= bounds.x + bounds.width &&
    point.y >= bounds.y &&
    point.y <= bounds.y + bounds.height
  );
}
