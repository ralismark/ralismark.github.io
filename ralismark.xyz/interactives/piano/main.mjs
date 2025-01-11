import {keyNames, keymap, salamander, scaleDegreeNames} from "./data.mjs"
import identify from "./chords.mjs"

const map = (() => {
  const map = {}
  for (const [key, group, offset, black] of keymap) {
    map[key] = [group, offset, black]
  }
  return map
})()

// base keys for top and bottom rows of the keyboard
window.base = [21, 28]

// whether a distinct sharp exists and isn't just enharmonic to another scale
// degree
const hasSharp = [true, true, false, true, true, true, false]

const keyNrToDegree = [0, 2, 4, 5, 7, 9, 11]

// redo all the key labelling, for when mappings get moved
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

// load sound playing
await import("https://cdnjs.cloudflare.com/ajax/libs/tone/14.7.58/Tone.js")
const synth = new Tone.Sampler(salamander).toDestination()
await Tone.loaded()
document.querySelector("#piano").setAttribute("data-ready", 1)

// set of pitch numbers that are being pressed
const pressed = new Set()

// element that shows the chord name
const chordname = document.querySelector("#chordname")

async function handle(pitchNr, isDown) {
  const octave = Math.floor(pitchNr / 12);
  const pitchName = scaleDegreeNames[pitchNr % 12] + octave;

  const el = document.querySelector(`.key[data-pitch="${pitchNr}"]`)
  if (isDown) {
    if (pressed.has(pitchNr)) return
    pressed.add(pitchNr)
    if (el) el.setAttribute("aria-pressed", "true")
  } else {
    if (!pressed.has(pitchNr)) return
    pressed.delete(pitchNr)
    if (el) el.setAttribute("aria-pressed", "false")
  }

  chordname.innerHTML = identify(pressed)

  await Tone.start()

  if (isDown) {
    synth.triggerAttack(pitchName)
  } else {
    synth.triggerRelease(pitchName)
  }
}

async function handleKeyEvent(ev) {
  const mapped = map[ev.code]
  if (mapped === undefined) return // not recognised key
  let [group, offset, sharp] = mapped

  let keynr = base[group] + offset
  if (sharp && !hasSharp[keynr % 7]) return // black key event where none exists

  const octave = Math.floor(keynr / 7)
  await handle(octave * 12 + keyNrToDegree[keynr % 7] + sharp, ev.type === "keydown")
}

document.addEventListener("keydown", handleKeyEvent)
document.addEventListener("keyup", handleKeyEvent)

for (const keyEl of document.querySelectorAll("#piano .key")) {
  const pitchNr = +keyEl.dataset.pitch

  keyEl.addEventListener("pointerover", ev => {
    if (ev.buttons === 0) return // hover doesn't count
    if (pressed.has(pitchNr)) return // don't double-tap
    handle(pitchNr, true)
    ev.target.releasePointerCapture(ev.pointerId)
    ev.preventDefault()
  })
  keyEl.addEventListener("pointerout", ev => {
    handle(pitchNr, false)
  })
}
