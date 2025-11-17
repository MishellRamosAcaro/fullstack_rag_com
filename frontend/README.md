# Frontend - Fullstack RAG COM

## Purpose / Propósito
English: Vue 3 + Vite UI for COM operators to query customer procedures via RAG, review context, and keep a session history.

Español: Interfaz en Vue 3 + Vite para que operadores del COM consulten procedimientos por cliente vía RAG, revisen el contexto y mantengan un historial de sesión.

## Architecture / Arquitectura
```mermaid
flowchart TD
    A[Usuario] --> B[Vue 3 + PrimeVue]
    B --> C[Axios Client]
    C -->|REST| D[FastAPI Backend]
    B --> E[State (historial en memoria)]
```

## Tech Stack / Stack técnico
- Vue 3
- Vite
- Tailwind CSS
- PrimeVue 4 + PrimeIcons
- Axios

## Setup / Instalación
```bash
cd frontend
npm install
npm run dev -- --host --port 5173
```

## Docker
```bash
docker build -t fullstack-rag-frontend .
docker run -p 5173:5173 fullstack-rag-frontend
```

## Folder structure / Estructura
- `src/main.js`: bootstrap de Vue, PrimeVue y estilos.
- `src/App.vue`: vista principal con dropdown de cliente, pregunta, respuesta, contexto y historial.
- `src/assets/tailwind.css`: configuración base de Tailwind.

## Roadmap
- Añadir soporte de i18n completo.
- Estado global para compartir historial entre componentes.
- Temas oscuros y accesibilidad mejorada.
- Tests de componentes con Vitest y Cypress.

## Security / Seguridad
- Variables de entorno para la URL del backend (`VITE_API_BASE_URL`).
- Sin almacenamiento de claves en cliente.
- Manejo básico de errores y validación de campos requeridos.
