# Cloudflare Workers - Lab 17 Notes

## Deployment Summary

- Worker URL: https://edge-api.makar-edge-api.workers.dev
- Main routes: `/`, `/health`, `/edge`, `/counter`, `/config`
- Configuration:
  - Vars: `APP_NAME`, `COURSE_NAME`, `RELEASE`
  - Secrets: `API_TOKEN`, `ADMIN_EMAIL` (stored via Wrangler, not in Git)
  - KV: `SETTINGS` bound to the Worker

## Evidence

- Dashboard screenshot: add a screenshot of the Worker overview/analytics page (requests or errors).
- Example `/edge` response:

```json
{"colo":"MXP","country":"CH","city":"Bellinzona","asn":51852,"httpProtocol":"HTTP/2","tlsVersion":"TLSv1.3","time":"2026-05-14T09:20:24.136Z"}
```

- Example log entry from `wrangler tail`:

```
GET https://edge-api.makar-edge-api.workers.dev/edge - Ok @ 5/14/2026, 12:22:02 PM
  (log) request { path: '/edge', colo: 'MXP', country: 'CH' }
```

- Metrics screenshot: add a screenshot of the Analytics section showing request counts/errors.

## Kubernetes vs Cloudflare Workers

| Aspect | Kubernetes | Cloudflare Workers |
|--------|------------|--------------------|
| Setup complexity | Cluster provisioning, manifests, networking, storage | Single project, CLI deploy |
| Deployment speed | Slower (image build + rollout) | Very fast (upload bundle) |
| Global distribution | Manual multi-region setup | Global by default at edge |
| Cost (for small apps) | Higher baseline (nodes) | Low/usage-based |
| State/persistence model | Volumes, databases, stateful sets | External services (KV, D1, R2) |
| Control/flexibility | Full OS/runtime control | Limited runtime, no Docker |
| Best use case | Complex apps, long-running workloads | Lightweight APIs, edge logic |

## When to Use Each

- Kubernetes: multi-service platforms, custom runtimes, heavy compute, tight networking control.
- Workers: globally distributed APIs, request routing, caching, lightweight compute.
- Recommendation: use Workers for edge APIs or routing; use Kubernetes for full control and complex systems.

## Reflection

- Easier than Kubernetes: setup and deployment speed, global routing without multi-region setup.
- More constrained: no Docker, limited runtime and filesystem access.
- Major change: Workers runs in a sandboxed edge runtime, so state must be external (KV/D1/R2).