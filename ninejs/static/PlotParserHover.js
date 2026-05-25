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
    clickHandlers: clickHandlers,
  };
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
  const tooltip_groups = hover_config.tooltipGroups;
  const hovered_group = tooltip_groups[record.index];

  parser.clearHoverEffects(hover_configs);
  const hovered_elements = hover_config.plotElements.filter((_, j) => {
    return tooltip_groups[j] === hovered_group;
  });

  if (hover_config.reverseHover) {
    hovered_elements.classed("not-hovered", true);
  } else {
    hover_config.plotElements.classed("not-hovered", true);
    hovered_elements.classed("not-hovered", false).classed("hovered", true);
  }

  parser.positionTooltip(event, hover_config.showTooltip);
  parser.setTooltipContent(hover_config.tooltipLabels[record.index]);
}

export function setHoverEffect(
  parser,
  plot_element,
  tooltip_labels,
  tooltip_groups,
  show_tooltip,
  reverse_hover = false,
  click_handlers = [],
) {
  const nodes = plot_element.nodes();
  const hover_config = normalizeHoverConfig(
    {
      plotElements: plot_element,
      tooltipLabels: tooltip_labels,
      tooltipGroups: tooltip_groups,
      showTooltip: show_tooltip,
      reverseHover: reverse_hover,
      clickHandlers: click_handlers,
    },
    nodes.length,
  );
  const hover_configs = [hover_config];

  parser.setClickEffect(plot_element, hover_config.clickHandlers);

  plot_element
    .on("mouseover", function (event) {
      const i = nodes.indexOf(this);

      parser.applyHoverRecord(
        { hoverConfig: hover_config, index: i },
        event,
        hover_configs,
      );
    })
    .on("mouseout", function () {
      parser.clearHoverEffects(hover_configs);
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
