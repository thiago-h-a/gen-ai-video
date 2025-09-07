
# React SPA (placeholder)

Implement a Vite + React + TypeScript SPA that:
- Submits prompts to `POST /api/prompts`
- Polls/streams job status (`GET /api/jobs/{id}`, optional SSE via `/api/events`)
- Renders artifacts by calling `GET /api/artifacts/{artifact_key}` and
  displaying the returned URL.

## Suggested structure

```
src/
  main.tsx
  App.tsx
  components/
    PromptForm.tsx
    JobStatus.tsx
    ArtifactViewer.tsx
  lib/
    api.ts  # thin fetch wrappers
```

## Quick start (when implemented)

```bash
npm create vite@latest react_app -- --template react-ts
cd react_app
npm install
npm run dev
```
