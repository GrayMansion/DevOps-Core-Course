export interface Env {
	APP_NAME: string;
	COURSE_NAME: string;
	RELEASE: string;
	API_TOKEN: string;
	ADMIN_EMAIL: string;
	SETTINGS: KVNamespace;
}

const jsonResponse = (data: unknown, init?: ResponseInit): Response =>
	Response.json(data, init);

export default {
	async fetch(request: Request, env: Env): Promise<Response> {
		const url = new URL(request.url);
		const path = url.pathname;
		const now = new Date().toISOString();

		console.log("request", {
			path,
			colo: request.cf?.colo,
			country: request.cf?.country,
		});

		if (path === "/health") {
			return jsonResponse({ status: "ok", time: now });
		}

		if (path === "/") {
			return jsonResponse({
				app: env.APP_NAME,
				course: env.COURSE_NAME,
				release: env.RELEASE,
				message: "Hello from Cloudflare Workers",
				timestamp: now,
				tokenConfigured: Boolean(env.API_TOKEN),
				adminConfigured: Boolean(env.ADMIN_EMAIL),
			});
		}

		if (path === "/edge") {
			return jsonResponse({
				colo: request.cf?.colo ?? null,
				country: request.cf?.country ?? null,
				city: request.cf?.city ?? null,
				asn: request.cf?.asn ?? null,
				httpProtocol: request.cf?.httpProtocol ?? null,
				tlsVersion: request.cf?.tlsVersion ?? null,
				time: now,
			});
		}

		if (path === "/counter") {
			if (request.method !== "GET" && request.method !== "POST") {
				return new Response("Method Not Allowed", { status: 405 });
			}
			const raw = await env.SETTINGS.get("visits");
			const visits = Number.parseInt(raw ?? "0", 10) + 1;
			await env.SETTINGS.put("visits", String(visits));
			return jsonResponse({ visits, time: now });
		}

		if (path === "/config") {
			return jsonResponse({
				app: env.APP_NAME,
				course: env.COURSE_NAME,
				release: env.RELEASE,
				secretsPresent: {
					apiToken: Boolean(env.API_TOKEN),
					adminEmail: Boolean(env.ADMIN_EMAIL),
				},
				time: now,
			});
		}

		return new Response("Not Found", { status: 404 });
	},
} satisfies ExportedHandler<Env>;
