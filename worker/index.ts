import { IttyRouter } from "itty-router"
import dovecote from "../dovecote"

const router = IttyRouter()
router
	.get("/_hello", () => "Hello world")
	.all("/_dovecote/*", dovecote.fetch)
	.all("*", async (request, env) => {
		return await env.ASSETS.fetch(new Request(request.url, { ...request }))
	})

export default { ...router }
