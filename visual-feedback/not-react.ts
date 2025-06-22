type Child = HTMLElement | string | Child[]

declare global {
	export namespace JSX {
		type IntrinsicElements = {
			[tag in keyof HTMLElementTagNameMap]: any;
		}
	}
}

function appendChildren(element: Node, child: Child) {
	if (child instanceof Array) {
		for (const c of child) appendChildren(element, c)
	} else if (typeof child === "string") {
		element.appendChild(document.createTextNode(child))
	} else {
		element.appendChild(child)
	}
}

export function createElement<P, E extends HTMLElement>(
	type: (props: P) => E,
	props: P,
): E;

export function createElement<P, E extends HTMLElement, C extends Child[]>(
	type: (props: P & { children: C }) => E,
	props: P,
	...children: C
): E;

export function createElement<K extends keyof HTMLElementTagNameMap>(
	type: K,
	props: any,
	...children: Child[]
): HTMLElementTagNameMap[K];

export function createElement<K extends keyof HTMLElementTagNameMap>(
	type: K | ((props: any) => HTMLElement),
	props: any,
	...children: Child[]
): HTMLElement {
	if (typeof type === "function") {
		if (props === null) props = {}
		props.children = children
		return type(props)
	}

	const element = document.createElement(type)
	if (props !== null) {
		for (const [name, value] of Object.entries(props)) {
			// skip false/null/undefined attributes
			if (value === false || value === null || value === undefined) continue;

			// add event listeners
			if (name.startsWith("on")) {
				element.addEventListener(name.substring(2).toLowerCase(), value as any)
				continue
			}

			if (value === true) {
				// true = attribute present but empty
				element.setAttribute(name, "")
				continue
			}

			element.setAttribute(name, value as any)
		}
	}

	appendChildren(element, children)

	return element
}

export function Fragment({ children }: { children: Child[] }) {
	const frag = document.createDocumentFragment()
	appendChildren(frag, children)
	return frag
}

const React = {
	createElement,
	Fragment
}
export default React
