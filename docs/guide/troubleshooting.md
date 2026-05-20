---
title: Troubleshooting
---

Since `ninejs` does many things via JavaScript (e.g., in your browser when you open your HTML file), you may easily encounter "silent" errors.

In practice, you will run your Python and everything will seem fine, but that does not mean what you'll see in the output is what you expected. There may be multiple reasons for this. Here I'll explain common things that can happen, and how to debug them.

## Developer tools

Your browser has a thing called developer tools. It allows you to view many things, but here we're mostly interested in its "console" section.

The console displays all the messages, including error messages, that the web page encountered at some point. Many of them are not necessarily interesting and are standard messages, but some of them might come from `ninejs` doing something wrong.

How to open the developer tools is browser-specific, but there's likely a shortcut to make it convenient. For instance, on macOS + Firefox I use ++option+cmd+i++.

Once open, you'll also be able to find messages from `ninejs`, such as the number of "points" (scatter plot) or "lines" (line plot) that have been found. This can give you clues as to what's going wrong.

## Debug `ninejs`

### Workflow

In order to have a comfortable workflow, it's recommended to have [`live-server`](https://www.npmjs.com/package/live-server) installed on your machine for automatic reload on file changes. Assuming you name your HTML file `mychart.html`, you'll just have to run `live-server mychart.html` and it'll open your plot in your default browser. Every time `mychart.html` is updated, it'll refresh the page. This makes debugging and iterating much faster and easier.

### Debugging

If you don't see what you expect in your chart, the first thing to do is to check the console. If you see any error message in it, that might be related to why it's not working as expected.

If you added your own CSS/JavaScript, make sure that:

- they use valid selectors
- they are actually included in the HTML page
