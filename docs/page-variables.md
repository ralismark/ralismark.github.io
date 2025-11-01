# Page Variables

The variables available to a page are:

`site`, containing information about the entire site.

|Variable|Description|Example|
|-
|`site.drafts`|Is the site in dev mode?|`true`|
|`site.url`|Full url that the site will be deployed to e.g. for permalinks|`https://kwellig.garden`|
|`site.fqdn`|`site.url` without the protocol|`kwellig.garden`|
|`site.title`|Title for the website|`Kwellig's Garden`|
|`site.description`|Description/byline|`Where temmie puts her things`|
|`site.collections`|Dict of all collections under the site; see `collection` below for value|`{"posts": ...}`|

`page`, containing page-specific information, including the front-matter

|Variable|Description|Example|
|-
|`page.path`|input absolute path|`"/path/to/project/foo/things/index.md"`|
|`page.opath`|output path relative to the output directory|`"foo/things.html`|
|`page.url`|permalink|`"/foo/things"`|
|`page.props`|frontmatter|`{"layout": "post", "title": "I love cats"}`|

`collection`, about the current collection

|Variable|Description|Example|
|-
|`collection`|List of all posts||
|`collection.series`|Dict of series to the posts in that series||

`__file__`, the path of the current _Jinja_ file, cf `page.path` -- in templates this is the path of the template, while `page.path` is the original page being rendered.
