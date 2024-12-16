# Chainlit datalayer

Chainlit datalayer shows how to log conversations happening on your Chainlit application.

## To use

Simply run:

```docker
docker compose -f compose.yaml
```

And add the following configurations to your Chainlit application:

```config.toml

```

## What is persisted ?

Thread, Step (all types), Score (feedback), Attachments.

## To deploy

Two infrastructure components make up the Chainlit datalayer:

- a database:
- an S3 for attachments

Decisions:

- use kysely or drizzle
- no projects
- no participant on Thread
- allow attachments
- no prompt
- no pothos/kysely -> ORM chainlit side only

- keep llm specific data?
- completion is legacy -> drop
