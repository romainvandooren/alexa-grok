# Research: xAI Grok API Integration

## API Compatibility
- **OpenAI Compatibility**: xAI's API is fully compatible with OpenAI's Chat Completions API format.
- **Base URL**: `https://api.x.ai/v1`
- **Endpoint**: `/chat/completions`

## Model Selection
- **Primary Model**: `grok-4-1-fast-non-reasoning`
- **Characteristics**: Low-latency, non-reasoning, multimodal support, 2M context window.
- **Other Options**: `grok-4-1-fast-reasoning`, `grok-4.20-non-reasoning`.

## Authentication
- **Method**: Bearer Token in `Authorization` header.
- **Format**: `Authorization: Bearer <API_KEY>`

## Implementation Notes for Alexa
- **Timeout**: Alexa has an 8-second timeout for Lambda responses. The "fast" model is ideal.
- **Dependencies**: `requests` library is already in `requirements.txt` and is sufficient for these calls.
- **Request Format**: Standard JSON body with `model`, `messages`, and optional parameters like `max_completion_tokens`.
