import {keyNames, keymap, salamander} from "./data.mjs"
import identify from "./chords.mjs"

const map = (() => {
  const map = {}
  for (const [key, group, offset, black] of keymap) {
    map[key] = [group, offset, black]
  }
  return map
})()

window.base = [21, 28]

// whether a distinct sharp exists and isn't just enharmonic to another scale
// degree
const hasSharp = [true, true, false, true, true, true, false]

window.relabel = function() {
  for (const label of document.querySelectorAll("[data-mapped]")) {
    label.remove()
  }

  for (const [key, group, offset, black] of keymap) {
    const keynr = base[group] + offset

    const el = document.querySelector(`#piano .key[data-nr="${keynr}"][data-${black ? "black" : "white"}]`)
    if (!el) continue

    const label = document.createElement("span")
    label.innerText = keyNames[key]
    label.setAttribute("data-mapped", key)
    label.setAttribute("data-group", group)

    el.appendChild(label)
  }
}

relabel()

const pressed = new Set()

const focusarea = document.querySelector("main")
const chordname = document.querySelector("#chordname")

await import("https://cdnjs.cloudflare.com/ajax/libs/tone/14.7.58/Tone.js")

const synth = new Tone.Sampler(salamander).toDestination()
await Tone.loaded()

document.querySelector("#piano").setAttribute("data-ready", 1)

const handle = async ev => {
  if (!focusarea.contains(ev.target)) return

  const mapped = map[ev.code]
  if (mapped === undefined) return
  let [group, offset, sharp] = mapped

  let keynr = base[group] + offset
  if (sharp && !hasSharp[keynr % 7]) {
    return
    // keynr += 1
    // sharp = false
  }

  const octave = Math.floor(keynr / 7)
  const degree = keynr % 7

  const pitchName = "CDEFGAB"[degree] + (sharp ? "#" : "") + octave
  const pitchNr = octave * 12 + [0, 2, 4, 5, 7, 9, 11][degree] + (sharp ? 1 : 0)

  ev.preventDefault()

  const el = document.querySelector(`.key[data-pitch="${pitchName}"]`)
  if (ev.type === "keydown") {
    if (pressed.has(pitchNr)) return
    pressed.add(pitchNr)
    if (el) el.setAttribute("aria-pressed", "true")
  } else {
    pressed.delete(pitchNr)
    if (el) el.setAttribute("aria-pressed", "false")
  }

  chordname.innerHTML = identify(pressed)

  await Tone.start()

  if (ev.type === "keydown") {
    synth.triggerAttack(pitchName)
  } else {
    synth.triggerRelease(pitchName)
  }
}

document.addEventListener("keydown", handle)
document.addEventListener("keyup", handle)
