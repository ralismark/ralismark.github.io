function notename(pitch) {
  return ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][pitch % 12]
}

const chords = {
  // dyads
  "100000000000": " + P8",
  "110000000000": " + m2",
  "101000000000": " + M2",
  "100100000000": " + m3",
  "100010000000": " + M3",
  "100001000000": " + P4",
  "100000100000": " + TT",
  "100000010000": " + P5",
  "100000001000": " + m6",
  "100000000100": " + M6",
  "100000000010": " + m7",
  "100000000001": " + M7",

  // triads
  "100010010000": "", // major
  "100100010000": "m", // minor
  "100100100000": "<sup>o</sup>", // dimished
  "100010001000": "<sup>+</sup>", // augmented
  "100001010000": "<sup>sus4</sup>", // suspended
  "101000010000": "<sup>sus2</sup>", // suspended

  // seventh chords
  "100010010001": "<sup>ma7</sup>", // major-major (major) seventh
  "100010010010": "<sup>7</sup>", // major-minor (dominant) seventh
  "100100010010": "m<sup>7</sup>", // minor-minor (minor) seventh
  "100100010010": "<sup>ø7</sup>", // half-diminished seventh
  "100100010100": "<sup>o7</sup>", // full-diminished seventh
}

// validate that we don't have any chords which are just rotations of each other
for (const bmap of Object.keys(chords)) {
  for (let i = 1; i < 12; ++i) {
    if (bmap[i] !== "1") continue
    const inv = bmap.substring(i) + bmap.substring(0, i)
    if (chords[inv] !== undefined) {
      console.warn("duplicate chord fingerprint", bmap, inv)
    }
  }
}

export default function identify(pitches) {
  if (pitches.size === 0) {
    return "-"
  } else if (pitches.size === 1) {
    const [key] = Array.from(pitches.values())
    return notename(key) + Math.floor(key / 12)
  }

  // chords

  let bass = Infinity
  for (const pitch of pitches) {
    bass = Math.min(bass, pitch)
  }

  for (let i = 0; i < 12; ++i) {
    const root = (bass + i) % 12 // always try bass as root first

    const mask = new Array(12).fill(0)
    for (const pitch of pitches) mask[(pitch + 12 - root) % 12] = 1
    if (!mask[0]) continue
    const bmask = mask.join("")

    const suffix = chords[bmask]
    console.log(bmask, suffix)
    if (suffix === undefined) continue

    // match!
    const name = notename(root) + suffix
    if (bass % 12 !== root) {
      // some inversion
      return `${name}/${notename(bass)}`
    }
    return name
  }

  return `?/${notename(bass)}`
}
