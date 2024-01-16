"use strict"; // vim: set noet:

(async function() {
	// constants
	const MAX_ENTRIES = 20;
	const API_BASE = "https://webmention.io/api/mentions.jf2?target=";

	const scriptTag = document.currentScript;

	// get url
	const url = scriptTag.getAttribute("data-url");
	if(!url) return;

	//
	// shortcuts
	//
	const become = (...elem) => {
		const frag = new DocumentFragment();
		elem.forEach(e => e && frag.appendChild(e));
		scriptTag.parentNode.replaceChild(frag, scriptTag);
	}
	// create text node
	const T = (str) => document.createTextNode(str);
	// create element
	const E = (tag, attr={}, ...ch) => {
		const elem = document.createElement(tag);
		Object.entries(attr).forEach(kv => elem.setAttribute(kv[0], kv[1]));
		ch.forEach(e => e && elem.appendChild(e));
		return elem;
	};

	// fetch webmentions. wrap in promise so we save a level of indent
	const response = await new Promise((resolve) => {
		const xhr = new XMLHttpRequest();
		xhr.onload = () => resolve(xhr.response);
		xhr.onerror = () => {
			// we don't actually get any helpful error strings, so just display a generic message
			become(E("p", {},
					E("em", {}, T("mi ken ala alasa e toki pi lipu ni")),
					E("br"),
					T("I can't seem to retrieve the comments...")
			));
		};
		xhr.responseType = "json";
		xhr.open("GET", API_BASE + encodeURIComponent(url));
		xhr.send();
	});

	console.log("Got webmention data", response);

	if(response.children.length === 0) {
		return become(E("p", {}, T("Nothing here yet. You could be the first!")));
	}

	const actionTitle = {
		"in-reply-to": "replied",
		"like-of": "liked",
		"repost-of": "reposted",
		"bookmark-of": "bookmarked",
		"mention-of": "mentioned",
		"rsvp": "RSVPed",
		"follow-of": "followed",
	};

	function getContent(r) {
		if(!r.content) return null;

		if(r.content.html) {
			const e = E("blockquote")
			e.innerHTML = r.content.html; // webmention.io sanitises it for us ^.^
			return e;
		} else if(r.content.text) {
			return E("blockquote", {}, T(r.content.text));
		}

		return null;
	}

	const entries = response.children.slice(0, MAX_ENTRIES).map(r => {
		const who = (r.author && r.author.name) || r.url.split("/")[2];
		const when = new Date(r.published || r["wm-received"]);

		// first create the bits of the heading:
		// (pic) {person name} {action} {time}

		const nametag = E("a", { rel: "nofollow ugc", title: who, href: r.author && r.author.url },
			// profile pic
			r.author && r.author.photo &&
				E("img", {
					src: r.author.photo,
					style: "display: inline-block; max-width: 2em; vertical-align: middle; border-radius: 50%",
				}),
			r.author && r.author.photo &&
				T(" "),
			T(who + " "),
		);

		const action = actionTitle[r["wm-property"]] && T(actionTitle[r["wm-property"]] + " ");

		const datetag = E("a", { rel: "nofollow ugc", href: r.url },
			E("time", { datetime: when.toISOString(), },
				T(when.toLocaleDateString(undefined, { dateStyle: "long" })),
			)
		);

		// then, the body of the thing
		const contentText = getContent(r);

		return E("li", { style: "margin-bottom: 1rem" },
			E("div", {},
				nametag, action, datetag,
			),
			contentText,
		);
	});

	return become(
		E("ul", {
			style: "list-style: none; padding: 0",
		}, ...entries,),
		response.children.length > MAX_ENTRIES &&
			E("p", { style: "opacity: .7" },
				T("+ " + (response.children.length - MAX_ENTRIES) + " more...")
			),
	);
})();
