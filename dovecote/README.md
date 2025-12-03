Dovecote is a [Webmention receiver](https://www.w3.org/TR/webmention/) that also performs microformats parsing to get post information, similar to <https://webmention.io>, which I previously used.
My motivations for making my own are:

- webmention.io doesn't handle target redirects ([#217](https://github.com/aaronpk/webmention.io/issues/217)).
	It also assumes domain names don't change, which I violated when I switched to `kwellig.garden`.
	The whole thing with old webmentions being stranded isn't a huge issue -- I can just fetch the couple variations of a page url -- but it's extra work.

- webmention.io didn't have any way of directly interacting with the stored webmentions.
	This would allow remedying the issues with me moving pages... or just any sort of data cleanup.
	I'd also get ownership over my data this way, instead of relying on another third-party service.

# Design Considerations

## Redirects

Redirects (both source and target) are tricky to support.

For target redirects (i.e. us changing the canonical URL of a page):

- I'm allowing it to require additional manual intervention from us.
- In order to support re-scrapes, we need to keep both original and canonical target URLs.
- Source may mention multiple aliases of the same page -- we don't support this well currently.

Source redirects are currently not supported.
