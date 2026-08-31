# sdd-kit — Dev Environment Notes

## Structure
- The repo is primarily a Claude Code / Codex plugin (markdown specs, Python hook scripts, agent definitions).
- The `landing/` directory contains a Vite + React + Tailwind landing page (the public-facing site for the plugin).

## Running locally
```bash
docker compose -f docker-compose.base44.yml up -d
```
The landing page dev server is on port 3000 (mapped from Vite's 5173).

## No external services or secrets required
The landing page is a static site — no backend, no database, no API keys needed.

## Verify
`curl http://localhost:3000/` should return the HTML page with live Vite dev modules.
