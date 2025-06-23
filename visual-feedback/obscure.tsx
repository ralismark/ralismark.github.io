// Obscure strings in plain text, so random scrapers don't get them
//
// This is not intended as a *security* feature!

function bufToBase64(buffer: ArrayBuffer) {
	return btoa(String.fromCharCode(...new Uint8Array(buffer)))
}

function base64ToBuf(b64: string) {
	const str = atob(b64)
	return Uint8Array.from(str, c => c.charCodeAt(0)).buffer
}

export type Obscured = {
	key: string
	iv: string
	ciphertext: string
}

// Encrypts a plaintext string with a randomly generated AES-GCM key
export async function obscure(plaintext: string) {
	// 1. Generate a 256-bit AES-GCM key
	const key = await crypto.subtle.generateKey(
		{ name: "AES-GCM", length: 256 },
		true, // extractable so we can export it
		["encrypt", "decrypt"]
	)

	// 2. Export key to raw format, then Base64-encode it
	const rawKey = await crypto.subtle.exportKey("raw", key)
	const b64Key = bufToBase64(rawKey)

	// 3. Prepare plaintext data and random IV
	const encoder = new TextEncoder()
	const data = encoder.encode(plaintext)
	const iv = crypto.getRandomValues(new Uint8Array(12)) // Recommended 12 bytes for AES-GCM

	// 4. Encrypt
	const encrypted = await crypto.subtle.encrypt(
		{ name: "AES-GCM", iv },
		key,
		data
	)

	// 5. Return JSON-ready object
	return {
		key: b64Key,
		iv: bufToBase64(iv.buffer),
		ciphertext: bufToBase64(encrypted)
	}
}

// Decrypts the object produced by obscure to recover original text
export async function clarify(j: Obscured) {
	// 1. Base64-decode and import the key
	const rawKey = base64ToBuf(j.key)
	const key = await crypto.subtle.importKey(
		"raw",
		rawKey,
		{ name: "AES-GCM" },
		false,
		["decrypt"]
	)

	// 2. Decode IV and ciphertext
	const iv = new Uint8Array(base64ToBuf(j.iv))
	const data = base64ToBuf(j.ciphertext)

	// 3. Decrypt
	const decrypted = await crypto.subtle.decrypt(
		{ name: "AES-GCM", iv },
		key,
		data
	)

	// 4. Decode text and return
	const decoder = new TextDecoder()
	return decoder.decode(decrypted)
}
