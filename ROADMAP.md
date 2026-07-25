# Dating with Intention — Product and Engineering Roadmap

## Motivation

This project began after a breakup as a personal attempt to build a dating app for people who are
only seeking long-term relationships.

It is also a learning project intended to:

- Practise Python and backend development.
- Build a mobile application with React Native and Expo.
- Learn engineering practices and infrastructure that are normally provided by an established
  platform at a large technology company.
- Explore authentication sessions, background jobs, queues, object storage, batching, caching,
  real-time communication, deployment, and observability when the product has a genuine need for
  them.

## Product principle

"Long-term relationship only" should be a product invariant, not merely the default value in a
dating-intention dropdown.

This means:

- Do not offer casual or "still figuring it out" intentions.
- Explain the expectation during onboarding.
- Ask questions that help people describe long-term compatibility.
- Allow users to report people who misrepresent their intentions.
- Avoid engagement mechanics such as unlimited swiping or artificial urgency.
- Optimise discovery for thoughtful decisions instead of time spent in the app.

Before building more features, define:

- The initial target users.
- What "long-term" means within the product.
- The minimum age and initial launch location.
- Required onboarding information.
- The rules that make a profile publishable.
- Safety, blocking, reporting, retention, and deletion expectations.
- An initial success metric, such as meaningful conversations per active user rather than swipe
  volume.

## Architecture

Keep the backend as a modular FastAPI monolith. This provides clear domain boundaries without
introducing the operational cost of microservices.

```text
Expo application
    |
    v
FastAPI REST API
    |-- accounts and sessions
    |-- profiles and photos
    |-- discovery
    |-- likes and matches
    |-- messaging
    `-- safety
           |
           v
       PostgreSQL
```

Infrastructure should be introduced when a product feature provides a real use case:

| Technology | Introduce when | Learning opportunity |
| --- | --- | --- |
| Server sessions | Now | Login, logout, expiry, rotation, revocation, and device sessions |
| Object storage | Profile photos | Signed uploads and private media |
| Background worker | Photos or match notifications | Moderation, notifications, and cleanup |
| Transactional outbox | With the worker | Reliable events following database commits |
| Redis | Rate limiting or jobs require it | TTLs, counters, and distributed coordination |
| Push notifications | Messaging works | Match and message alerts |
| WebSockets | Polling works correctly | Real-time message delivery |
| Request batching | Mobile traffic demonstrates a need | Reducing repeated profile/media requests |
| Cache | Measurements identify slow queries | Cache invalidation with a real use case |

Do not add microservices, Kafka, Kubernetes, GraphQL, or recommendation machine learning during
the MVP. They would create infrastructure work before the product produces useful scale or data.

## Milestone 0: Finish the engineering foundation

- Commit the current prompt model and migration changes.
- Add a database session dependency with clear transaction boundaries.
- Create separate development and test database configuration.
- Make pytest execute against PostgreSQL.
- Add migration tests:
  - Upgrade a clean database to the latest revision.
  - Downgrade and re-upgrade.
  - Confirm that Alembic detects no schema drift.
- Fix the existing mypy configuration error around `Settings`.
- Add continuous integration for Ruff, mypy, pytest, and migration checks.
- Add structured logging and consistent API error responses.

Completion criterion: a clean checkout can start PostgreSQL, migrate, test, lint, and run the API
using documented commands.

## Milestone 1: Authentication and first-party sessions

Use an email magic link, OAuth provider, or managed identity provider to verify identity. Do not
implement password storage as part of this project. Exchange the verified identity for a
first-party application session.

Suggested `sessions` fields:

- `id`
- `account_id`
- Hashed session token
- `created_at`
- `last_seen_at`
- `expires_at`
- `revoked_at`
- Optional device name

Session behaviour:

- Generate cryptographically random opaque tokens.
- Store only token hashes in PostgreSQL.
- Store the raw token in Expo SecureStore.
- Support rotation, logout, logout from all devices, expiry, and account suspension.
- Rate-limit authentication endpoints.
- Begin with PostgreSQL-backed sessions; introduce Redis only when justified.

Completion criterion: authenticated requests resolve exactly one account, revoked sessions stop
working, and users cannot access another account's private resources.

Add Auth0 configuration fields.
Add the Session SQLAlchemy model.
Generate and apply its migration.
Implement Auth0 JWT verification.
Implement POST /api/v1/sessions/exchange.
Generate and hash first-party session tokens.
Implement the current-account FastAPI dependency.
Implement current-device and all-device logout.
Add session expiry and revocation tests.
Build the Expo Auth0 flow and SecureStore integration.

## Milestone 2: Text-only profile onboarding

Build the first complete backend vertical slice:

- `GET /api/v1/prompts`
- `GET /api/v1/me/profile`
- `PUT /api/v1/me/profile`
- `PUT /api/v1/me/profile/prompt-answers`
- `POST /api/v1/me/profile/publish`
- `POST /api/v1/me/profile/unpublish`

Define publishability rules in the profile service. A published profile should require:

- Compliance with the supported adult age policy.
- Display name and date of birth.
- Supported location information.
- A completed biography.
- The required number of prompt answers.
- Acceptance of the long-term-only expectation.
- Profile photos once photo support is available.

Keep draft and published states explicit. Clients must not directly change `is_discoverable` or
`published_at` without domain validation.

Test ownership, invalid dates of birth, blank answers, duplicate prompts, unpublished profiles,
and suspended accounts.

Completion criterion: a user can complete and publish a text-only profile through authenticated
APIs.

## Milestone 3: Create the Expo application

Suggested libraries:

- Expo Router for navigation.
- TypeScript.
- TanStack Query for server state.
- React Hook Form and Zod for forms.
- Expo SecureStore for session credentials.
- An OpenAPI generator for API types if it provides enough value.

Initial screens:

1. Welcome and authentication.
2. Explanation and acceptance of the long-term-only principle.
3. Basic details.
4. Biography and prompt answers.
5. Profile preview.
6. Publish confirmation.
7. Account and session settings.

Business rules remain authoritative on the backend. The mobile app may mirror validation to
provide faster feedback.

Completion criterion: a new user can authenticate and publish a profile entirely from a phone or
simulator.

## Milestone 4: Photos and private object storage

Add a `ProfilePhoto` model containing ownership, storage key, display order, moderation state, and
timestamps.

Use a signed-upload workflow:

1. The app requests an upload reservation.
2. The API authorises it and returns a short-lived signed URL.
3. The app uploads directly to object storage.
4. The app confirms completion.
5. A worker validates the object and creates thumbnails.
6. Only approved photos appear in discovery.

MinIO can provide an S3-compatible local development environment. Photo processing and moderation
provide the first natural use for a background queue.

Completion criterion: users can upload, reorder, and remove private profile photos without the API
proxying image bytes.

## Milestone 5: Discovery

Start with deterministic SQL rather than machine learning.

Discovery preferences may include:

- Age range.
- Distance or supported region.
- Gender identity and who the user wants to meet.
- Responsibly represented deal-breakers.
- Exclusion of blocked, banned, unpublished, previously decided, and self profiles.

Use cursor pagination instead of offset pagination. Make eligibility decisions explainable enough
to diagnose why a candidate was included or excluded.

For an early private beta, a chronological or lightly randomised candidate pool is sufficient.
There will not yet be enough behavioural data for sophisticated ranking.

Completion criterion: discovery returns stable pages of authorised, eligible profiles without
duplicates.

## Milestone 6: Likes, passes, and mutual matches

Suggested entities:

- `ProfileDecision`: a like or pass from one profile to another.
- `Match`: created once when reciprocal likes exist.

Create decisions and matches transactionally. Use database uniqueness constraints so retries and
concurrent requests cannot create duplicate decisions or matches.

This is the appropriate point to introduce a transactional outbox:

```text
Like transaction
    |-- store decision
    |-- create match if reciprocal
    `-- store MatchCreated outbox event
                 |
                 v
          background worker
                 |
                 v
        send push notification
```

Use idempotency keys for writes that the mobile client might retry over an unreliable connection.

Completion criterion: two reciprocal likes create exactly one match, including when requests
arrive concurrently.

## Milestone 7: Conversations and messaging

Begin with REST and polling:

- One conversation per match.
- Cursor-paginated messages.
- A client-generated idempotency key for each message.
- Read position or last-read message tracking.
- Match state controls whether sending is allowed.
- Message length and rate limits.
- Blocking immediately prevents future communication.

After persistence and reconnection work correctly, add WebSockets as a transport improvement.
PostgreSQL remains the source of truth; a socket connection must never be the only place a message
exists.

Completion criterion: matched users can exchange persistent, ordered messages and recover
correctly after reconnecting.

## Milestone 8: Safety and privacy

Safety is an MVP requirement for a dating product.

Implement:

- Block user.
- Report a profile, photo, or message.
- Staff review status and audit logging.
- Account pause and deletion.
- Data export.
- Immediate discovery removal after blocking or unpublishing.
- Redaction of precise location and sensitive information from logs.
- Rate limits for discovery, likes, reports, and messages.
- Basic moderation tools before inviting users outside a trusted group.

Use soft deletion where abuse investigation or auditing requires retention. Document retention
periods and permanently delete data when legally and operationally appropriate.

Completion criterion: blocking is enforced across discovery, matching, and messaging, rather than
only hiding content in the UI.

## Milestone 9: Observability and deployment

Add:

- Request IDs.
- Structured JSON logs.
- Error tracking.
- Latency and error metrics.
- Database connection-pool metrics.
- Worker queue depth and retry metrics.
- Database backups and a tested restore procedure.
- Separate staging and production environments.
- Secret management.
- A safe deployment migration strategy.
- Privacy policy, terms, and community guidelines.

Run a small invite-only beta before enabling public discovery.

## Delivery order

The recommended delivery sequence is:

1. Foundation and tests.
2. Sessions.
3. Profile onboarding API.
4. Expo onboarding UI.
5. Photos.
6. Discovery.
7. Likes and matches.
8. Messaging.
9. Safety and administration.
10. Observability and an invite-only beta.

Every milestone should end with a demonstrable user workflow, not only additional tables.

## Immediate next implementation

The next vertical slice is **authenticated text profile onboarding**:

1. Add database session and transaction dependencies.
2. Add a test database fixture.
3. Add the `sessions` model and migration.
4. Implement the authentication dependency and session lifecycle.
5. Add Pydantic profile schemas.
6. Add profile repository and service logic.
7. Add `/api/v1/me/profile` and `/api/v1/prompts`.
8. Add profile publish and unpublish rules.
9. Add integration and authorisation tests.
10. Scaffold the Expo app after these endpoints are stable.

This slice provides practical experience with Python typing, FastAPI dependency injection,
SQLAlchemy transactions, session security, REST API design, database constraints, and integration
testing while also producing the first usable part of the product.
