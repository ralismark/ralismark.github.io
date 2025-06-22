import React from "./not-react"
import { screenshot } from "./screenshot"
import css from "./ui.css"

export function UI() {
	const canvas = <canvas/>

	const dialog = <dialog>
		{/*<details open>
			<summary>feedback</summary>
			<form method="dialog">
				<input style="grid-area: title" name="title" placeholder="Title" />
				<button style="grid-area: submit">Submit</button>
				<textarea style="grid-area: description" name="description" placeholder="Describe the issue here"></textarea>
			</form>
		</details>*/}
		{canvas}
	</dialog>

	return <>
		{dialog}
		<button
			id="feedback-button"
			type="button"
			onclick={async () => {
				const viewport = await screenshot()
				canvas.replaceWith(viewport)
				dialog.showModal()
			}}
		>
			feedback!
		</button>
		<style>{css}</style>
	</>
}

// create shadow root
window.addEventListener("load", () => {
	const host = document.createElement("kwellig-visual-feedback")
	const shadow = host.attachShadow({mode: "open"})
	shadow.appendChild(UI())

	document.body.appendChild(host)
	console.log("visual-feedback loaded")
})
