import { IttyRouter } from "itty-router"
import { mf2 } from "microformats-parser"
import { discoverPostType, PostType } from "./post-type-discovery"
import { JSDOM } from "jsdom"
import DOMPurify from "dompurify"


// TODO database interactions
// TODO API for getting webmentions

type Datetime = number // unix time in seconds

function now(): Datetime {
	return Math.floor(Date.now() / 1000)
}

// Info about the webmention source.
type WebmentionDistilled = {
	// This is all `undefined` if the page does not have valid microformats

	// The post type of the source
	type?: PostType

	// When the source page was published, according to the page itself
	published_ts?: Datetime

	// Display name of the author
	author_name?: string
	// Photo URL of the author
	author_photo?: string

	// Content of source page, as text/html
	content_html?: string
}

// 3.2.1 Request Verification: https://www.w3.org/TR/webmention/#h-request-verification
async function getSourceTarget(formData: FormData): Promise<{ source: URL, target: string, targetUrl: URL } | string> {
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

	return {
		source: sourceUrl,
		target: target,
		targetUrl: targetUrl,
	}
}

// 3.2.2 Webmention Verification: https://www.w3.org/TR/webmention/#h-webmention-verification
async function getWebmention(source: URL, target: string): Promise<{body: string, resolvedSource: string} | string> {
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
			`\n\nGET source: ${e}`
	}

	if (!(200 <= r.status && r.status < 300))
		return "https://www.w3.org/TR/webmention/#webmention-verification-p-2" +
			`\n\nGET source: got HTTP status ${r.status} ${r.statusText}`

	// The receiver SHOULD use per-media-type rules to determine whether the
	// source document mentions the target URL.

	// https://httpwg.org/specs/rfc9110.html#field.content-type
	// If a Content-Type header field is not present, the recipient MAY either
	// assume a media type of "application/octet-stream"
	const contentType = r.headers.get("Content-Type") || "(not specified)"
	if (!["text/html", "application/xhtml"].some(x => contentType.startsWith(x)))
		return "https://www.w3.org/TR/webmention/#webmention-verification-p-3" +
			`\n\nGET source: Cannot handle Content-Type=${contentType}`

	// TODO
	// For example, in an [ HTML5] document, the receiver should look for <a
	// href="*">, <img href="*">, <video src="*"> and other similar links.

	const body = await r.text()
	// TODO
	// https://www.w3.org/TR/webmention/#limits-on-get-requests-p-4
	// Receivers SHOULD place limits on the amount of data and time they spend
	// fetching unverified source URLs. For example, if a source URL doesn't
	// respond within 5 seconds, it can treat that as a failure. Similarly, the
	// receiver can fetch only the first 1mb of the page, since any reasonable
	// HTML or JSON page will be smaller than that.

	// The source document MUST have an exact match of the target URL provided
	// in order for it to be considered a valid Webmention.
	if (!body.includes(target))
		return "https://www.w3.org/TR/webmention/#webmention-verification-p-3" +
			`\n\nSource did not mention target`

	return {
		body,
		resolvedSource: r.url,
	}
}

const CANONICAL_DOMAIN = new Map([
	["waratah.kwellig.garden", "kwellig.garden"], // "localhost" for testing!
	["kwellig.garden", "kwellig.garden"],
	["ralismark.xyz", "kwellig.garden"],
	["www.ralismark.xyz", "kwellig.garden"],
])

// Get the canonical URL target of a webmention
async function resolveTarget(target: URL, assets: Fetcher): Promise<URL | string> {
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

	/*
	const mf = mf2(await r.text(), { baseUrl: r.url })

	// check page says to send webmentions to dovecote
	const relWebmention = mf.rels["webmention"] ?? []
	if (!relWebmention.includes("https://kwellig.garden/_dovecote"))
		return `Target rel=webmention not handled by dovecote (found ${JSON.stringify(relWebmention)})`

	// use rel=canonical, otherwise final url after redirects
	const canonicalStr = (mf.rels["canonical"] ?? [r.url])[0]
	return new URL(canonicalStr)
	*/

	return new URL(r.url)
}

function distill(mf: ParsedDocument): WebmentionDistilled | null {
	for (const doc of mf.items) {
		if (!doc.type?.includes("h-entry")) continue

		function getProperty(root: MicroformatRoot, key: string): MicroformatProperty[] {
			const props = root.properties[key]
			if (props === undefined) return []
			return props
		}

		function propertyIsRoot(property: MicroformatProperty): property is MicroformatRoot {
			return typeof property === "object" && "type" in property
		}

		function propertyIsImage(property: MicroformatProperty): property is Image {
			return typeof property === "object" && "alt" in property
		}

		function propertyIsHtml(property: MicroformatProperty): property is Html {
			return typeof property === "object" && "html" in property
		}

		const type = discoverPostType(doc)
		const published_ts: Datetime | undefined = (() => {
			const p = getProperty(doc, "published")[0]
			const parsed = Math.floor(Date.parse(p as string) / 1000)
			return isNaN(parsed) ? undefined : parsed
		})()

		let author_name: string | undefined = undefined
		let author_photo: string | undefined = undefined
		let content_html: string | undefined = undefined

		const hcard = getProperty(doc, "author").filter(propertyIsRoot).filter(p => p.type?.includes("h-card"))[0]
		if (hcard) {
			author_name = getProperty(hcard, "name").filter(p => typeof p === "string")[0]

			const photo = getProperty(hcard, "photo")[0]
			author_photo =
				typeof photo === "string" ? photo
				: propertyIsImage(photo) ? photo.value
				: undefined
		}

		const content = getProperty(doc, "content").filter(propertyIsHtml)[0]
		if (content?.html) {
			content_html = content.html
		} else if (content?.value) {
			const entities: Record<string, string> = {
				"&": "&amp;",
				"<": "&lt;",
				">": "&gt;",
			}
			content_html = content.value.replaceAll(/[&<>]/g, s => entities[s])
		}

		return {
			type,
			published_ts,
			author_name,
			author_photo,
			content_html,
		}
	}

	return null
}

async function receive(formData: FormData, env: Env): Promise<Response> {
	// If the Webmention was not successful because of something the sender did,
	// it MUST return a 400 Bad Request status code and MAY include a
	// description of the error in the response body.

	// 3.2.1 Request Verification: https://www.w3.org/TR/webmention/#h-request-verification
	const sourceTarget = await getSourceTarget(formData)
	if (typeof sourceTarget === "string") return new Response(sourceTarget, {status: 400})
	const { source, target, targetUrl } = sourceTarget

	// The receiver SHOULD check that target is a valid resource for which it
	// can accept Webmentions. This check SHOULD happen synchronously to reject
	// invalid Webmentions before more in-depth verification begins. What a
	// "valid resource" means is up to the receiver. For example, some receivers
	// may accept Webmentions for multiple domains, others may accept
	// Webmentions for only the same domain the endpoint is on.
	const resolvedTarget = await resolveTarget(targetUrl, env.ASSETS)
	if (typeof resolvedTarget === "string") {
		// TODO check if the source/target corresponds to an existing
		// webmention, for validation
		return new Response(resolvedTarget, {status: 400})
	}

	console.log({
		source: source.toString(),
		target: target,
		resolvedTarget: resolvedTarget.toString(),
	})

	// 3.2.2 Webmention Verification: https://www.w3.org/TR/webmention/#h-webmention-verification
	const webmention = await getWebmention(source, target)
	if (typeof webmention === "string") {
		// erase if exists
		await env.dovecote.prepare(`
			UPDATE Webmention
			SET valid = FALSE, updated_ts = ?1
			WHERE source = ?2 AND target = ?3
		`).bind(
			now(),
			source.toString(),
			target,
		).run()
		return new Response(webmention, {status: 400})
	}
	const { body, resolvedSource } = webmention

	// try parse as microformats
	const mf = mf2(body, { baseUrl: resolvedSource.toString() })
	const parsed = distill(mf)

	const r = await env.dovecote.prepare(`
		INSERT INTO Webmention(
			source, resolved_source, target, resolved_target,
			entered_ts, updated_ts, valid,
			type, published_ts, author_name, author_photo, content_html
		)
		VALUES (
			?2, ?3, ?4, ?5,
			?1, ?1, TRUE,
			?6, ?7, ?8, ?9, ?10
		)
		ON CONFLICT DO UPDATE SET
			resolved_source = excluded.resolved_source,
			resolved_target = excluded.resolved_target,
			updated_ts = excluded.updated_ts,
			valid = excluded.valid,
			type = excluded.type,
			published_ts = excluded.published_ts,
			author_name = excluded.author_name,
			author_photo = excluded.author_photo,
			content_html = excluded.content_html
		RETURNING *
	`).bind(
		now(), // 1
		source.toString(), // 2
		resolvedSource.toString(), // 3
		target, // 4
		resolvedTarget.toString(), // 5
		parsed?.type ?? null, // 6
		parsed?.published_ts ?? null, // 7
		parsed?.author_name ?? null, // 8
		parsed?.author_photo ?? null, // 9
		parsed?.content_html ?? null, // 10
	).run()
	console.log("insert", { result: r })

	return new Response(JSON.stringify(r))
}

function protectFromCancel(ctx: ExecutionContext, p: Promise<Response>): Promise<Response> {
	return new Promise((resolve, reject) => {
		ctx.waitUntil(p.then(resolve).catch(reject))
	})
}

const router = IttyRouter({ base: "/_dovecote" })
router
	.post("/", async (request: Request, env: Env, ctx: ExecutionContext) => {
		let formData: FormData
		try {
			formData = await request.formData()
		} catch(e) {
			return new Response(null, {status: 415, headers: {"Accept-Post": "application/x-www-form-urlencoded"}})
		}

		return await protectFromCancel(ctx, receive(formData, env))
	})
	.post("/parse", async (request: Request) => {
		const source = (await request.formData()).get("source")
		if (typeof source !== "string") return
		const r = await fetch(source)

		const mf = mf2(await r.text(), { baseUrl: r.url })
		const distilled = distill(mf)

		return new Response(JSON.stringify({
			mf,
			distilled,
		}))
	})
	.get("/", async (request: Request, env: Env) => {
		const params = (new URL(request.url)).searchParams
		const target = params.get("target")

		const r = await env.dovecote.prepare(`
			SELECT
				coalesce(published_ts, entered_ts) AS _ts,
				*
			FROM Webmention
			WHERE valid = TRUE
				AND (?1 IS NULL OR resolved_target = ?1)
			ORDER BY _ts DESC
		`).bind(target).run()
		console.log("query", {
			target: target,
			query_meta: r.meta
		})
		return new Response(JSON.stringify({
			entries: r.results
		}))
	})
	.all("*", () => new Response("dovecote: nothing here", {status:404}))

export default { ...router }
