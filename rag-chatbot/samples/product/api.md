# Developer API

## Authentication
The API uses bearer tokens. Create a token under Settings > Developer > API keys and send it as `Authorization: Bearer <token>`. Tokens inherit the permissions of the user who created them.

## Rate limits
The default rate limit is 120 requests per minute per token. Exceeding it returns HTTP 429 with a `Retry-After` header. Business plans can request a higher limit.

## Webhooks
Register a webhook URL under Settings > Developer > Webhooks. We send a signed POST on every board change; verify the `X-Signature` header against your signing secret to confirm authenticity.
