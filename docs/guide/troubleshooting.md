---
title: Troubleshooting
---

Since `ninejs` handles many tasks with JavaScript in the browser, you may encounter "silent" errors when you open your HTML file.

In practice, your Python code may run without errors, but the output may still not be what you expected. There may be multiple reasons for this. This guide explains common issues and how to debug them.

## Developer tools

Your browser includes developer tools. They let you inspect many parts of the page, but here we're mostly interested in the "console" section.

The console displays messages from the web page, including errors. Many are routine browser messages, but some might point to an issue in `ninejs`.

How to open the developer tools is browser-specific, but there's likely a shortcut to make it convenient. For instance, on macOS + Firefox I use ++option+cmd+i++.

Once open, you can find messages from `ninejs`, such as the number of "points" (scatter plot) or "lines" (line plot) found. This can give you clues about what is going wrong.

## Debug `ninejs`

### Workflow

For a smoother workflow, install [`live-server`](https://www.npmjs.com/package/live-server) to reload the page automatically when files change. Assuming your HTML file is named `mychart.html`, run `live-server mychart.html` to open your plot in your default browser. Every time `mychart.html` is updated, the page will refresh. This makes debugging and iterating much faster and easier.

### Debugging

If you don't see what you expect in your chart, the first thing to do is to check the console. If you see any error message in it, that might be related to why it's not working as expected.

If you added your own CSS/JavaScript, make sure that:

- they use valid selectors
- they are actually included in the HTML page
