import React from "./not-react"
import { clarify } from "./obscure"
import { screenshot } from "./screenshot"
import css from "./ui.css"

// I don't want the url to be visible in the code
const WEBHOOK = clarify({
	"key": "jIgMBuuYlmB2tat1numz2+7dCfsivYrdSISa5CB8CJo=",
	"iv": "1XCPUG+EzREIMSfe",
	"ciphertext": "8o1iQKh2vDGsy17R8FbrbfUtablzrg7ZL/kBSH9M25MNgOyQNFFdgKBlniws8VmNofnV4zZ+I9AgDuQ5AIxQlwjCdrpWulJTdT48xEfr3H/MgV1oMQO9/TRRWsTLLVrOtcf7onwmUhO6jQ9CxHGSczJX7/tAilsUnW9PlV13Cl2+IfD3cZpF05o="
})

async function submit_issue({ description, canvas }: { description: string, canvas: HTMLCanvasElement }) {
	const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve))

	const formdata = new FormData()
	formdata.append("payload_json", JSON.stringify({
		content: `URL: ${location}
User Agent: \`${navigator.userAgent}\`
>>> ${description}`,
		attachments: [
			{
				id: 0,
				filename: "screenshot.png",
			}
		]
	}))
	formdata.append("files[0]", blob!)

	await fetch(await WEBHOOK, {
		method: "POST",
		body: formdata,
	})
}

function Form({ getcanvas, getdialog }: {
	getcanvas: () => HTMLCanvasElement,
	getdialog: () => HTMLDialogElement,
}) {
	const description = <textarea
		style="grid-area: description"
		name="description"
		placeholder="Describe the issue here"
		minlength={10}
		required
	/>

	return <form
		method="dialog"
		onsubmit={() => {
			submit_issue({
				description: description.value,
				canvas: getcanvas(),
			})
		}}
	>
		{description}
		<button
			style="grid-area: cancel"
			type="button"
			onclick={(e: PointerEvent) => {
				getdialog().close()
				e.preventDefault()
			}}
		>Cancel</button>
		<button style="grid-area: submit">Submit</button>
	</form>
}

// use pointer events to draw on canvas
function make_drawable(canvas: HTMLCanvasElement) {
	const ctx = canvas.getContext("2d")!

	ctx.lineWidth = 3
	ctx.lineCap = "round"
	ctx.strokeStyle = "purple"

	const lastPoint = new Map<number, [number, number]>()

	function strokeTo(e: PointerEvent) {
		const last = lastPoint.get(e.pointerId)
		if (!last) return

		ctx.beginPath()
		ctx.moveTo(last[0], last[1])
		ctx.lineTo(e.offsetX, e.offsetY)
		ctx.stroke()
		lastPoint.set(e.pointerId, [e.offsetX, e.offsetY])
	}

	canvas.addEventListener("pointerdown", e => {
		lastPoint.set(e.pointerId, [e.offsetX, e.offsetY])
		e.preventDefault()
	})

	canvas.addEventListener("pointermove", e => {
		strokeTo(e)
	})

	canvas.addEventListener("pointerup", e => {
		strokeTo(e)
		lastPoint.delete(e.pointerId)
	})

	canvas.addEventListener("pointercancel", e => {
		lastPoint.delete(e.pointerId)
	})

	canvas.addEventListener("pointerleave", e => {
		lastPoint.delete(e.pointerId)
	})
}

export function UI() {
	let canvas = <canvas />

	const dialog = <dialog id="visual-feedback">
		<details open>
			<summary>Feedback</summary>
			<Form
				getcanvas={() => canvas}
				getdialog={() => dialog}
			/>
		</details>
		{canvas}
	</dialog>

	return <>
		{dialog}
		<button
			id="feedback-button"
			type="button"
			onclick={async () => {
				let viewport: HTMLCanvasElement
				try {
					viewport = await screenshot()
				} catch(e) {
					fetch(await WEBHOOK, {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({
							content: `**Failed to take screenshot!**
URL: ${location}
User Agent: \`${navigator.userAgent}\`
\`\`\`
${e}
\`\`\``,
						})
					})
					alert("We couldn't take a screenshot :(\n\n" + e)
					return
				}
				make_drawable(viewport)

				canvas.replaceWith(viewport)
				canvas = viewport
				dialog.showModal()
			}}
		>
			feedback!
		</button>
		<style>{css}</style>
	</>
}

const host = document.createElement("kwellig-visual-feedback")
const shadow = host.attachShadow({mode: "open"})
shadow.appendChild(UI())
document.currentScript!.insertAdjacentElement("afterend", host)
