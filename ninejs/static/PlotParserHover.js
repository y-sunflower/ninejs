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

function repeatExact(values, length) {
  if (values.length === 0 || values.length === length) {
    return values;
  }

  if (length > values.length && length % values.length === 0) {
    return Array.from({ length: length }, (_, i) => values[i % values.length]);
  }

  return values;
}

function hasClickHandler(click_handler) {
  if (click_handler == null) {
    return false;
  }
  if (typeof click_handler === "number" && Number.isNaN(click_handler)) {
    return false;
  }

  return String(click_handler).trim() !== "";
}

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

  if (
    tooltipGroups.length === 0 &&
    (tooltipLabels.length > 0 || clickHandlers.length > 0)
  ) {
    tooltipGroups = Array.from({ length: length }, (_, i) => i);
  }

  hover_config.nodes = nodes;
  hover_config.tooltipLabels = tooltipLabels;
  hover_config.tooltipGroups = tooltipGroups;
  hover_config.hoverKeys = hoverKeys;
  hover_config.clickHandlers = clickHandlers;
  hover_config.matchNodesByField = {
    hoverKeys: buildNodesByValue(nodes, hoverKeys),
    tooltipGroups: buildNodesByValue(nodes, tooltipGroups),
  };
  hover_config._ninejsNormalized = true;
  return hover_config;
}

export function normalizeHoverConfigs(hover_configs) {
  return hover_configs.map((hover_config) => {
    return normalizeHoverConfig(
      hover_config,
      hover_config.plotElements.nodes().length,
    );
  });
}

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

function getHoverMatch(record) {
  const hover_keys = record.hoverConfig.hoverKeys || [];

  if (hover_keys.length > 0) {
    return { field: "hoverKeys", value: hover_keys[record.index] };
  }

  const tooltip_groups = record.hoverConfig.tooltipGroups || [];
  return { field: "tooltipGroups", value: tooltip_groups[record.index] };
}

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

export function positionTooltip(parser, event, show_tooltip) {
  parser.tooltip
    .style("display", show_tooltip)
    .style("left", event.pageX + "px")
    .style("top", event.pageY + "px");
}

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

function getScopeState(hover_configs) {
  let state = hoverScopeStates.get(hover_configs);

  if (!state) {
    state = { activeNodes: [], dimmedConfigs: [] };
    hoverScopeStates.set(hover_configs, state);
  }

  return state;
}

function setNodesClass(nodes, className, value) {
  for (const node of nodes) {
    node.classList.toggle(className, value);
  }
}

export function setHoverEffect(
  parser,
  plot_element,
  tooltip_labels,
  tooltip_groups,
  show_tooltip,
  reverse_hover = false,
  click_handlers = [],
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
    },
    nodes.length,
  );
  const scoped_hover_configs =
    hover_configs === null
      ? [hover_config]
      : normalizeHoverConfigs(hover_configs);

  setClickEffect(parser, plot_element, hover_config.clickHandlers);

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

export function setClickEffect(parser, plot_element, click_handlers = []) {
  const nodes = plot_element.nodes();
  const handlers = repeatExact(click_handlers || [], nodes.length);

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
