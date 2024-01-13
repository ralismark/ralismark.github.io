// replace with KeyboardLayoutMap[1] once that stabilises
//
// [1]: https://developer.mozilla.org/en-US/docs/Web/API/KeyboardLayoutMap
export const keyNames = {
  "Digit1":       "1",
  "Digit2":       "2",
  "Digit3":       "3",
  "Digit4":       "4",
  "Digit5":       "5",
  "Digit6":       "6",
  "Digit7":       "7",
  "Digit8":       "8",
  "Digit9":       "9",
  "Digit0":       "0",
  "Minus":        "-",
  "Equal":        "=",

  "KeyQ":         "q",
  "KeyW":         "w",
  "KeyE":         "e",
  "KeyR":         "r",
  "KeyT":         "t",
  "KeyY":         "y",
  "KeyU":         "u",
  "KeyI":         "i",
  "KeyO":         "o",
  "KeyP":         "p",
  "BracketLeft":  "[",
  "BracketRight": "]",
  "Backslash":    "\\",

  "KeyA":         "a",
  "KeyS":         "s",
  "KeyD":         "d",
  "KeyF":         "f",
  "KeyG":         "g",
  "KeyH":         "h",
  "KeyJ":         "j",
  "KeyK":         "k",
  "KeyL":         "l",
  "Semicolon":    ";",
  "Quote":        "'",

  "KeyZ":         "z",
  "KeyX":         "x",
  "KeyC":         "c",
  "KeyV":         "v",
  "KeyB":         "b",
  "KeyN":         "n",
  "KeyM":         "m",
  "Comma":        ",",
  "Period":       ".",
  "Slash":        "/",
}

// values are [name, group, key nr, black?]
export const keymap = [
  // top row
  ["Digit1",       0, -1, true],
  ["KeyQ",         0, 0,  false],
  ["Digit2",       0, 0,  true],
  ["KeyW",         0, 1,  false],
  ["Digit3",       0, 1,  true],
  ["KeyE",         0, 2,  false],
  ["Digit4",       0, 2,  true],
  ["KeyR",         0, 3,  false],
  ["Digit5",       0, 3,  true],
  ["KeyT",         0, 4,  false],
  ["Digit6",       0, 4,  true],
  ["KeyY",         0, 5,  false],
  ["Digit7",       0, 5,  true],
  ["KeyU",         0, 6,  false],
  ["Digit8",       0, 6,  true],
  ["KeyI",         0, 7,  false],
  ["Digit9",       0, 7,  true],
  ["KeyO",         0, 8,  false],
  ["Digit0",       0, 8,  true],
  ["KeyP",         0, 9,  false],
  ["Minus",        0, 9,  true],
  ["BracketLeft",  0, 10, false],
  ["Equal",        0, 10, true],
  ["BracketRight", 0, 11, false],
  // bottom row
  ["KeyA",         1, -1, true],
  ["KeyZ",         1, 0,  false],
  ["KeyS",         1, 0,  true],
  ["KeyX",         1, 1,  false],
  ["KeyD",         1, 1,  true],
  ["KeyC",         1, 2,  false],
  ["KeyF",         1, 2,  true],
  ["KeyV",         1, 3,  false],
  ["KeyG",         1, 3,  true],
  ["KeyB",         1, 4,  false],
  ["KeyH",         1, 4,  true],
  ["KeyN",         1, 5,  false],
  ["KeyJ",         1, 5,  true],
  ["KeyM",         1, 6,  false],
  ["KeyK",         1, 6,  true],
  ["Comma",        1, 7,  false],
  ["KeyL",         1, 7,  true],
  ["Period",       1, 8,  false],
  ["Semicolon",    1, 8,  true],
  //["Slash",        1, 9,  false], // doesn't work with firefox
  //["Quote",        1, 9,  true], // doesn't work with firefox
]

export const salamander = {
  baseUrl: "https://tonejs.github.io/audio/salamander/",
  release: 1,

  urls: {
    "A0": "A0.mp3",
    "A1": "A1.mp3",
    "A2": "A2.mp3",
    "A3": "A3.mp3",
    "A4": "A4.mp3",
    "A5": "A5.mp3",
    "A6": "A6.mp3",
    "A7": "A7.mp3",
    "C1": "C1.mp3",
    "C2": "C2.mp3",
    "C3": "C3.mp3",
    "C4": "C4.mp3",
    "C5": "C5.mp3",
    "C6": "C6.mp3",
    "C7": "C7.mp3",
    "C8": "C8.mp3",
    "D#1": "Ds1.mp3",
    "D#2": "Ds2.mp3",
    "D#3": "Ds3.mp3",
    "D#4": "Ds4.mp3",
    "D#5": "Ds5.mp3",
    "D#6": "Ds6.mp3",
    "D#7": "Ds7.mp3",
    "F#1": "Fs1.mp3",
    "F#2": "Fs2.mp3",
    "F#3": "Fs3.mp3",
    "F#4": "Fs4.mp3",
    "F#5": "Fs5.mp3",
    "F#6": "Fs6.mp3",
    "F#7": "Fs7.mp3",
  }
}