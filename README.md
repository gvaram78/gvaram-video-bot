# STYLIO MVP Backend Foundation

Express + MongoDB backend for STYLIO (beauty services marketplace in Georgia), including JWT auth, provider/client/admin flows, and a small frontend tester.

## Features covered

- Roles: `client`, `provider`, `admin`
- Provider profile, up to 6 photos, services, availability, location options
- Provider verification docs upload + admin review flow
- Client browse/filter providers by city/service type
- Booking with multiple services in one appointment
- Booking statuses: `pending`, `confirmed`, `completed`, `cancelled`
- Fixed 10 GEL booking deposit (mock payment marked paid)
- Admin: users, bookings, provider moderation, banner management
- Cities supported: Tbilisi, Rustavi, Batumi, Kutaisi
- Language field support: Georgian (`ka`), Russian (`ru`), English (`en`)

## Project structure

- `src/models`: MongoDB schemas (users, providers, bookings, banners)
- `src/controllers`: business logic for auth/provider/booking/admin APIs
- `src/routes`: REST endpoints
- `src/middleware`: auth, upload handlers, and error handling
- `src/public/index.html`: basic UI to test API quickly

## Run locally

1. Install dependencies
   ```bash
   npm install
   ```
2. Copy env file
   ```bash
   cp .env.example .env
   ```
3. Update `.env` values (especially `JWT_SECRET` and `MONGODB_URI`)
4. Start MongoDB locally (or use MongoDB Atlas)
5. Run API in dev mode
   ```bash
   npm run dev
   ```
6. Open:
   - API: `http://localhost:5000/api/health`
   - Frontend tester: `http://localhost:5000`

## Core endpoints (MVP)

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Providers
- `GET /api/providers`
- `GET /api/providers/:id`
- `POST /api/providers/me/profile`
- `POST /api/providers/me/services`
- `POST /api/providers/me/photos` (multipart field: `photos`)
- `POST /api/providers/me/verification-docs` (multipart field: `docs`)

### Bookings
- `POST /api/bookings`
- `GET /api/bookings`
- `PATCH /api/bookings/:id/status`

### Admin
- `GET /api/admin/dashboard`
- `PATCH /api/admin/providers/:id/review`
- `GET /api/admin/users`
- `PATCH /api/admin/users/:id/status`
- `GET /api/admin/bookings`
- `POST /api/admin/banners`
- `GET /api/admin/banners`
- `DELETE /api/admin/banners/:id`

## Notes
- Payments are mocked for MVP and always set booking deposit (`10 GEL`) as paid on booking creation.
- Provider approval is required (`approvedByAdmin`) to show in browse list and allow bookings.
