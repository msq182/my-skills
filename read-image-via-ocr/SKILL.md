---
name: read-image-via-ocr
description: Use when the model cannot see images and the user asks to 读图、看图、识别图片、看截图、读取图片里的文字、OCR、提取扫描件/PDF 内容、数图片里的人数、识别二维码/条形码、判断图片内容。This skill teaches a vision-less model how to "read" images by calling the local macos-vision-mcp tools (Apple Vision OCR) and working from the extracted text/structure instead of the pixels.
---

# Read Images Without Vision (via macos-vision-mcp)

This model has **no vision capability**: it cannot actually see image pixels, no matter how the prompt is phrased. To "read" an image, **always extract data first through the macos-vision-mcp tools**, then reason over the returned text/structure. Never claim you can see the image directly.

## Available tools (provided by the `macos-vision-mcp` MCP server)

All run **locally via Apple Vision Framework** — offline, no API keys, files never leave the Mac.

| Tool | Purpose |
| ---- | ------- |
| `ocr_image` | Extract text from JPG / PNG / HEIC / TIFF / PDF. Supports `start_page` / `max_pages` for long PDFs. |
| `analyze_document` | Full pipeline: reading-order paragraphs + raw text blocks (bbox/confidence) + faces + barcodes + rectangles in one call. Best for reconstructing documents into Markdown/HTML/JSON. |
| `classify_image` | Classify image content into 1000+ categories with confidence scores. |
| `detect_faces` | Count and locate human faces. |
| `detect_barcodes` | Read QR, EAN, UPC, Code128, PDF417, Aztec, and other 1D/2D codes. |
| `detect_document` | Find the four corners of a document (paper, receipt, ID) — use as a crop/deskew hint before OCR. |

## Intent → tool routing

| User intent | Tool to call |
| ----------- | ------------ |
| "图片里的文字是什么 / 读取截图内容 / OCR" | `ocr_image` |
| "把这张图/PDF 转成 Markdown / 结构化整理" | `analyze_document` |
| "这张图/这是什么 / 内容分类" | `classify_image` |
| "图里有几个人" | `detect_faces` |
| "二维码/条形码是什么" | `detect_barcodes` |
| "找出文档的边界/校正拍摄" | `detect_document` |
| 通用："看完这张图并总结/回答" | `analyze_document` (or `ocr_image` + `classify_image`) |

## Workflow

1. **Resolve the file path.** If the user gives a relative path, resolve it against the current working directory. Convert to an absolute path (or `~`-prefixed) before calling the tool — the MCP server needs a real filesystem path.
2. **Pick the right tool** from the routing table above.
3. **Call the tool** with the resolved path.
4. **Reason over the result.** Answer the user's actual question from the extracted text/classification. For documents, preserve reading order (use the returned paragraphs) when reconstructing.
5. **If the extraction looks empty or wrong**, mention the OCR result was sparse and offer `analyze_document` for a fuller structured read.

## Notes

- Supported inputs: images (JPG, PNG, HEIC, TIFF) and multi-page PDF.
- Long PDFs: pass `start_page` / `max_pages` to OCR only the pages you need.
- Extracting text locally cuts tokens ~97% vs sending raw pixels — always prefer extraction over attempting to describe pixels.
- The user may refer to images by description ("我刚截的图") without a path — ask for the file path if you cannot locate it.
