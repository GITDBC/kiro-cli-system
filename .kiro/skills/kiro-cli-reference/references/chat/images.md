> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Working with images

> Kiro can analyze and discuss images directly in your chat session. You can share images with Kiro by dragging and dropping them into your terminal window or by using the `read` tool with the Image mode.

Kiro can analyze and discuss images directly in your chat session. You can share images with Kiro by dragging and dropping them into your terminal window or by using the `read` tool with the Image mode.

## Drag and drop images

The simplest way to share images with Kiro is to drag and drop them directly into your terminal window. When you drag an image into the terminal:

1. The image path is automatically inserted into your prompt
2. You can then add text to provide context about what you want Kiro to do with the image
3. Kiro will process the image and respond based on its content

Example:

```
Kiro> /path/to/architecture-diagram.png Can you explain this architecture and generate sample code for implementing it?
```

## Ask Kiro to read an image

You can also ask Kiro to analyze an image by including its path:

```
Kiro> Can you analyze this screenshot at /path/to/screenshot.png?
```

Kiro reads the image from the path in your prompt.

## Pasting images from your clipboard

You can paste an image from your system clipboard with:

```
/paste
```

## Image use cases

Common use cases for sharing images with Kiro include:

* Analyzing screenshots of error messages for troubleshooting
* Converting architecture diagrams into code implementations
* Discussing UI/UX designs and generating corresponding HTML/CSS
* Understanding flowcharts and translating them into algorithms
* Reviewing code snippets shared as images
* Interpreting technical diagrams for documentation

## Supported formats and limitations

Supported image formats include JPEG/JPG, PNG, GIF, and WebP. Images must be under 10MB in size, and you can share up to 10 images in a single request.

In V2, Kiro automatically resizes images that exceed supported pixel dimensions while preserving their aspect ratio, and scales down oversized images in saved history when a session loads. If the model provider still rejects an image, Kiro retries automatically, then replaces the rejected images with a placeholder and shows a notice so you can continue the session.

In V3, Kiro resizes images to fit the selected model instead of failing the request.

For best results:

* Use high-resolution images with clear text
* Provide specific instructions about what you want Kiro to do with the image
* For complex diagrams, consider providing additional context
