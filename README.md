# Chainlit datalayer

Basic data layer for Chainlit apps. Schema description is in `prisma/schema.prisma`.

## Run services

Run:

```docker
docker compose -f compose.yaml
```

Two services are now up:

- a fresh PostgreSQL
- a 'fake' S3 bucket - to simulate storage for attachments

## Deploy schema to DB

Run:

```
npx prisma migrate deploy
```

## Use from Chainlit

Add the following environment variables in `.env`:

```
# To link to the PostgreSQL instance
DATABASE_URL="postgresql+asyncpg://root:root@localhost:5432/postgres"

# To link to the S3 bucket
BUCKET_NAME="my-bucket"
APP_AWS_ACCESS_KEY="random-key"
APP_AWS_SECRET_KEY="random-key"
APP_AWS_REGION="eu-central-1"
DEV_AWS_ENDPOINT="http://localhost:4566"
```

For production, use robust passwords and point to your actual storage provider.
See [supported list](https://docs.chainlit.io).
