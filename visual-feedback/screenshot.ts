// The limitations we need to work around are listed in:
// https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image

const isInstanceOfElement = <
T extends typeof Element | typeof HTMLElement | typeof SVGImageElement,
>(
	node: Element | HTMLElement | SVGImageElement,
	instance: T,
): node is T["prototype"] => {
	if (node instanceof instance) return true

	const nodePrototype = Object.getPrototypeOf(node)

	if (nodePrototype === null) return false

	return (
		nodePrototype.constructor.name === instance.name ||
			isInstanceOfElement(nodePrototype, instance)
	)
}

async function fetchAsDataUrl(url: string): Promise<string> {
	const r = await fetch(url, {
	})
	const blob = await r.blob()
	const dataUrl = await new Promise<string>((resolve, reject) => {
		const reader = new FileReader()
		reader.onload = () => resolve(reader.result as string)
		reader.onerror = reject
		reader.readAsDataURL(blob)
	})
	return dataUrl
}

function imageToDataURL(image: HTMLImageElement | HTMLCanvasElement) {
	const canvas = document.createElement("canvas")
	canvas.width = image.width
	canvas.height = image.height
	canvas.getContext("2d")!.drawImage(image, 0, 0, canvas.width, canvas.height)
	try {
		return canvas.toDataURL()
	} catch(e) {
		if (e instanceof DOMException && e.name === "SecurityError") {
			// img taints the canvas (e.g. cross-origin image), so we can't get it
			console.warn("Can't preserve tainted image", image)
			return null
		} else {
			throw e
		}
	}
}

function placeholderSvg(width: number, height: number, text: string = "") {
	const svg = `
		<?xml version="1.0" encoding="UTF-8"?>
		<svg
			xmlns:xlink="http://www.w3.org/1999/xlink"
			xmlns="http://www.w3.org/2000/svg"
			width="${width}"
			height="${height}"
		>
			<defs>
				<pattern
					id="fill"
					width="10" height="10"
					patternUnits="userSpaceOnUse"
					patternTransform="rotate(45 50 50)"
				>
					<line stroke="rebeccapurple" stroke-width="5" x1="2.5" y1="0" x2="2.5" y2="10"/>
					<line stroke="#444" stroke-width="5" x1="7.5" y1="0" x2="7.5" y2="10"/>
				</pattern>
			</defs>

			<rect
				x="0"
				y="0"
				width="${width}"
				height="${height}"
				fill="url(#fill)"
			/>

			<text x="0" y="${height - 16}" fill="white">Can't capture</text>
			<text x="0" y="${height}" fill="white">${text}</text>
		</svg>
	`.trim()
	return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
}

async function cloneNodeInner(node: Node): Promise<Node | null> {
	try {
		if (node instanceof Text) {
			return node.cloneNode(true)
		} else if (!(node instanceof Element)) {
			return null
		}

		if (
			node instanceof Comment // invalid in svgs
				|| isInstanceOfElement(node, HTMLScriptElement) // doesn't do anything
				|| node.tagName === "NOSCRIPT" // javascript is definitely enabled
		) {
			return null
		} else if (
			(isInstanceOfElement(node, HTMLLinkElement) && node.rel == "stylesheet")
				|| isInstanceOfElement(node, HTMLStyleElement)
		) {
			// we import all css using document.styleSheets
			return null
		} else if (isInstanceOfElement(node, HTMLCanvasElement)) {
			// canvas doesn't show up when it's in the SVG, but instead uses its
			// (fallback) contents
			const clone = node.cloneNode(false)

			let dataUrl
			try {
				dataUrl = node.toDataURL()
			} catch(e) {
				console.warn("Can't preserve tainted canvas", node)
				dataUrl = placeholderSvg(node.offsetWidth, node.offsetHeight, "canvas")
			}

			const img = new Image(node.offsetWidth, node.offsetHeight)
			img.src = dataUrl
			clone.appendChild(img)
			return clone

		} else if (isInstanceOfElement(node, HTMLImageElement)) {
			const clone = node.cloneNode(false) as typeof node
			clone.src = (
				imageToDataURL(node) ||
					placeholderSvg(node.width, node.height, node.src.substring(0, 50))
			)
			clone.width = node.width
			clone.height = node.height
			return clone

		} else if (isInstanceOfElement(node, HTMLIFrameElement)) {
			// iframes are cross-origin and so don't clone well
			// TODO doesn't work on chromium -- the element is omitted entirely
			const clone = node.cloneNode(false) as typeof node
			clone.style.background = `url("${placeholderSvg(node.offsetWidth, node.offsetHeight, "iframe:" + node.src)}")`
			return clone
		} else if (isInstanceOfElement(node, HTMLDetailsElement) && !node.open) {
			// for some reason, firefox doesn't handle closed details correctly
			const clone = node.cloneNode(false)
			for (const child of node.childNodes) {
				// omit all other children
				if ((child as HTMLElement).tagName == "SUMMARY") {
					const childClone = await cloneNode(child)
					if (!childClone) continue
					clone.appendChild(childClone)
				}
			}
			return clone
		} else {
			// default clone
			const clone = node.cloneNode(false) as typeof node
			for (const child of node.childNodes) {
				const childClone = await cloneNode(child)
				if (!childClone) continue
				clone.appendChild(childClone)
			}

			// copy over values
			if (isInstanceOfElement(node, HTMLInputElement)) {
				clone.setAttribute("value", node.value)
			} else if (isInstanceOfElement(node, HTMLOptionElement)) {
				if (node.selected) clone.setAttribute("selected", "")
			} else if (isInstanceOfElement(node, HTMLTextAreaElement)) {
				clone.textContent = node.value
			}

			return clone
		}
	} catch(e) {
		console.error("Failed to clone", node, e)
		return null
	}
}

async function cloneNode(node: Node): Promise<Node | null> {
	const clone = await cloneNodeInner(node)
	if (clone === null) return null

	return clone
}

const RE_CSS_URL = /url\((['"]?)([^'"]+?)\1\)/g

async function preserveStylesheet() {
	const fragment = document.createDocumentFragment()

	for (const stylesheet of document.styleSheets) {
		const style = document.createElement("style")
		for (const rule of stylesheet.cssRules) {
			let text = rule.cssText

			// TODO handle @import and font defns

			if (!(rule instanceof CSSFontFaceRule)) {
				// convert url(...) to data url
				const promises: Promise<string>[] = []
				text.replace(RE_CSS_URL, (_, __, url) => {
					promises.push(fetchAsDataUrl(url).catch(e => {
						console.warn("Failed to preserve", url, e)
						return ""
					}))
					return ""
				})
				const results = await Promise.all(promises)
				text = text.replace(RE_CSS_URL, () => `url("${results.shift()}")`)
			}

			style.appendChild(document.createTextNode(text + "\n"))
		}
		fragment.appendChild(style)
	}

	return fragment
}

export async function screenshot(): Promise<HTMLCanvasElement> {
	const width = document.documentElement.clientWidth
	const height = document.documentElement.clientHeight

	// clone the node

	const clone = (await cloneNode(document.documentElement))!
	clone.appendChild(await preserveStylesheet())

	// offset the html element
	const offsetStyle = document.createElement("style")
	offsetStyle.textContent = `
		html {
			position: relative;
			top: -${window.scrollY}px;
			left: -${window.scrollX}px;
		}
	`
	clone.appendChild(offsetStyle)

	// create svg of document

	const xmlns = "http://www.w3.org/2000/svg"

	const foreignObject = document.createElementNS(xmlns, "foreignObject")
	foreignObject.setAttribute("width", "100%")
	foreignObject.setAttribute("height", "100%")
	foreignObject.setAttribute("x", "0")
	foreignObject.setAttribute("y", "0")
	foreignObject.setAttribute("externalResourcesRequired", "true")

	foreignObject.appendChild(clone)

	const svg = document.createElementNS(xmlns, "svg")
	svg.setAttribute("width", `${width}`)
	svg.setAttribute("height", `${height}`)
	svg.setAttribute("viewBox", `0 0 ${width} ${height}`)

	svg.appendChild(foreignObject)

	// convert svg to HTMLImageElement

	const svgString = new XMLSerializer().serializeToString(svg)
	console.log(svgString)
	const svgUrl = `data:image/svg+xml,${encodeURIComponent(svgString)}`

	const img = await new Promise<HTMLImageElement>((resolve, reject) => {
		const img = new Image()
		img.onload = () => {
			img.decode().then(() => {
				requestAnimationFrame(() => resolve(img))
			})
		}
		img.onerror = e => {
			console.error("Failed to render to image", e)
			reject(e)
		}
		img.decoding = "async"
		img.src = svgUrl
	})

	// render image to canvas

	const canvas = document.createElement("canvas")
	canvas.width = width
	canvas.height = height

	const context = canvas.getContext("2d")!
	context.imageSmoothingEnabled = false

	// Drawing to canvas at 1:1 scale is kinda blurry, we'd like to use larger
	// width/height for the <canvas> and draw to the full side, but the svg uses
	// the width/height of our drawImage call for media queries, so we must use
	// exactly `width`/`height` (and cannot draw upscaled).
	context.drawImage(img, 0, 0, width, height)

	return canvas
}
