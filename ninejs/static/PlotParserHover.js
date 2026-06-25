export function setTooltipContent(parser, label) {
  const value = label == null ? "" : String(label);

  if (!parser.sanitizer || typeof parser.sanitizer.sanitize !== "function") {
    parser.tooltip.text(value);
    return;
  }

  parser.tooltip.html(
    parser.sanitizer.sanitize(value, parser.tooltip_sanitize_config),
  );
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
  const tooltipLabels = repeatExact(
    hover_config.tooltipLabels || [],
    node_count,
  );
  let tooltipGroups = repeatExact(hover_config.tooltipGroups || [], node_count);
  const hoverKeys = repeatExact(hover_config.hoverKeys || [], node_count);
  const clickHandlers = repeatExact(
    hover_config.clickHandlers || [],
    node_count,
  );

  if (
    tooltipGroups.length === 0 &&
    (tooltipLabels.length > 0 || clickHandlers.length > 0)
  ) {
    tooltipGroups = Array.from({ length: node_count }, (_, i) => i);
  }

  return {
    ...hover_config,
    tooltipLabels: tooltipLabels,
    tooltipGroups: tooltipGroups,
    hoverKeys: hoverKeys,
    clickHandlers: clickHandlers,
  };
}

export function normalizeHoverConfigs(hover_configs) {
  return hover_configs.map((hover_config) => {
    return normalizeHoverConfig(
      hover_config,
      hover_config.plotElements.nodes().length,
    );
  });
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
  for (const hover_config of hover_configs) {
    hover_config.plotElements
      .classed("not-hovered", false)
      .classed("hovered", false);
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

  clearHoverEffects(hover_configs);

  for (const scoped_hover_config of hover_configs) {
    const hover_values = scoped_hover_config[hover_match.field] || [];

    if (hover_values.length === 0) {
      continue;
    }

    const hovered_elements = scoped_hover_config.plotElements.filter((_, j) => {
      return hover_values[j] === hover_match.value;
    });

    if (hover_config.reverseHover) {
      hovered_elements.classed("not-hovered", true);
    } else {
      scoped_hover_config.plotElements.classed("not-hovered", true);
      hovered_elements.classed("not-hovered", false).classed("hovered", true);
    }
  }

  positionTooltip(parser, event, hover_config.showTooltip);
  setTooltipContent(parser, hover_config.tooltipLabels[record.index]);
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
