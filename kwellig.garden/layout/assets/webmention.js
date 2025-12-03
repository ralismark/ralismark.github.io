
(async function() {
	// constants
	const API_BASE = "/_dovecote?target=";

	const scriptTag = document.getElementById("webmention-js");

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

	if(response.entries.length === 0) {
		return become(E("p", {}, T("Nothing here yet. You could be the first!")));
	}

	await import("https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js");

	const entries = response.entries.map(r => {
		// first create the bits of the heading:
		// (pic) {person name} {action} {time}

		const who = r.author_name || (new URL(r.resolved_source)).host
		const nametag = E("span", { title: who, class: "u-author h-card" },
			// profile pic
			E("img", {
				src: r.author_photo,
				style: "display: inline-block; max-width: 2em; vertical-align: middle; border-radius: 50%",
			}),
			T(" " + who),
		);

		const actionTitle = {
			"reply": "replied",
			"repost": "reposted",
			"like": "liked",
		};
		const action = T(actionTitle[r.type] || "mentioned")

		const when = new Date(r._ts * 1000)
		const datetag = E("a", { class: "u-url", rel: "nofollow ugc", href: r.source },
			E("time", { class: "dt-published", datetime: when.toISOString(), },
				T(when.toLocaleDateString(undefined, { dateStyle: "long" })),
			)
		);

		// then, the body of the thing
		let content = null
		if (r.content_html) {
			content = E("blockquote", { class: "e-content" })
			content.innerHTML = DOMPurify.sanitize(r.content_html)
		}

		// assemble everything together
		return E("li", { style: "margin-bottom: 1rem", class: "u-comment h-cite" },
			E("div", {},
				nametag, T(" "), action, T(" on "), datetag,
			),
			content,
		);
	});

	return become(
		E("ul", {
			style: "list-style: none; padding: 0",
		}, ...entries,),
	);
})();
