import * as d3 from "d3";
import {
  applyHoverRecord,
  clearHoverEffects,
  normalizeHoverConfig,
  positionTooltip,
} from "./PlotParserHover.js";
import {
  eventToSvgPoint,
  getNodeAnchorPoints,
  getPanelBounds,
  isFinitePoint,
  pointInBounds,
} from "./PlotParserGeometry.js";

/**
 * Attach nearest-point hover behavior for one axes group.
 *
 * @param {object} parser - Plot parser instance.
 * @param {d3.Selection} svg - SVG root selection.
 * @param {string} axes_class - Matplotlib axes group id.
 * @param {Array<object>} hover_configs - Hover configurations for this axes.
 * @param {Array<object>|null} hover_scope_configs - Optional linked-hover scope.
 */
export function setNearestHoverEffect(
  parser,
  svg,
  axes_class,
  hover_configs,
  hover_scope_configs = null,
) {
  const axes_node = svg.select(`g#${axes_class}`).node();

  if (!axes_node) {
    return;
  }

  for (const hc of hover_configs) {
    normalizeHoverConfig(hc, hc.plotElements.nodes().length);
  }
  const normalized_hover_configs = hover_configs;
  if (hover_scope_configs !== null && hover_scope_configs.length > 0) {
    for (const hc of hover_scope_configs) {
      normalizeHoverConfig(hc, hc.plotElements.nodes().length);
    }
  }
  const normalized_hover_scope_configs =
    hover_scope_configs === null || hover_scope_configs.length === 0
      ? normalized_hover_configs
      : hover_scope_configs;
  const panel_bounds = getPanelBounds(parser, axes_class);
  const records = getHoverRecords(normalized_hover_configs);
  const anchors = getNearestAnchors(parser, records, panel_bounds);

  if (anchors.length === 0) {
    return;
  }

  const nearest_index = d3
    .quadtree()
    .x((d) => d.x)
    .y((d) => d.y)
    .addAll(anchors);
  const record_by_node = new Map(
    records.map((record) => {
      return [record.node, record];
    }),
  );
  if (panel_bounds) {
    ensureNearestHoverPanel(axes_node, panel_bounds);
  }
  const state = {
    axesNode: axes_node,
    activeRecord: null,
    activeHoverConfigs: null,
    hoverConfigs: normalized_hover_configs,
    hoverScopeConfigs: normalized_hover_scope_configs,
    nearestIndex: nearest_index,
    panelBounds: panel_bounds,
    recordByNode: record_by_node,
  };
  let animation_frame = null;
  let last_event = null;
  let pointer_inside = false;

  svg
    .on(`mousemove.nearest-${axes_class}`, function (event) {
      pointer_inside = true;
      last_event = event;

      if (animation_frame !== null) {
        return;
      }

      const request_frame = event.view?.requestAnimationFrame
        ? event.view.requestAnimationFrame.bind(event.view)
        : (callback) => callback();
      animation_frame = true;
      const frame_id = request_frame(() => {
        const pending_event = last_event;
        animation_frame = null;

        if (!pointer_inside || pending_event === null) {
          return;
        }

        updateNearestHover(parser, pending_event, state);
      });
      if (animation_frame !== null && frame_id !== undefined) {
        animation_frame = frame_id;
      }
    })
    .on(`mouseleave.nearest-${axes_class}`, function (event) {
      pointer_inside = false;
      last_event = null;

      if (animation_frame !== null && event.view?.cancelAnimationFrame) {
        event.view.cancelAnimationFrame(animation_frame);
      }

      animation_frame = null;
      state.activeRecord = null;
      clearHoverEffects(state.activeHoverConfigs || normalized_hover_configs);
      state.activeHoverConfigs = null;
      parser.tooltip.style("display", "none");
    });
}

/**
 * Update the active nearest-hover record for a pointer event.
 *
 * @param {object} parser - Plot parser instance.
 * @param {Event} event - Pointer or mouse event.
 * @param {object} state - Nearest-hover state.
 */
export function updateNearestHover(parser, event, state) {
  const svg_point = eventToSvgPoint(parser, event);

  if (
    !svg_point ||
    (state.panelBounds && !pointInBounds(svg_point, state.panelBounds))
  ) {
    clearActiveNearestHover(parser, state);
    return;
  }

  const direct_record = getDirectHoverRecord(event, state);
  const nearest_anchor =
    direct_record == null
      ? state.nearestIndex.find(svg_point.x, svg_point.y)
      : null;
  const record = direct_record || nearest_anchor?.record;

  if (!record) {
    clearActiveNearestHover(parser, state);
    return;
  }

  if (record !== state.activeRecord) {
    const hover_configs = getHoverScope(record, state);
    applyHoverRecord(parser, record, event, hover_configs);
    state.activeRecord = record;
    state.activeHoverConfigs = hover_configs;
    return;
  }

  positionTooltip(parser, event, record.hoverConfig.showTooltip);
}

/**
 * Choose the hover scope for a nearest-hover record.
 *
 * @param {object} record - Hover record.
 * @param {object} state - Nearest-hover state.
 * @returns {Array<object>} Hover configurations in scope.
 */
function getHoverScope(record, state) {
  const hover_keys = record.hoverConfig.hoverKeys || [];

  if (hover_keys.length > 0) {
    return state.hoverScopeConfigs;
  }

  return state.hoverConfigs;
}

/**
 * Ensure an invisible panel exists to receive nearest-hover pointer events.
 *
 * @param {SVGGElement} axes_node - Axes group node.
 * @param {object} panel_bounds - Panel bounds.
 */
export function ensureNearestHoverPanel(axes_node, panel_bounds) {
  let panel = axes_node.querySelector("rect.nearest-hover-panel");

  if (!panel) {
    panel = axes_node.ownerDocument.createElementNS(
      "http://www.w3.org/2000/svg",
      "rect",
    );
    panel.setAttribute("class", "nearest-hover-panel");
    axes_node.insertBefore(panel, axes_node.firstChild);
  }

  panel.setAttribute("x", panel_bounds.x);
  panel.setAttribute("y", panel_bounds.y);
  panel.setAttribute("width", panel_bounds.width);
  panel.setAttribute("height", panel_bounds.height);
  panel.setAttribute("fill", "transparent");
  panel.setAttribute("pointer-events", "all");
}

/**
 * Clear the active nearest-hover record and tooltip.
 *
 * @param {object} parser - Plot parser instance.
 * @param {object} state - Nearest-hover state.
 */
export function clearActiveNearestHover(parser, state) {
  if (state.activeRecord === null) {
    return;
  }

  state.activeRecord = null;
  clearHoverEffects(state.activeHoverConfigs || state.hoverConfigs);
  state.activeHoverConfigs = null;
  parser.tooltip.style("display", "none");
}

/**
 * Build hover records from normalized hover configurations.
 *
 * @param {Array<object>} hover_configs - Hover configurations to index.
 * @returns {Array<object>} Hover records aligned to plot nodes.
 */
export function getHoverRecords(hover_configs) {
  const records = [];

  for (const hover_config of hover_configs) {
    const tooltip_labels = hover_config.tooltipLabels || [];
    const tooltip_groups = hover_config.tooltipGroups || [];
    const hover_keys = hover_config.hoverKeys || [];
    if (
      tooltip_labels.length === 0 &&
      tooltip_groups.length === 0 &&
      hover_keys.length === 0
    ) {
      continue;
    }

    const nodes = hover_config.plotElements.nodes();
    const normalized_hover_config = normalizeHoverConfig(
      hover_config,
      nodes.length,
    );
    for (let i = 0; i < nodes.length; i += 1) {
      records.push({
        hoverConfig: normalized_hover_config,
        index: i,
        node: nodes[i],
      });
    }
  }

  return records;
}

/**
 * Build nearest-hover anchor points for hover records.
 *
 * @param {object} parser - Plot parser instance.
 * @param {Array<object>} records - Hover records to sample.
 * @param {object|null} bounds - Optional bounds filter.
 * @returns {Array<object>} Anchor points with attached hover records.
 */
export function getNearestAnchors(parser, records, bounds = null) {
  const anchors = [];

  for (const record of records) {
    const points = getNodeAnchorPoints(parser, record.node);

    for (const point of points) {
      if (
        isFinitePoint(point) &&
        (bounds === null || pointInBounds(point, bounds))
      ) {
        anchors.push({ x: point.x, y: point.y, record: record });
      }
    }
  }

  return anchors;
}

/**
 * Resolve a directly targeted plot element to its hover record.
 *
 * @param {Event} event - Pointer or mouse event.
 * @param {object} state - Nearest-hover state.
 * @returns {object|null} Hover record or null.
 */
export function getDirectHoverRecord(event, state) {
  const plot_element = closestPlotElement(event.target, state.axesNode);

  if (!plot_element) {
    return null;
  }

  return state.recordByNode.get(plot_element) || null;
}

/**
 * Find the nearest ancestor plot element within an axes group.
 *
 * @param {Node} node - Starting DOM node.
 * @param {SVGGElement} axes_node - Axes group node.
 * @returns {Element|null} Matching plot element or null.
 */
export function closestPlotElement(node, axes_node) {
  let current = node;

  while (current && current !== axes_node.parentNode) {
    if (
      current.classList?.contains("plot-element") &&
      axes_node.contains(current)
    ) {
      return current;
    }

    current = current.parentNode;
  }

  return null;
}
