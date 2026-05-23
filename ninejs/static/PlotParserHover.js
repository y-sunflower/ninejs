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

export function normalizeHoverConfig(hover_config, node_count) {
  return {
    ...hover_config,
    tooltipLabels: repeatExact(hover_config.tooltipLabels || [], node_count),
    tooltipGroups: repeatExact(hover_config.tooltipGroups || [], node_count),
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
    .style("left", event.pageX + parser.tooltip_x_shift + "px")
    .style("top", event.pageY + parser.tooltip_y_shift + "px");
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
) {
  const nodes = plot_element.nodes();
  const hover_config = normalizeHoverConfig(
    {
      plotElements: plot_element,
      tooltipLabels: tooltip_labels,
      tooltipGroups: tooltip_groups,
      showTooltip: show_tooltip,
      reverseHover: reverse_hover,
    },
    nodes.length,
  );
  const hover_configs = [hover_config];

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
