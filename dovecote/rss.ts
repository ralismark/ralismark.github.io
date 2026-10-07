import { Datetime, WebmentionRow } from "./types"

function escapeHTML(unsafe: string): string {
	return unsafe
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;")
}

function datetimeToISO(dt: Datetime): string {
	return new Date(dt * 1000).toISOString()
}

export function* generateAtomFeed(entries: (WebmentionRow & { _ts: Datetime })[]): Generator<string> {
	// https://validator.w3.org/feed/docs/atom.html

	const feedUpdated = Math.max(...entries.map(e => e.updated_ts), 0)

	yield '<?xml version="1.0" encoding="utf-8"?>\n'
	yield `<feed xmlns="http://www.w3.org/2005/Atom">
		<id>https://kwellig.garden/_dovecote/.rss</id>
		<link rel="self" type="application/atom+xml" href="https://kwellig.garden/_dovecote/.rss" />
		<title>kwellig.garden - comments</title>
		<updated>${datetimeToISO(feedUpdated)}</updated>
		<author><name>Various</name></author>
	`

	for (const entry of entries) {
		yield `<entry>
			<id>${escapeHTML(entry.source)}</id>
			<title>Reply to ${escapeHTML(entry.resolved_target)} from ${escapeHTML(entry.resolved_source)}</title>
			<updated>${datetimeToISO(entry.updated_ts)}</updated>
			<link rel="alternate" href="${escapeHTML(entry.resolved_source)}" />
		`
		if (entry.published_ts) yield `<published>${datetimeToISO(entry.entered_ts)}</published>`
		if (entry.author_name) yield `<author><name>${escapeHTML(entry.author_name)}</name></author>`
		if (entry.content_html) yield `<content type="html">${escapeHTML(entry.content_html)}</content>`
		yield `</entry>`
	}

	yield `</feed>`
}
