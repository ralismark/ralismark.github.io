// https://indieweb.org/post-type-discovery

export type PostType =
	| "rsvp"
	| "reply"
	| "repost"
	| "like"
	| "video"
	| "photo"
	| "note"
	| "article"

export function discoverPostType(post: MicroformatRoot): PostType {
	// 1. If the post has an "rsvp" property with a valid value,
	//    Then it is an RSVP post.
	if (post.properties["rsvp"]) return "rsvp"

	// 2. If the post has an "in-reply-to" property with a valid URL,
	//    Then it is a reply post.
	if (post.properties["in-reply-to"]) return "reply"

	// 3. If the post has a "repost-of" property with a valid URL,
	//    Then it is a repost (AKA "share") post.
	if (post.properties["repost-of"]) return "repost"

	// 4. If the post has a "like-of" property with a valid URL,
	//    Then it is a like (AKA "favorite") post.
	if (post.properties["like-of"]) return "like"

	// 5. If the post has a "video" property with a valid URL,
	//    Then it is a video post.
	if (post.properties["video"]) return "video"

	// 6. If the post has a "photo" property with a valid URL,
	//    Then it is a photo post.
	if (post.properties["photo"]) return "photo"

	return "note"
	/* lot of expensive logic just to distinguish between "article" and "note"

	// 7. If the post has a "content" property with a non-empty value,
	//    Then use its first non-empty value as the content
	let content: string
	if (post.properties["content"]) content = (post.properties["content"][0] as Html).value

	// 8. Else if the post has a "summary" property with a non-empty value,
	//    Then use its first non-empty value as the content
	else if (post.properties["summary"]) content = (post.properties["summary"][0] as Html).value

	// 9. Else it is a note post.
	else return "note"

	// 10. If the post has no "name" property
	//       or has a "name" property with an empty string value (or no value)
	//     Then it is a note post.
	if (!post.properties["name"] || !post.properties["name"][0]) return "note"

	// 11. Take the first non-empty value of the "name" property
	let name = post.properties["name"][0] as string
	// 12. Trim all leading/trailing whitespace
	name = name.trim()
	// 13. Collapse all sequences of internal whitespace to a single space (0x20) character each
	name = name.replaceAll(/\s+/, " ")
	// 14. Do the same with the content
	content = content.trim().replaceAll(/\s+/, " ")

	// 15. If this processed "name" property value is NOT a prefix of the processed content,
	//     Then it is an article post.
	if (!content.startsWith(name)) return "article"

	// 16. It is a note post.
	return "note"

	*/
}
