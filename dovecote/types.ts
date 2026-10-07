export type Datetime = number // unix time in seconds

// Identical to Webmention table of schema.sql
export type WebmentionRow = {
	source: string
	resolved_source: string
	target: string
	resolved_target: string
	entered_ts: Datetime
	updated_ts: Datetime
	valid: number,
	text: string | null,
	published_ts: Datetime | null,
	author_name: string | null,
	author_photo: string | null,
	content_html: string | null,
}
