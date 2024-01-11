const map = (() => {
  const map = {}
  for (const [key, group, offset, black] of keymap) {
    map[key] = [group, offset, black]
  }
  return map
})()

const base = [21, 28]

// whether a distinct sharp exists and isn't just enharmonic to another scale
// degree
const hasSharp = [true, true, false, true, true, true, false]

function getPitch(keynr, sharp) {
  const octave = Math.floor(keynr / 7)
  const degree = keynr % 7

  return "CDEFGAB"[degree] + (sharp ? "#" : "") + octave
}

function relabel() {
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

//const synth = new Tone.PolySynth(Tone.Synth).toDestination();
const synth = new Tone.Sampler(salamander).toDestination()

const pressed = {}

const handle = async ev => {
  if (ev.target !== document.body) return

  const mapped = map[ev.code]
  if (mapped === undefined) return
  let [group, offset, sharp] = mapped

  let keynr = base[group] + offset
  if (sharp && !hasSharp[keynr % 7]) {
    return
    // keynr += 1
    // sharp = false
  }

  const pitch = getPitch(keynr, sharp)

  ev.preventDefault()

  const el = document.querySelector(`.key[data-pitch="${pitch}"]`)
  if (ev.type === "keydown") {
    if (pressed[pitch]) return
    pressed[pitch] = true
    if (el) el.setAttribute("aria-pressed", "true")
  } else {
    delete pressed[pitch]
    if (el) el.setAttribute("aria-pressed", "false")
  }

  await Tone.start()
  await Tone.loaded()

  if (ev.type === "keydown") {
    synth.triggerAttack(pitch, Tone.now())
  } else {
    synth.triggerRelease(pitch, Tone.now())
  }
}

document.addEventListener("keydown", handle)
document.addEventListener("keyup", handle)
