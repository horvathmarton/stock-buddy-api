# Logging

## Guidelines

1. Use full English sentences. Present continuous tense before the fact and past simple after (e.g.: `Starting sync 123 initiated by hello user.` and `Finished sync 123.`). Prefer logging before the action if not using both.
2. Log as much as possible on the lowest level possible. This way we avoid spamming high level channels, but could keep the most information for debugging.
3. Don't log sensitive information! Check the variables in a log entry to avoid leaking any sensitive data.

## Log levels

- **TRACE**: Don't commit anything on this level. Use it for local debugging.
- **DEBUG**: Anything that don't fits at least info.
- **INFO**: User driven and system specific (scheduled) actions.
- **WARN**: Anything that could become an error.
- **ERROR**: Exceptional condition in the app.
- **CRITICAL**: Anything that has to terminate the process.

## Tips

- Write the log massage as a standalone item (don't presume anything from code context). E.g.: `User registered` is bad, `User 1234 successfully registered with email asdf@email.com.`.
- Append the stack trace when logging an error.
