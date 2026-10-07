import { IttyRouter } from "itty-router"
import dovecote from "../dovecote"

const router = IttyRouter()
router
	// make sure all routes here are in .assets.run_worker_first of
	// ../wrangler.jsonc
	.get("/_hello", async () => new Response("Hello from cloudflare worker!"))
	.all("/_dovecote/*", dovecote.fetch)
	.all("*", async () => new Response("no matching route in cloudflare worker", {status: 404}))

export default { ...router }
