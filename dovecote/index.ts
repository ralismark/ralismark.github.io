import { IttyRouter } from "itty-router"
import { mf2 } from "microformats-parser"
import { discoverPostType, PostType } from "./post-type-discovery"

type Datetime = string

// These are updated whenever the webmention source is fetched.
type WmPostData = {
	// The post type of the source
	type: PostType,

	// When the source page was published
	published_ts: Datetime | null, // TODO better type?

	// URL of the author
	author_url: string | null
	// Display name of the author
	author_name: string | null
	// Photo URL of the author
	author_photo: string | null

	// Content of source page, as text/html
	content_html: string | null
	// Content of source page, as text/plain
	content_text: string | null
}

// TODO database interactions
// TODO API for getting webmentions

type Webmention = WmPostData & {
	// WmPostData is only valid if status is good or good-refetch

	// Primary keys -----------------------------------------------------------
	// These are populated when the request is created and never changed
	// afterwards

	// The source page
	source: string,
	// The target page
	target: string,

	// Processing status ------------------------------------------------------
	
	// State of processing
	status:
		| "pending" // received, still processing
		| "bad" // invalid mention
		| "good" // valid mention
		| "good-refetch" // valid mention, was requested to be recrawled

	// When did the webmention last enter "pending" or "good-refetch"
	enqueued_ts: Datetime,
	// When did the webmention last enter "bad" or "good"
	processed_ts: Datetime,
}

// 3.2.1 Request Verification: https://www.w3.org/TR/webmention/#h-request-verification
async function getSourceTarget(formData: FormData, assets: Fetcher): Promise<{ source: URL, target: string, targetUrl: URL } | string> {
	const source = formData.get("source")
	const target = formData.get("target")
	if (typeof(source) !== "string" || typeof(target) !== "string")
		return "https://www.w3.org/TR/webmention/#sender-notifies-receiver-p-2"

	// The receiver MUST check that source and target are valid URLs [URL] and
	// are of schemes that are supported by the receiver. (Most commonly this
	// means checking that the source and target schemes are http or https).
	const sourceUrl = URL.parse(source)
	if (!sourceUrl || (sourceUrl.protocol !== "http:" && sourceUrl.protocol !== "https:"))
		return "https://www.w3.org/TR/webmention/#request-verification-p-1"
	const targetUrl = URL.parse(target)
	if (!targetUrl || (targetUrl.protocol !== "http:" && targetUrl.protocol !== "https:"))
		return "https://www.w3.org/TR/webmention/#request-verification-p-1"

	// The receiver MUST reject the request if the source URL is the same as the target URL.
	if (sourceUrl.href === targetUrl.href)
		return "https://www.w3.org/TR/webmention/#request-verification-p-2"

	// The receiver SHOULD check that target is a valid resource for which it
	// can accept Webmentions. This check SHOULD happen synchronously to reject
	// invalid Webmentions before more in-depth verification begins. What a
	// "valid resource" means is up to the receiver. For example, some receivers
	// may accept Webmentions for multiple domains, others may accept
	// Webmentions for only the same domain the endpoint is on.
	const canonical = await canonicalizeTarget(targetUrl, assets)
	if (typeof canonical === "string")
		return "https://www.w3.org/TR/webmention/#request-verification-p-3" +
			`\n\n${canonical}`

	return {
		source: sourceUrl,
		target: target,
		targetUrl: canonical,
	}
}

// 3.2.2 Webmention Verification: https://www.w3.org/TR/webmention/#h-webmention-verification
async function getWebmention(source: URL, target: string): Promise<{body: string} | string> {
	// If the receiver is going to use the Webmention in some way, (displaying
	// it as a comment on a post, incrementing a "like" counter, notifying the
	// author of a post), then it MUST perform an HTTP GET request on source,
	// following any HTTP redirects (and SHOULD limit the number of redirects it
	// follows) to confirm that it actually mentions the target. The receiver
	// SHOULD include an HTTP Accept header indicating its preference of content
	// types that are acceptable.
	let r: Response
	try {
		r = await fetch(source, {headers: {"Accept": "text/html,application/xhtml+xml"}})
	} catch(e) {
		return "https://www.w3.org/TR/webmention/#webmention-verification-p-2" +
			`\n\nCould not GET the target: ${e}`
	}

	if (!(200 <= r.status && r.status < 300))
		return `Received HTTP ${r.status} ${r.statusText} trying to GET ${source}.`

	// The receiver SHOULD use per-media-type rules to determine whether the
	// source document mentions the target URL.

	// https://httpwg.org/specs/rfc9110.html#field.content-type
	// If a Content-Type header field is not present, the recipient MAY either
	// assume a media type of "application/octet-stream"
	const contentType = r.headers.get("Content-Type") || "(not specified)"
	if (!["text/html", "application/xhtml"].some(x => contentType.startsWith(x)))
		return `Cannot handle Content-Type=${contentType}`

	// TODO
	// For example, in an [ HTML5] document, the receiver should look for <a
	// href="*">, <img href="*">, <video src="*"> and other similar links.

	// The source document MUST have an exact match of the target URL provided
	// in order for it to be considered a valid Webmention.
	const body = await r.text()
	if (!body.includes(target))
		return "https://www.w3.org/TR/webmention/#webmention-verification-p-3" +
			`\n\nDocument did not mention target.`

	return {
		body,
	}
}

const CANONICAL_DOMAIN = new Map([
	["kwellig.garden", "kwellig.garden"],
	["ralismark.xyz", "kwellig.garden"],
	["www.ralismark.xyz", "kwellig.garden"],
])

// Get the canonical URL target of a webmention
async function canonicalizeTarget(target: URL, assets: Fetcher): Promise<URL | string> {
	target = new URL(target) // copy

	// canonicalize host
	const host = CANONICAL_DOMAIN.get(target.host)
	if (!host) return "unacceptable domain"
	target.host = host

	// reset everything but path
	target.protocol = "https:"
	target.username = ""
	target.password = ""
	target.search = ""
	target.hash = ""

	// check rels on page
	const r = await assets.fetch(target)
	if (r.status !== 200)
		return `Target returns HTTP ${r.status} ${r.statusText}`
	const mf = mf2(await r.text(), { baseUrl: r.url })

	// check page says to send webmentions to dovecote
	const relWebmention = mf.rels["webmention"] ?? []
	if (!relWebmention.includes("https://kwellig.garden/_dovecote"))
		return `Target rel=webmention not handled by dovecote (found ${JSON.stringify(relWebmention)})`

	// use rel=canonical, otherwise final url after redirects
	const canonicalStr = (mf.rels["canonical"] ?? [r.url])[0]
	return new URL(canonicalStr)
}

function distill2(source: URL, body: string): WmPostData | null {
	const mf = mf2(body, { baseUrl: source.toString() })

	for (const doc of mf.items) {
		if (!doc.type?.includes("h-entry")) continue

		const hcard: MicroformatRoot | null = doc.properties.author ? doc.properties.author.filter(p => p.type?.includes("h-card"))[0] : null

		const type = discoverPostType(doc)
		const published_ts: Datetime | null = (doc.properties.published ?? [null])[0] as Datetime | null

		const author_url = (hcard?.properties.url ?? [null])[0] as string | null
		const author_name = (hcard?.properties.name ?? [null])[0] as string | null
		const author_photo = (hcard?.properties.photo ?? [null])[0] as string | null

		const content = (doc.properties.content ?? [null])[0] as Html

		return {
			type,
			published_ts,
			author_url,
			author_name,
			author_photo,
			content_html: content?.html ?? null,
			content_text: content?.value ?? null,
		}
	}

	return null
}

function simplyMf(root: MicroformatRoot) {
	const jf2: Record<string, any> = {}
	for (const [key, values] of Object.entries(root.properties)) {
		const simpleValues = values.map(v => v.properties ? simplyMf(v) : v)
		jf2[key] = simpleValues.length === 1 ? simpleValues[0] : simpleValues
	}
	jf2.type = root.type![0].replace("h-", "")
	if (root.id) jf2.id = root.id
	if (root.lang) jf2.lang = root.lang
	if (root.children) jf2.children = root.children
	return jf2
}

function distill(source: URL, body: string): any {
	const mf = mf2(body, { baseUrl: source.toString() })

	for (const doc of mf.items) {
		if (!doc.type?.includes("h-entry")) continue
		return simplyMf(doc)
	}

	return null
}

async function receive(request: Request, env: Env): Promise<Response> {
	let formData: FormData
	try {
		formData = await request.formData()
	} catch(e) {
		return new Response(null, {status: 415, headers: {"Accept-Post": "application/x-www-form-urlencoded"}})
	}

	// If the Webmention was not successful because of something the sender did,
	// it MUST return a 400 Bad Request status code and MAY include a
	// description of the error in the response body.

	const sourceTarget = await getSourceTarget(formData, env.ASSETS)
	if (typeof sourceTarget === "string") return new Response(sourceTarget, {status: 400})
	const { source, target, targetUrl } = sourceTarget

	const webmention = await getWebmention(source, target)
	if (typeof webmention === "string") return new Response(webmention, {status: 400})
	const { body } = webmention

	// microformats
	const mf = mf2(body, { baseUrl: source.toString() })
	// TODO do something with the parsed microformats

	const meta = distill2(source, body)
	if (!meta) return new Response("no h-entry", {status:422})

	return new Response(JSON.stringify({ meta, targetUrl }))
}

const router = IttyRouter({ base: "/_dovecote" })
router
	.post("/", async (request: Request, env: Env, ctx: ExecutionContext) => {
		// don't cancel request if client disconnects
		return new Promise((resolve, reject) => {
			ctx.waitUntil((async () => {
				try {
					resolve(receive(request, env))
				} catch(e) {
					reject(e)
				}
			})())
		})
	})
	.post("/parse", async (request: Request) => {
		const source = (await request.formData()).get("source")
		if (typeof source !== "string") return
		const r = await fetch(source)
		return new Response(JSON.stringify(mf2(await r.text(), { baseUrl: source })))
	})
	.all("*", () => new Response("dovecote: nothing here", {status:404}))

export default { ...router }
