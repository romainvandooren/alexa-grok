# Requirements: Alexa Grok Migration

## Functional Requirements
- **[FUN-01]** Skill must handle user queries via `GptQueryIntent`.
- **[FUN-02]** Skill must call xAI's `grok-4-1-fast-non-reasoning` model for responses.
- **[FUN-03]** Skill must maintain session-based conversation history.
- **[FUN-04]** Skill must generate follow-up question suggestions.
- **[FUN-05]** Skill must allow easy model name modification.

## Non-Functional Requirements
- **[NFR-01]** API calls must be efficient to avoid Alexa timeouts (8 seconds).
- **[NFR-02]** System prompts must be adapted for the Grok model.
- **[NFR-03]** API keys must not be hardcoded in the final version (use environment variables).

## Out of Scope
- Integration with other xAI features (like vision) for now.
- Custom training or fine-tuning of the model.
