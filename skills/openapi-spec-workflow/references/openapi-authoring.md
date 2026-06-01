# OpenAPI authoring checklist

## Minimum structure

```yaml
openapi: 3.0.3
info:
  title: Example API
  version: 1.0.0
paths: {}
```

## Always pin down

- API purpose
- owning system
- consumer(s)
- auth model
- endpoint names and methods
- request body shape
- response body shape
- error model
- ids, enums, and date/time formats

## Good defaults

### Naming
- use business-capability names
- use stable `operationId` values
- keep schema names singular and clear

### Responses
- include success + obvious failure responses
- use `404`, `400`, `401`, `403`, `409`, `422`, `500` only when they are actually plausible

### Components
Move repeated objects into `components/schemas`.

### Security
If auth is known, model it in `components/securitySchemes` and `security`.
If unknown, leave a clear TODO comment in the working draft instead of inventing certainty.

## Drafting order

1. `info`
2. `servers` if known
3. `paths`
4. operations
5. request/response payloads
6. `components/schemas`
7. security
8. examples when they add clarity

## Blunt rule

If the final design cannot tell you what the endpoint does, who calls it, and what it returns, the design is not done enough yet.
