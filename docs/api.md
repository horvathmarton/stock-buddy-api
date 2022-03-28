# API conventions

This API is following the RESTful API conventions.

- Try to expose everything as a resource.
- Use the URL path to describe hierarchy. Use nouns as much as possible.
- Describe the type of operation with the HTTP verb.
- Use the proper HTTP status code in responses.
- Communicate in JSON format.
- Use `kebab-case` in URL path.
- Use `snake_case` in query params and payload properties.

Think of any resource/operation on the server as one of the four types:

- Document: a single resource (e.g.: a stock trade)
- Collection: a list of resource exposed to the users, but handled by the server (e.g.: stocks)
- Store: a list of resource exposed and handled by the client (e.g.: strategy with items)
- Controller: a procedural concept triggered by the user (verbs in URL is prohibitted in this case) (e.g.: select strategy)
