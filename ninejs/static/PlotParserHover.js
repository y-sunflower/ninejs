/**
 * Set sanitized tooltip content.
 *
 * @param {object} parser - Plot parser instance.
 * @param {*} label - Tooltip label value.
 */
export function setTooltipContent(parser, label) {
  const value = label == null ? "" : String(label);

  if (!parser.sanitizer || typeof parser.sanitizer.sanitize !== "function") {
    parser.tooltip.text(value);
    return;
  }

  parser._tooltipHtmlCache = parser._tooltipHtmlCache || new Map();
  if (!parser._tooltipHtmlCache.has(value)) {
    parser._tooltipHtmlCache.set(
      value,
      parser.sanitizer.sanitize(value, parser.tooltip_sanitize_config),
    );
  }

  parser.tooltip.html(parser._tooltipHtmlCache.get(value));
}

/**
 * Check whether a hover handler reference is present.
 *
 * @param {*} hover_handler - Handler function or registered handler id.
 * @returns {boolean} Whether the value can reference a hover handler.
 */
function hasHoverHandler(hover_handler) {
  if (hover_handler == null) {
    return false;
  }
  if (typeof hover_handler === "number" && Number.isNaN(hover_handler)) {
    return false;
  }

  return String(hover_handler).trim() !== "";
}

/**
 * Check whether a click handler reference is present.
 *
 * @param {*} click_handler - Handler function or registered handler id.
 * @returns {boolean} Whether the value can reference a click handler.
 */
function hasClickHandler(click_handler) {
  if (click_handler == null) {
    return false;
  }
  if (typeof click_handler === "number" && Number.isNaN(click_handler)) {
    return false;
  }

  return String(click_handler).trim() !== "";
}

/**
 * Resolve a hover handler function from a function value or registered id.
 *
 * @param {*} hover_handler - Handler function or registered handler id.
 * @returns {Function|null} Hover handler function or null.
 */
function getHoverHandler(hover_handler) {
  if (typeof hover_handler === "function") {
    return hover_handler;
  }

  if (!hasHoverHandler(hover_handler)) {
    return null;
  }

  const hover_handlers = globalThis.ninejs?.hoverHandlers;
  if (!hover_handlers) {
    return null;
  }

  const handler = click_handlers[String(click_handler)];
  return typeof handler === "function" ? handler : null;
}

/**
 * Resolve a click handler function from a function value or registered id.
 *
 * @param {*} click_handler - Handler function or registered handler id.
 * @returns {Function|null} Click handler function or null.
 */
function getClickHandler(click_handler) {
  if (typeof click_handler === "function") {
    return click_handler;
  }

  if (!hasClickHandler(click_handler)) {
    return null;
  }

  const click_handlers = globalThis.ninejs?.clickHandlers;
  if (!click_handlers) {
    return null;
  }

  const handler = click_handlers[String(click_handler)];
  return typeof handler === "function" ? handler : null;
}

/**
 * Repeat values only when they evenly fill the requested length.
 *
 * @param {Array} values - Values to repeat.
 * @param {number} length - Target length.
 * @returns {Array} Original or repeated values.
 */
function repeatExact(values, length) {
  if (values.length === 0 || values.length === length) {
    return values;
  }

  if (length > values.length && length % values.length === 0) {
    return Array.from({ length }, (_, i) => values[i % values.length]);
  }

  return values;
}

/**
 * Normalize hover configuration arrays and node lookup maps in place.
 *
 * @param {object} hover_config - Hover configuration object.
 * @param {number} node_count - Number of plot element nodes.
 * @returns {object} Normalized hover configuration.
 */
export function normalizeHoverConfig(hover_config, node_count) {
  if (hover_config._ninejsNormalized) {
    return hover_config;
  }

  const nodes =
    hover_config.nodes ||
    hover_config.plotElements?.nodes?.() ||
    Array.from({ length: node_count ?? 0 }, () => null);
  const length = node_count ?? nodes.length;
  const tooltipLabels = repeatExact(hover_config.tooltipLabels || [], length);
  let tooltipGroups = repeatExact(hover_config.tooltipGroups || [], length);
  const hoverKeys = repeatExact(hover_config.hoverKeys || [], length);
  const clickHandlers = repeatExact(hover_config.clickHandlers || [], length);
  const hoverHandlers = repeatExact(hover_config.hoverHandlers || [], length);

  if (
    tooltipGroups.length === 0 &&
    (tooltipLabels.length > 0 ||
      clickHandlers.length > 0 ||
      hoverHandlers.length > 0)
  ) {
    tooltipGroups = Array.from({ length }, (_, i) => i);
  }

  hover_config.nodes = nodes;
  hover_config.tooltipLabels = tooltipLabels;
  hover_config.tooltipGroups = tooltipGroups;
  hover_config.hoverKeys = hoverKeys;
  hover_config.clickHandlers = clickHandlers;
  hover_config.hoverHandlers = hoverHandlers;
  hover_config.matchNodesByField = {
    hoverKeys: buildNodesByValue(nodes, hoverKeys),
    tooltipGroups: buildNodesByValue(nodes, tooltipGroups),
  };
  hover_config._ninejsNormalized = true;
  return hover_config;
}

/**
 * Normalize a list of hover configurations.
 *
 * @param {Array<object>} hover_configs - Hover configurations to normalize.
 * @returns {Array<object>} Normalized hover configurations.
 */
export function normalizeHoverConfigs(hover_configs) {
  return hover_configs.map((hover_config) => {
    return normalizeHoverConfig(
      hover_config,
      hover_config.plotElements.nodes().length,
    );
  });
}

/**
 * Build a map from hover field values to matching SVG nodes.
 *
 * @param {Array<SVGElement|null>} nodes - Plot element nodes.
 * @param {Array} values - Field values aligned with nodes.
 * @returns {Map<*, Array<SVGElement>>} Nodes grouped by field value.
 */
function buildNodesByValue(nodes, values) {
  const nodesByValue = new Map();
  const length = Math.min(nodes.length, values.length);

  for (let i = 0; i < length; i += 1) {
    if (nodes[i] === null) {
      continue;
    }

    const value = values[i];
    const valueNodes = nodesByValue.get(value);

    if (valueNodes) {
      valueNodes.push(nodes[i]);
    } else {
      nodesByValue.set(value, [nodes[i]]);
    }
  }

  return nodesByValue;
}

/**
 * Get the hover field and value used to match linked elements.
 *
 * @param {object} record - Hover record.
 * @returns {object} Match field and value.
 */
function getHoverMatch(record) {
  const hover_keys = record.hoverConfig.hoverKeys || [];

  if (hover_keys.length > 0) {
    return { field: "hoverKeys", value: hover_keys[record.index] };
  }

  const tooltip_groups = record.hoverConfig.tooltipGroups || [];
  return { field: "tooltipGroups", value: tooltip_groups[record.index] };
}

/**
 * Clear hover classes for a hover scope.
 *
 * @param {Array<object>} hover_configs - Hover configurations in the scope.
 */
export function clearHoverEffects(hover_configs) {
  const state = getScopeState(hover_configs);

  if (state.dimmedConfigs.length > 0 || state.activeNodes.length > 0) {
    for (const hover_config of state.dimmedConfigs) {
      setNodesClass(hover_config.nodes, "not-hovered", false);
    }
    setNodesClass(state.activeNodes, "not-hovered", false);
    setNodesClass(state.activeNodes, "hovered", false);
    state.dimmedConfigs = [];
    state.activeNodes = [];
    return;
  }

  for (const hover_config of normalizeHoverConfigs(hover_configs)) {
    setNodesClass(hover_config.nodes, "not-hovered", false);
    setNodesClass(hover_config.nodes, "hovered", false);
  }
}

/**
 * Move and show or hide the tooltip for a pointer event.
 *
 * @param {object} parser - Plot parser instance.
 * @param {Event} event - Pointer or mouse event.
 * @param {string} show_tooltip - CSS display value for the tooltip.
 */
export function positionTooltip(parser, event, show_tooltip) {
  parser.tooltip
    .style("display", show_tooltip)
    .style("left", event.pageX + "px")
    .style("top", event.pageY + "px");
}

/**
 * Apply hover classes and tooltip content for one hover record.
 *
 * @param {object} parser - Plot parser instance.
 * @param {object} record - Hover record containing config and node index.
 * @param {Event} event - Pointer or mouse event.
 * @param {Array<object>} hover_configs - Hover configurations in scope.
 */
export function applyHoverRecord(parser, record, event, hover_configs) {
  const hover_config = record.hoverConfig;
  const hover_match = getHoverMatch(record);
  const state = getScopeState(hover_configs);

  clearHoverEffects(hover_configs);

  for (const scoped_hover_config of normalizeHoverConfigs(hover_configs)) {
    const hovered_nodes =
      scoped_hover_config.matchNodesByField[hover_match.field].get(
        hover_match.value,
      ) || [];

    if (hovered_nodes.length === 0) {
      continue;
    }

    if (hover_config.reverseHover) {
      setNodesClass(hovered_nodes, "not-hovered", true);
    } else {
      setNodesClass(scoped_hover_config.nodes, "not-hovered", true);
      setNodesClass(hovered_nodes, "not-hovered", false);
      setNodesClass(hovered_nodes, "hovered", true);
      state.dimmedConfigs.push(scoped_hover_config);
    }
    state.activeNodes.push(...hovered_nodes);
  }

  positionTooltip(parser, event, hover_config.showTooltip);
  setTooltipContent(parser, hover_config.tooltipLabels[record.index]);
}

const hoverScopeStates = new WeakMap();

/**
 * Get persistent hover state for a hover configuration scope.
 *
 * @param {Array<object>} hover_configs - Hover configurations in the scope.
 * @returns {object} Mutable hover state.
 */
function getScopeState(hover_configs) {
  let state = hoverScopeStates.get(hover_configs);

  if (!state) {
    state = { activeNodes: [], dimmedConfigs: [] };
    hoverScopeStates.set(hover_configs, state);
  }

  return state;
}

/**
 * Toggle a CSS class on a list of nodes.
 *
 * @param {Array<SVGElement>} nodes - Nodes to update.
 * @param {string} className - Class name to toggle.
 * @param {boolean} value - Whether the class should be present.
 */
function setNodesClass(nodes, className, value) {
  for (const node of nodes) {
    node.classList.toggle(className, value);
  }
}

/**
 * Attach direct hover behavior to plot elements.
 *
 * @param {object} parser - Plot parser instance.
 * @param {d3.Selection} plot_element - Plot element selection.
 * @param {Array} tooltip_labels - Tooltip labels aligned with nodes.
 * @param {Array} tooltip_groups - Tooltip groups aligned with nodes.
 * @param {string} show_tooltip - CSS display value for the tooltip.
 * @param {boolean} reverse_hover - Whether to invert hover highlighting.
 * @param {Array} click_handlers - Click handler ids aligned with nodes.
 * @param {Array} hover_handlers - Hover handler ids aligned with nodes.
 * @param {Array} hover_keys - Linked-hover keys aligned with nodes.
 * @param {Array<object>|null} hover_configs - Optional hover scope configs.
 */
export function setHoverEffect(
  parser,
  plot_element,
  tooltip_labels,
  tooltip_groups,
  show_tooltip,
  reverse_hover = false,
  click_handlers = [],
  hover_handlers = [],
  hover_keys = [],
  hover_configs = null,
) {
  const nodes = plot_element.nodes();
  const hover_config = normalizeHoverConfig(
    {
      plotElements: plot_element,
      tooltipLabels: tooltip_labels,
      tooltipGroups: tooltip_groups,
      hoverKeys: hover_keys,
      showTooltip: show_tooltip,
      reverseHover: reverse_hover,
      clickHandlers: click_handlers,
      hoverHandlers: hover_handlers,
    },
    nodes.length,
  );
  if (hover_configs !== null) {
    for (const hc of hover_configs) {
      normalizeHoverConfig(hc, hc.plotElements.nodes().length);
    }
  }
  const scoped_hover_configs =
    hover_configs === null ? [hover_config] : hover_configs;

  setClickEffectHandler(parser, plot_element, hover_config.clickHandlers);
  setHoverEffectHandler(parser, plot_element, hover_config.hoverHandlers);

  plot_element
    .on("mouseover", function (event) {
      const i = nodes.indexOf(this);

      applyHoverRecord(
        parser,
        { hoverConfig: hover_config, index: i },
        event,
        scoped_hover_configs,
      );
    })
    .on("mouseout", function () {
      clearHoverEffects(scoped_hover_configs);
      parser.tooltip.style("display", "none");
    });
}

/**
 * Attach click behavior to plot elements.
 *
 * @param {object} parser - Plot parser instance.
 * @param {d3.Selection} plot_element - Plot element selection.
 * @param {Array} click_handlers - Click handler ids aligned with nodes.
 */
export function setClickEffectHandler(
  parser,
  plot_element,
  click_handlers = [],
) {
  const nodes = plot_element.nodes();
  const handlers = click_handlers || [];

  plot_element
    .each(function (_, i) {
      if (hasClickHandler(handlers[i])) {
        this.classList.add("clickable");
      } else {
        this.classList.remove("clickable");
      }
    })
    .on("click", function (event) {
      const i = nodes.indexOf(this);
      const handler = getClickHandler(handlers[i]);

      if (!handler) {
        return;
      }

      handler.call(this, event);
    });
}

/**
 * Attach hover behavior to plot elements.
 *
 * @param {object} parser - Plot parser instance.
 * @param {d3.Selection} plot_element - Plot element selection.
 * @param {Array} hover_handlers - hover handler ids aligned with nodes.
 */
export function setHoverEffectHandler(
  parser,
  plot_element,
  hover_handlers = [],
) {
  const nodes = plot_element.nodes();
  const handlers = hover_handlers || [];

  plot_element
    .each(function (_, i) {
      if (hasHoverHandler(handlers[i])) {
        this.classList.add("hoverable");
      } else {
        this.classList.remove("hoverable");
      }
    })
    .on("mouseover", function (event) {
      const i = nodes.indexOf(this);
      const handler = getHoverHandler(handlers[i]);

      if (!handler) {
        return;
      }

      handler.call(this, event);
    });
}
