# Dovecote

Dovecote is the Webmention receiver for my website, built on Cloudflare Workers.

Previously I used <https://webmention.io>.
My motivations for making my own are:

- webmention.io doesn't handle redirects and rel=canonical ([#217](https://github.com/aaronpk/webmention.io/issues/217)).
	It also assumes domain names don't change, which I violated when I switched to `kwellig.garden`.
	The whole thing with old webmentions being stranded isn't a huge issue -- I can just fetch the couple variations of a page url -- but it just kinda sucks.

- webmention.io didn't have any way of directly interacting with the stored webmentions.
	This would allow remedying the issues with me moving pages... or just any sort of data cleanup.
	I'd also get ownership over my data this way, instead of relying on another third-party service.

## How it works

The webmention endpoint implements the [webmention spec](https://www.w3.org/TR/webmention/).
It also does microformats parsing to get additional data, like author, contents, and post type.

Of note, it should handle re-processing and deletions, since we'd use that functionality when submitting a batch of webmentions, or updating them.
Batch-processing can likely just be handled by a script that respects backoff/etc, rather than implemented inside the worker.

We'll still be exposing a similar API as webmention.io:

- Get all webmentions for a particular `target`
- Get all webmentions, overall.
	This could be used for a feed page, or just an RSS feed.

### Data Storage

Conceptually, we store the webmentions in a table with the following fields:

- `target`, canonical URL of our page receiving the webmention.
- `source`, the page that referenced `target`.
	Together with `target`, they form a unique key.
- `data`, the actual extracted data from `source` (probably jf2 format).

We might also want a `dt-published` field (when `source` was published) in the table, for sorting reasons, but we can also push that responsibility onto clients if fetching all entries isn't an issue.
For individual pages, that shouldn't be an issue, but for fetching the sitewide feed, it may be.

We need to be able to perform the following queries:

- Find all rows with a specific `target`.
	Additionally ordered by `dt-published`, if we're ordering data server-side.
- List all rows.
	Additionally ordered by `dt-published`, if we're ordering data server-side.
- Find and update/delete the row for a specific `target` + `source` combination.

I was originally planning on using R2 (or S3) as the actual data store, whose list API only allows filtering by prefix and paginating in lexicographical order.
If we don't use `dt-published`, we can have `<target>#<source>` as the object key.
If we do, we need `<target>#<dt-published>#<source>`, which stops us from being able to locate a row easily.

The benefit of S3 is that it's really easy to work with the data -- we can use filesystem-based tools like rclone.

Alternatively, we can use Cloudflare D1, which is a regular SQL database.
It should be pretty obvious how our data format maps onto one.
