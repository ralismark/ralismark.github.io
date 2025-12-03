CREATE TABLE Webmention (
	-- The source page, as spelled in the ping.
	source TEXT NOT NULL,
	-- The resolved source page.
	-- Currently unused.
	resolved_source TEXT NOT NULL,
	-- The target page, as spelled in the ping.
	-- For re-scrapes.
	target TEXT NOT NULL,
	-- The resolved target page.
	-- For querying all webmentions for a page.
	resolved_target TEXT NOT NULL,

	-- Processing Status -------------------------------------------------------

	-- (unix time seconds) When did this row get created?
	-- For observability and as a fallback to published_ts.
	entered_ts INTEGER NOT NULL,
	-- (unix time seconds) When was this row last updated?
	-- For observability.
	updated_ts INTEGER NOT NULL,
	-- (boolean) Instead of deleting rows, we set this to false, to avoid
	-- accidental data loss.
	valid INTEGER NOT NULL,

	-- Webmention Summary ------------------------------------------------------
	type TEXT NULL,
	published_ts INTEGER NULL,
	author_name TEXT NULL,
	author_photo TEXT NULL,
	content_html TEXT NULL -- Warning: this is *unsanitized*
) STRICT;

-- Create unique constraints as UNIQUE INDEX so we can modify them as we please.
-- (UNIQUE in table definition can't be changed!)
CREATE UNIQUE INDEX idx_Webmention_source_target ON Webmention(source, target);
CREATE INDEX idx_Webmention_canonical ON Webmention(resolved_target);

