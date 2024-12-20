# Chainlit datalayer

PostgresSQL data layer for Chainlit apps. Schema description is in `prisma/schema.prisma`. 
Option to upload elements to cloud storage.

## Demo

![Data layer demo](./demo.gif) # TODO: update

## Try it locally

### Run services

Run:

```docker
docker compose -f compose.yaml
```

Two services are now up:
- a fresh (empty) PostgreSQL
- a 'fake' S3 bucket - to simulate storage for elements

We create table and "imprint" our Prisma schema to the fresh PostgreSQL:
```
npx prisma migrate deploy
```

To view your data, use `npx prisma studio`.

Now, all tables are created and welcoming chat data!

## Use from Chainlit

Add the following environment variables in `.env`:
```
# To link to the PostgreSQL instance.
DATABASE_URL="postgresql+asyncpg://root:root@localhost:5432/postgres"
```

Upon running `chainlit run app.py`, Chainlit attempts to connect to the 
specified database and keeps track of threads, users, steps, elements, feedback. 

Remember to activate:
- user authentication: https://docs.chainlit.io/authentication/overview
- chat history: https://docs.chainlit.io/data-persistence/history#chat-history

Elements -- that is files attached in the chat -- are written to a cloud storage. 
Locally, we have a fake S3 running up, which you can connect to with the following
`.env` configuration:

```
BUCKET_NAME="my-bucket"

# S3 configuration.
APP_AWS_ACCESS_KEY="random-key"
APP_AWS_SECRET_KEY="random-key"
APP_AWS_REGION="eu-central-1"
DEV_AWS_ENDPOINT="http://localhost:4566"
```

Re-launch your Chainlit app and add files to your chat. Then browse to 
http://localhost:4566/my-bucket to list your attachments. 

## Deploy in production

In production, deploy a production database -- please use robust passwords --
and point to an actual cloud provider. 

Chainlit supports three cloud providers, see below for `.env` example
configurations.

### AWS S3

```
APP_AWS_ACCESS_KEY="random-key"
APP_AWS_SECRET_KEY="random-key"
APP_AWS_REGION="eu-central-1"
DEV_AWS_ENDPOINT="http://localhost:4566"
```

### Google Cloud Storage (GCS)

With Google Cloud, the following environment variables are necessary to connect:
- `APP_GCS_PROJECT_ID`: project ID (not the project number)
- `APP_GCS_CLIENT_EMAIL`: email of the service account with adequate permissions 
- `APP_GCS_PRIVATE_KEY`: secret key to authenticate

Create your service account from "IAM & Admin" > "Service Accounts". 
You can go with Storage Object Viewer and Creator/Admin. 
Key for the service account can be created from the "Keys" tab on the service account
details page. 

Here's an example of what your configuration could look like:
```
APP_GCS_PROJECT_ID="chat-project-123456"
APP_GCS_CLIENT_EMAIL="chat-project-bucket@chat-project-123456.iam.gserviceaccount.com"
APP_GCS_PRIVATE_KEY="ABC...123...XYZ"
```

### Azure Blob Storage

??