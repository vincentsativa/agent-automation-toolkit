# Code Review Checklist

## Correctness
- Does the code do what it claims?
- Edge cases handled (empty inputs, nulls, large data, concurrent access)?
- Error paths handled gracefully?

## Security
- No hardcoded secrets, credentials, or API keys
- Input validation on user-facing inputs
- No SQL injection, XSS, or path traversal
- Auth/authz checks where needed

## Code Quality
- Clear naming (variables, functions, classes)
- No unnecessary complexity or premature abstraction
- DRY, no duplicated logic that should be extracted
- Functions are focused (single responsibility)

## Testing
- New code paths tested?
- Happy path and error cases covered?
- Tests readable and maintainable?

## Performance
- No N+1 queries or unnecessary loops
- Appropriate caching where beneficial
- No blocking operations in async code paths

## Documentation
- Public APIs documented
- Non-obvious logic has comments explaining "why"
- README updated if behavior changed