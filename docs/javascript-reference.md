## Modules

<dl>
<dt><a href="#module_PlotParser">PlotParser</a></dt>
<dd><p>Plot parser implementation.</p>
</dd>
<dt><a href="#module_PlotParserInit">PlotParserInit</a></dt>
<dd><p>Initialization for the plot parser.</p>
</dd>
</dl>

## Functions

<dl>
<dt><a href="#getNodeAnchorPoints">getNodeAnchorPoints(parser, node)</a> ⇒ <code>Array.&lt;object&gt;</code></dt>
<dd><p>Get SVG-space anchor points for nearest-hover hit testing on a node.</p>
</dd>
<dt><a href="#getPathSamplePoints">getPathSamplePoints(parser, node)</a> ⇒ <code>Array.&lt;object&gt;</code></dt>
<dd><p>Sample an SVG path into SVG-space points.</p>
</dd>
<dt><a href="#getBBoxAnchorPoints">getBBoxAnchorPoints(parser, node, include_corners)</a> ⇒ <code>Array.&lt;object&gt;</code></dt>
<dd><p>Get center and optional edge anchor points from a node bounding box.</p>
</dd>
<dt><a href="#getNodeBBox">getNodeBBox(parser, node)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Get a finite bounding box for an SVG node.</p>
</dd>
<dt><a href="#getAttributeBBox">getAttributeBBox(node)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Build a bounding box from SVG position and size attributes.</p>
</dd>
<dt><a href="#numberAttribute">numberAttribute(node, name)</a> ⇒ <code>number</code></dt>
<dd><p>Read a numeric SVG attribute.</p>
</dd>
<dt><a href="#getPanelBounds">getPanelBounds(parser, axes_class)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Get the interactive panel bounds for an axes group.</p>
</dd>
<dt><a href="#getAxesClipBounds">getAxesClipBounds(parser, axes_class)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Get bounds from the clip path attached to an axes group.</p>
</dd>
<dt><a href="#getClipPathId">getClipPathId(clip_path)</a> ⇒ <code>string</code> | <code>null</code></dt>
<dd><p>Extract the id referenced by an SVG clip-path value.</p>
</dd>
<dt><a href="#eventToSvgPoint">eventToSvgPoint(parser, event)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Convert a pointer event position to SVG coordinates.</p>
</dd>
<dt><a href="#clientPointToSvg">clientPointToSvg(parser, client_x, client_y)</a> ⇒ <code>object</code></dt>
<dd><p>Convert viewport client coordinates to SVG coordinates.</p>
</dd>
<dt><a href="#clientPointToSvgFromViewBox">clientPointToSvgFromViewBox(parser, client_x, client_y)</a> ⇒ <code>object</code></dt>
<dd><p>Convert client coordinates to SVG coordinates using the SVG viewBox.</p>
</dd>
<dt><a href="#getSvgViewBox">getSvgViewBox(svg_node, rect)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Resolve an SVG viewBox from baseVal, attributes, or rendered bounds.</p>
</dd>
<dt><a href="#nodePointToSvg">nodePointToSvg(parser, node, x, y)</a> ⇒ <code>object</code></dt>
<dd><p>Convert a node-local point to SVG root coordinates.</p>
</dd>
<dt><a href="#isFinitePoint">isFinitePoint(point)</a> ⇒ <code>boolean</code></dt>
<dd><p>Check whether a point has finite x and y coordinates.</p>
</dd>
<dt><a href="#isFiniteBBox">isFiniteBBox(bbox)</a> ⇒ <code>boolean</code></dt>
<dd><p>Check whether a bounding box has finite position and size values.</p>
</dd>
<dt><a href="#pointInBounds">pointInBounds(point, bounds)</a> ⇒ <code>boolean</code></dt>
<dd><p>Check whether a point lies within rectangular bounds.</p>
</dd>
<dt><a href="#setTooltipContent">setTooltipContent(parser, label)</a></dt>
<dd><p>Set sanitized tooltip content.</p>
</dd>
<dt><a href="#hasClickHandler">hasClickHandler(click_handler)</a> ⇒ <code>boolean</code></dt>
<dd><p>Check whether a click handler reference is present.</p>
</dd>
<dt><a href="#getClickHandler">getClickHandler(click_handler)</a> ⇒ <code>function</code> | <code>null</code></dt>
<dd><p>Resolve a click handler function from a function value or registered id.</p>
</dd>
<dt><a href="#repeatExact">repeatExact(values, length)</a> ⇒ <code>Array</code></dt>
<dd><p>Repeat values only when they evenly fill the requested length.</p>
</dd>
<dt><a href="#normalizeHoverConfig">normalizeHoverConfig(hover_config, node_count)</a> ⇒ <code>object</code></dt>
<dd><p>Normalize hover configuration arrays and node lookup maps in place.</p>
</dd>
<dt><a href="#normalizeHoverConfigs">normalizeHoverConfigs(hover_configs)</a> ⇒ <code>Array.&lt;object&gt;</code></dt>
<dd><p>Normalize a list of hover configurations.</p>
</dd>
<dt><a href="#buildNodesByValue">buildNodesByValue(nodes, values)</a> ⇒ <code>Map.&lt;*, Array.&lt;SVGElement&gt;&gt;</code></dt>
<dd><p>Build a map from hover field values to matching SVG nodes.</p>
</dd>
<dt><a href="#getHoverMatch">getHoverMatch(record)</a> ⇒ <code>object</code></dt>
<dd><p>Get the hover field and value used to match linked elements.</p>
</dd>
<dt><a href="#clearHoverEffects">clearHoverEffects(hover_configs)</a></dt>
<dd><p>Clear hover classes for a hover scope.</p>
</dd>
<dt><a href="#positionTooltip">positionTooltip(parser, event, show_tooltip)</a></dt>
<dd><p>Move and show or hide the tooltip for a pointer event.</p>
</dd>
<dt><a href="#applyHoverRecord">applyHoverRecord(parser, record, event, hover_configs)</a></dt>
<dd><p>Apply hover classes and tooltip content for one hover record.</p>
</dd>
<dt><a href="#getScopeState">getScopeState(hover_configs)</a> ⇒ <code>object</code></dt>
<dd><p>Get persistent hover state for a hover configuration scope.</p>
</dd>
<dt><a href="#setNodesClass">setNodesClass(nodes, className, value)</a></dt>
<dd><p>Toggle a CSS class on a list of nodes.</p>
</dd>
<dt><a href="#setHoverEffect">setHoverEffect(parser, plot_element, tooltip_labels, tooltip_groups, show_tooltip, reverse_hover, click_handlers, hover_keys, hover_configs)</a></dt>
<dd><p>Attach direct hover behavior to plot elements.</p>
</dd>
<dt><a href="#setClickEffect">setClickEffect(parser, plot_element, click_handlers)</a></dt>
<dd><p>Attach click behavior to plot elements.</p>
</dd>
<dt><a href="#setNearestHoverEffect">setNearestHoverEffect(parser, svg, axes_class, hover_configs, hover_scope_configs)</a></dt>
<dd><p>Attach nearest-point hover behavior for one axes group.</p>
</dd>
<dt><a href="#updateNearestHover">updateNearestHover(parser, event, state)</a></dt>
<dd><p>Update the active nearest-hover record for a pointer event.</p>
</dd>
<dt><a href="#getHoverScope">getHoverScope(record, state)</a> ⇒ <code>Array.&lt;object&gt;</code></dt>
<dd><p>Choose the hover scope for a nearest-hover record.</p>
</dd>
<dt><a href="#ensureNearestHoverPanel">ensureNearestHoverPanel(axes_node, panel_bounds)</a></dt>
<dd><p>Ensure an invisible panel exists to receive nearest-hover pointer events.</p>
</dd>
<dt><a href="#clearActiveNearestHover">clearActiveNearestHover(parser, state)</a></dt>
<dd><p>Clear the active nearest-hover record and tooltip.</p>
</dd>
<dt><a href="#getHoverRecords">getHoverRecords(hover_configs)</a> ⇒ <code>Array.&lt;object&gt;</code></dt>
<dd><p>Build hover records from normalized hover configurations.</p>
</dd>
<dt><a href="#getNearestAnchors">getNearestAnchors(parser, records, bounds)</a> ⇒ <code>Array.&lt;object&gt;</code></dt>
<dd><p>Build nearest-hover anchor points for hover records.</p>
</dd>
<dt><a href="#getDirectHoverRecord">getDirectHoverRecord(event, state)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Resolve a directly targeted plot element to its hover record.</p>
</dd>
<dt><a href="#closestPlotElement">closestPlotElement(node, axes_node)</a> ⇒ <code>Element</code> | <code>null</code></dt>
<dd><p>Find the nearest ancestor plot element within an axes group.</p>
</dd>
<dt><a href="#setZoomEffect">setZoomEffect(svg, options)</a> ⇒ <code>object</code> | <code>null</code></dt>
<dd><p>Attach visual zoom and pan behavior to the rendered SVG chart.</p>
</dd>
</dl>

<a name="module_PlotParser"></a>

## PlotParser
Plot parser implementation.


* [PlotParser](#module_PlotParser)
    * [module.exports](#exp_module_PlotParser--module.exports) ⏏
        * [new module.exports(svg, tooltip, sanitizer, nearest_sample_spacing, nearest_max_samples)](#new_module_PlotParser--module.exports_new)
        * [.findBars(svg, axes_class, tooltip_groups)](#module_PlotParser--module.exports+findBars) ⇒ <code>d3.Selection</code>
        * [.findBoxes(svg, axes_class, tooltip_groups)](#module_PlotParser--module.exports+findBoxes) ⇒ <code>d3.Selection</code>
        * [.findPoints(svg, axes_class, tooltip_groups)](#module_PlotParser--module.exports+findPoints) ⇒ <code>d3.Selection</code>
        * [.findLines(svg, axes_class)](#module_PlotParser--module.exports+findLines) ⇒ <code>d3.Selection</code>
        * [.findAreas(svg, axes_class)](#module_PlotParser--module.exports+findAreas) ⇒ <code>d3.Selection</code>
        * [.findPolygons(svg, axes_class)](#module_PlotParser--module.exports+findPolygons) ⇒ <code>d3.Selection</code>
        * [.getSvgSummary(svg, axes_config)](#module_PlotParser--module.exports+getSvgSummary) ⇒ <code>string</code>
        * [.getAxesSummary(axes_class, plot_elements)](#module_PlotParser--module.exports+getAxesSummary) ⇒ <code>object</code>
        * [.logParseSummary(svg_summary, axes_summaries)](#module_PlotParser--module.exports+logParseSummary)
        * [._selectionSize(selection)](#module_PlotParser--module.exports+_selectionSize) ⇒ <code>number</code>
        * [._formatCount(count, noun)](#module_PlotParser--module.exports+_formatCount) ⇒ <code>string</code>
        * [._formatIds(ids)](#module_PlotParser--module.exports+_formatIds) ⇒ <code>string</code>

<a name="exp_module_PlotParser--module.exports"></a>

### module.exports ⏏
Parses a Matplotlib-generated SVG and labels plot elements for ninejs
interactions.

**Kind**: Exported class  
<a name="new_module_PlotParser--module.exports_new"></a>

#### new module.exports(svg, tooltip, sanitizer, nearest_sample_spacing, nearest_max_samples)
Create a parser for one SVG plot.


| Param | Type | Default | Description |
| --- | --- | --- | --- |
| svg | <code>d3.Selection</code> |  | SVG root selection. |
| tooltip | <code>d3.Selection</code> |  | Tooltip container selection. |
| sanitizer | <code>object</code> |  | Optional DOMPurify-compatible sanitizer. |
| nearest_sample_spacing | <code>number</code> | <code>12</code> | Pixel spacing for nearest-hover sampling. |
| nearest_max_samples | <code>number</code> | <code>48</code> | Maximum samples used for path hit-testing. |

<a name="module_PlotParser--module.exports+findBars"></a>

#### module.exports.findBars(svg, axes_class, tooltip_groups) ⇒ <code>d3.Selection</code>
Find bar paths in an axes group and assign tooltip group identifiers.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>d3.Selection</code> - Bar element selection.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_class | <code>string</code> | Matplotlib axes group id. |
| tooltip_groups | <code>Array.&lt;string&gt;</code> | Tooltip group id per bar. |

<a name="module_PlotParser--module.exports+findBoxes"></a>

#### module.exports.findBoxes(svg, axes_class, tooltip_groups) ⇒ <code>d3.Selection</code>
Find boxplot glyphs in an axes group and assign tooltip group identifiers.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>d3.Selection</code> - Box element selection.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_class | <code>string</code> | Matplotlib axes group id. |
| tooltip_groups | <code>Array.&lt;string&gt;</code> | Tooltip group id per box. |

<a name="module_PlotParser--module.exports+findPoints"></a>

#### module.exports.findPoints(svg, axes_class, tooltip_groups) ⇒ <code>d3.Selection</code>
Find point markers in an axes group and assign tooltip group identifiers.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>d3.Selection</code> - Point element selection.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_class | <code>string</code> | Matplotlib axes group id. |
| tooltip_groups | <code>Array.&lt;string&gt;</code> | Tooltip group id per point. |

<a name="module_PlotParser--module.exports+findLines"></a>

#### module.exports.findLines(svg, axes_class) ⇒ <code>d3.Selection</code>
Find line paths in an axes group while excluding axis decoration lines.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>d3.Selection</code> - Line element selection.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_class | <code>string</code> | Matplotlib axes group id. |

<a name="module_PlotParser--module.exports+findAreas"></a>

#### module.exports.findAreas(svg, axes_class) ⇒ <code>d3.Selection</code>
Find area fill paths in an axes group.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>d3.Selection</code> - Area element selection.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_class | <code>string</code> | Matplotlib axes group id. |

<a name="module_PlotParser--module.exports+findPolygons"></a>

#### module.exports.findPolygons(svg, axes_class) ⇒ <code>d3.Selection</code>
Find polygon paths in an axes group.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>d3.Selection</code> - Polygon element selection.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_class | <code>string</code> | Matplotlib axes group id. |

<a name="module_PlotParser--module.exports+getSvgSummary"></a>

#### module.exports.getSvgSummary(svg, axes_config) ⇒ <code>string</code>
Build a short parse summary for all axes groups in the SVG.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>string</code> - Human-readable SVG summary.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_config | <code>object</code> | Parser configuration keyed by axes id. |

<a name="module_PlotParser--module.exports+getAxesSummary"></a>

#### module.exports.getAxesSummary(axes_class, plot_elements) ⇒ <code>object</code>
Summarize detected plot elements for one axes group.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>object</code> - Axes summary object.  

| Param | Type | Description |
| --- | --- | --- |
| axes_class | <code>string</code> | Matplotlib axes group id. |
| plot_elements | <code>object</code> | Element selections keyed by geom type. |

<a name="module_PlotParser--module.exports+logParseSummary"></a>

#### module.exports.logParseSummary(svg_summary, axes_summaries)
Log the SVG and axes parse summaries to the browser console.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  

| Param | Type | Description |
| --- | --- | --- |
| svg_summary | <code>string</code> | Human-readable SVG summary. |
| axes_summaries | <code>Array.&lt;object&gt;</code> | Per-axes summary objects. |

<a name="module_PlotParser--module.exports+_selectionSize"></a>

#### module.exports.\_selectionSize(selection) ⇒ <code>number</code>
Count the elements in a D3 selection.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>number</code> - Number of selected elements.  

| Param | Type | Description |
| --- | --- | --- |
| selection | <code>d3.Selection</code> | Selection to count. |

<a name="module_PlotParser--module.exports+_formatCount"></a>

#### module.exports.\_formatCount(count, noun) ⇒ <code>string</code>
Format a count and noun with simple pluralization.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>string</code> - Formatted count.  

| Param | Type | Description |
| --- | --- | --- |
| count | <code>number</code> | Count to format. |
| noun | <code>string</code> | Singular noun. |

<a name="module_PlotParser--module.exports+_formatIds"></a>

#### module.exports.\_formatIds(ids) ⇒ <code>string</code>
Format a list of SVG ids for log output.

**Kind**: instance method of [<code>module.exports</code>](#exp_module_PlotParser--module.exports)  
**Returns**: <code>string</code> - Parenthesized ids or a none marker.  

| Param | Type | Description |
| --- | --- | --- |
| ids | <code>Array.&lt;string&gt;</code> | SVG ids to format. |

<a name="module_PlotParserInit"></a>

## PlotParserInit
Initialization for the plot parser.

<a name="exp_module_PlotParserInit--module.exports"></a>

### module.exports() ⏏
Initialize ninejs interactions for the embedded plot.

**Kind**: Exported function  
<a name="getNodeAnchorPoints"></a>

## getNodeAnchorPoints(parser, node) ⇒ <code>Array.&lt;object&gt;</code>
Get SVG-space anchor points for nearest-hover hit testing on a node.

**Kind**: global function  
**Returns**: <code>Array.&lt;object&gt;</code> - Anchor points in SVG coordinates.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| node | <code>SVGElement</code> | Plot element node. |

<a name="getPathSamplePoints"></a>

## getPathSamplePoints(parser, node) ⇒ <code>Array.&lt;object&gt;</code>
Sample an SVG path into SVG-space points.

**Kind**: global function  
**Returns**: <code>Array.&lt;object&gt;</code> - Sampled points in SVG coordinates.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| node | <code>SVGElement</code> | Path-like SVG node. |

<a name="getBBoxAnchorPoints"></a>

## getBBoxAnchorPoints(parser, node, include_corners) ⇒ <code>Array.&lt;object&gt;</code>
Get center and optional edge anchor points from a node bounding box.

**Kind**: global function  
**Returns**: <code>Array.&lt;object&gt;</code> - Anchor points in SVG coordinates.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| node | <code>SVGElement</code> | SVG node to inspect. |
| include_corners | <code>boolean</code> | Whether to include corners and edge midpoints. |

<a name="getNodeBBox"></a>

## getNodeBBox(parser, node) ⇒ <code>object</code> \| <code>null</code>
Get a finite bounding box for an SVG node.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - Bounding box or null when unavailable.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| node | <code>SVGElement</code> | SVG node to inspect. |

<a name="getAttributeBBox"></a>

## getAttributeBBox(node) ⇒ <code>object</code> \| <code>null</code>
Build a bounding box from SVG position and size attributes.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - Bounding box or null when attributes are incomplete.  

| Param | Type | Description |
| --- | --- | --- |
| node | <code>SVGElement</code> | SVG node to inspect. |

<a name="numberAttribute"></a>

## numberAttribute(node, name) ⇒ <code>number</code>
Read a numeric SVG attribute.

**Kind**: global function  
**Returns**: <code>number</code> - Numeric value, or NaN when missing or invalid.  

| Param | Type | Description |
| --- | --- | --- |
| node | <code>SVGElement</code> | SVG node to inspect. |
| name | <code>string</code> | Attribute name. |

<a name="getPanelBounds"></a>

## getPanelBounds(parser, axes_class) ⇒ <code>object</code> \| <code>null</code>
Get the interactive panel bounds for an axes group.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - Panel bounds or null when unavailable.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| axes_class | <code>string</code> | Matplotlib axes group id. |

<a name="getAxesClipBounds"></a>

## getAxesClipBounds(parser, axes_class) ⇒ <code>object</code> \| <code>null</code>
Get bounds from the clip path attached to an axes group.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - Clip bounds or null when unavailable.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| axes_class | <code>string</code> | Matplotlib axes group id. |

<a name="getClipPathId"></a>

## getClipPathId(clip_path) ⇒ <code>string</code> \| <code>null</code>
Extract the id referenced by an SVG clip-path value.

**Kind**: global function  
**Returns**: <code>string</code> \| <code>null</code> - Clip path id or null when absent.  

| Param | Type | Description |
| --- | --- | --- |
| clip_path | <code>string</code> \| <code>null</code> | SVG clip-path attribute value. |

<a name="eventToSvgPoint"></a>

## eventToSvgPoint(parser, event) ⇒ <code>object</code> \| <code>null</code>
Convert a pointer event position to SVG coordinates.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - SVG point or null when coordinates are invalid.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| event | <code>Event</code> | Pointer or mouse event. |

<a name="clientPointToSvg"></a>

## clientPointToSvg(parser, client_x, client_y) ⇒ <code>object</code>
Convert viewport client coordinates to SVG coordinates.

**Kind**: global function  
**Returns**: <code>object</code> - SVG point.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| client_x | <code>number</code> | Client x coordinate. |
| client_y | <code>number</code> | Client y coordinate. |

<a name="clientPointToSvgFromViewBox"></a>

## clientPointToSvgFromViewBox(parser, client_x, client_y) ⇒ <code>object</code>
Convert client coordinates to SVG coordinates using the SVG viewBox.

**Kind**: global function  
**Returns**: <code>object</code> - SVG point.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| client_x | <code>number</code> | Client x coordinate. |
| client_y | <code>number</code> | Client y coordinate. |

<a name="getSvgViewBox"></a>

## getSvgViewBox(svg_node, rect) ⇒ <code>object</code> \| <code>null</code>
Resolve an SVG viewBox from baseVal, attributes, or rendered bounds.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - ViewBox-like bounds or null when unavailable.  

| Param | Type | Description |
| --- | --- | --- |
| svg_node | <code>SVGSVGElement</code> | SVG root node. |
| rect | <code>DOMRect</code> | Rendered SVG bounds. |

<a name="nodePointToSvg"></a>

## nodePointToSvg(parser, node, x, y) ⇒ <code>object</code>
Convert a node-local point to SVG root coordinates.

**Kind**: global function  
**Returns**: <code>object</code> - SVG point.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| node | <code>SVGElement</code> | SVG node containing the point. |
| x | <code>number</code> | Node-local x coordinate. |
| y | <code>number</code> | Node-local y coordinate. |

<a name="isFinitePoint"></a>

## isFinitePoint(point) ⇒ <code>boolean</code>
Check whether a point has finite x and y coordinates.

**Kind**: global function  
**Returns**: <code>boolean</code> - Whether the point is finite.  

| Param | Type | Description |
| --- | --- | --- |
| point | <code>object</code> \| <code>null</code> | Point to inspect. |

<a name="isFiniteBBox"></a>

## isFiniteBBox(bbox) ⇒ <code>boolean</code>
Check whether a bounding box has finite position and size values.

**Kind**: global function  
**Returns**: <code>boolean</code> - Whether the bounding box is finite.  

| Param | Type | Description |
| --- | --- | --- |
| bbox | <code>object</code> \| <code>null</code> | Bounding box to inspect. |

<a name="pointInBounds"></a>

## pointInBounds(point, bounds) ⇒ <code>boolean</code>
Check whether a point lies within rectangular bounds.

**Kind**: global function  
**Returns**: <code>boolean</code> - Whether the point is inside the bounds.  

| Param | Type | Description |
| --- | --- | --- |
| point | <code>object</code> | Point to inspect. |
| bounds | <code>object</code> | Rectangular bounds. |

<a name="setTooltipContent"></a>

## setTooltipContent(parser, label)
Set sanitized tooltip content.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| label | <code>\*</code> | Tooltip label value. |

<a name="hasClickHandler"></a>

## hasClickHandler(click_handler) ⇒ <code>boolean</code>
Check whether a click handler reference is present.

**Kind**: global function  
**Returns**: <code>boolean</code> - Whether the value can reference a click handler.  

| Param | Type | Description |
| --- | --- | --- |
| click_handler | <code>\*</code> | Handler function or registered handler id. |

<a name="getClickHandler"></a>

## getClickHandler(click_handler) ⇒ <code>function</code> \| <code>null</code>
Resolve a click handler function from a function value or registered id.

**Kind**: global function  
**Returns**: <code>function</code> \| <code>null</code> - Click handler function or null.  

| Param | Type | Description |
| --- | --- | --- |
| click_handler | <code>\*</code> | Handler function or registered handler id. |

<a name="repeatExact"></a>

## repeatExact(values, length) ⇒ <code>Array</code>
Repeat values only when they evenly fill the requested length.

**Kind**: global function  
**Returns**: <code>Array</code> - Original or repeated values.  

| Param | Type | Description |
| --- | --- | --- |
| values | <code>Array</code> | Values to repeat. |
| length | <code>number</code> | Target length. |

<a name="normalizeHoverConfig"></a>

## normalizeHoverConfig(hover_config, node_count) ⇒ <code>object</code>
Normalize hover configuration arrays and node lookup maps in place.

**Kind**: global function  
**Returns**: <code>object</code> - Normalized hover configuration.  

| Param | Type | Description |
| --- | --- | --- |
| hover_config | <code>object</code> | Hover configuration object. |
| node_count | <code>number</code> | Number of plot element nodes. |

<a name="normalizeHoverConfigs"></a>

## normalizeHoverConfigs(hover_configs) ⇒ <code>Array.&lt;object&gt;</code>
Normalize a list of hover configurations.

**Kind**: global function  
**Returns**: <code>Array.&lt;object&gt;</code> - Normalized hover configurations.  

| Param | Type | Description |
| --- | --- | --- |
| hover_configs | <code>Array.&lt;object&gt;</code> | Hover configurations to normalize. |

<a name="buildNodesByValue"></a>

## buildNodesByValue(nodes, values) ⇒ <code>Map.&lt;\*, Array.&lt;SVGElement&gt;&gt;</code>
Build a map from hover field values to matching SVG nodes.

**Kind**: global function  
**Returns**: <code>Map.&lt;\*, Array.&lt;SVGElement&gt;&gt;</code> - Nodes grouped by field value.  

| Param | Type | Description |
| --- | --- | --- |
| nodes | <code>Array.&lt;(SVGElement\|null)&gt;</code> | Plot element nodes. |
| values | <code>Array</code> | Field values aligned with nodes. |

<a name="getHoverMatch"></a>

## getHoverMatch(record) ⇒ <code>object</code>
Get the hover field and value used to match linked elements.

**Kind**: global function  
**Returns**: <code>object</code> - Match field and value.  

| Param | Type | Description |
| --- | --- | --- |
| record | <code>object</code> | Hover record. |

<a name="clearHoverEffects"></a>

## clearHoverEffects(hover_configs)
Clear hover classes for a hover scope.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| hover_configs | <code>Array.&lt;object&gt;</code> | Hover configurations in the scope. |

<a name="positionTooltip"></a>

## positionTooltip(parser, event, show_tooltip)
Move and show or hide the tooltip for a pointer event.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| event | <code>Event</code> | Pointer or mouse event. |
| show_tooltip | <code>string</code> | CSS display value for the tooltip. |

<a name="applyHoverRecord"></a>

## applyHoverRecord(parser, record, event, hover_configs)
Apply hover classes and tooltip content for one hover record.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| record | <code>object</code> | Hover record containing config and node index. |
| event | <code>Event</code> | Pointer or mouse event. |
| hover_configs | <code>Array.&lt;object&gt;</code> | Hover configurations in scope. |

<a name="getScopeState"></a>

## getScopeState(hover_configs) ⇒ <code>object</code>
Get persistent hover state for a hover configuration scope.

**Kind**: global function  
**Returns**: <code>object</code> - Mutable hover state.  

| Param | Type | Description |
| --- | --- | --- |
| hover_configs | <code>Array.&lt;object&gt;</code> | Hover configurations in the scope. |

<a name="setNodesClass"></a>

## setNodesClass(nodes, className, value)
Toggle a CSS class on a list of nodes.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| nodes | <code>Array.&lt;SVGElement&gt;</code> | Nodes to update. |
| className | <code>string</code> | Class name to toggle. |
| value | <code>boolean</code> | Whether the class should be present. |

<a name="setHoverEffect"></a>

## setHoverEffect(parser, plot_element, tooltip_labels, tooltip_groups, show_tooltip, reverse_hover, click_handlers, hover_keys, hover_configs)
Attach direct hover behavior to plot elements.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| plot_element | <code>d3.Selection</code> | Plot element selection. |
| tooltip_labels | <code>Array</code> | Tooltip labels aligned with nodes. |
| tooltip_groups | <code>Array</code> | Tooltip groups aligned with nodes. |
| show_tooltip | <code>string</code> | CSS display value for the tooltip. |
| reverse_hover | <code>boolean</code> | Whether to invert hover highlighting. |
| click_handlers | <code>Array</code> | Click handler ids aligned with nodes. |
| hover_keys | <code>Array</code> | Linked-hover keys aligned with nodes. |
| hover_configs | <code>Array.&lt;object&gt;</code> \| <code>null</code> | Optional hover scope configs. |

<a name="setClickEffect"></a>

## setClickEffect(parser, plot_element, click_handlers)
Attach click behavior to plot elements.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| plot_element | <code>d3.Selection</code> | Plot element selection. |
| click_handlers | <code>Array</code> | Click handler ids aligned with nodes. |

<a name="setNearestHoverEffect"></a>

## setNearestHoverEffect(parser, svg, axes_class, hover_configs, hover_scope_configs)
Attach nearest-point hover behavior for one axes group.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| svg | <code>d3.Selection</code> | SVG root selection. |
| axes_class | <code>string</code> | Matplotlib axes group id. |
| hover_configs | <code>Array.&lt;object&gt;</code> | Hover configurations for this axes. |
| hover_scope_configs | <code>Array.&lt;object&gt;</code> \| <code>null</code> | Optional linked-hover scope. |

<a name="updateNearestHover"></a>

## updateNearestHover(parser, event, state)
Update the active nearest-hover record for a pointer event.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| event | <code>Event</code> | Pointer or mouse event. |
| state | <code>object</code> | Nearest-hover state. |

<a name="getHoverScope"></a>

## getHoverScope(record, state) ⇒ <code>Array.&lt;object&gt;</code>
Choose the hover scope for a nearest-hover record.

**Kind**: global function  
**Returns**: <code>Array.&lt;object&gt;</code> - Hover configurations in scope.  

| Param | Type | Description |
| --- | --- | --- |
| record | <code>object</code> | Hover record. |
| state | <code>object</code> | Nearest-hover state. |

<a name="ensureNearestHoverPanel"></a>

## ensureNearestHoverPanel(axes_node, panel_bounds)
Ensure an invisible panel exists to receive nearest-hover pointer events.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| axes_node | <code>SVGGElement</code> | Axes group node. |
| panel_bounds | <code>object</code> | Panel bounds. |

<a name="clearActiveNearestHover"></a>

## clearActiveNearestHover(parser, state)
Clear the active nearest-hover record and tooltip.

**Kind**: global function  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| state | <code>object</code> | Nearest-hover state. |

<a name="getHoverRecords"></a>

## getHoverRecords(hover_configs) ⇒ <code>Array.&lt;object&gt;</code>
Build hover records from normalized hover configurations.

**Kind**: global function  
**Returns**: <code>Array.&lt;object&gt;</code> - Hover records aligned to plot nodes.  

| Param | Type | Description |
| --- | --- | --- |
| hover_configs | <code>Array.&lt;object&gt;</code> | Hover configurations to index. |

<a name="getNearestAnchors"></a>

## getNearestAnchors(parser, records, bounds) ⇒ <code>Array.&lt;object&gt;</code>
Build nearest-hover anchor points for hover records.

**Kind**: global function  
**Returns**: <code>Array.&lt;object&gt;</code> - Anchor points with attached hover records.  

| Param | Type | Description |
| --- | --- | --- |
| parser | <code>object</code> | Plot parser instance. |
| records | <code>Array.&lt;object&gt;</code> | Hover records to sample. |
| bounds | <code>object</code> \| <code>null</code> | Optional bounds filter. |

<a name="getDirectHoverRecord"></a>

## getDirectHoverRecord(event, state) ⇒ <code>object</code> \| <code>null</code>
Resolve a directly targeted plot element to its hover record.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - Hover record or null.  

| Param | Type | Description |
| --- | --- | --- |
| event | <code>Event</code> | Pointer or mouse event. |
| state | <code>object</code> | Nearest-hover state. |

<a name="closestPlotElement"></a>

## closestPlotElement(node, axes_node) ⇒ <code>Element</code> \| <code>null</code>
Find the nearest ancestor plot element within an axes group.

**Kind**: global function  
**Returns**: <code>Element</code> \| <code>null</code> - Matching plot element or null.  

| Param | Type | Description |
| --- | --- | --- |
| node | <code>Node</code> | Starting DOM node. |
| axes_node | <code>SVGGElement</code> | Axes group node. |

<a name="setZoomEffect"></a>

## setZoomEffect(svg, options) ⇒ <code>object</code> \| <code>null</code>
Attach visual zoom and pan behavior to the rendered SVG chart.

**Kind**: global function  
**Returns**: <code>object</code> \| <code>null</code> - D3 zoom behavior or null when unavailable.  

| Param | Type | Description |
| --- | --- | --- |
| svg | <code>d3.Selection</code> | SVG root selection. |
| options | <code>object</code> | Zoom options. |

