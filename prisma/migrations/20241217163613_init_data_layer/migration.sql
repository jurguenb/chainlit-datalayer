-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- CreateEnum
CREATE TYPE "StepType" AS ENUM ('assistant_message', 'embedding', 'llm', 'retrieval', 'rerank', 'run', 'system_message', 'tool', 'undefined', 'user_message');

-- CreateEnum
CREATE TYPE "ScoreType" AS ENUM ('HUMAN', 'CODE', 'AI');

-- CreateTable
CREATE TABLE "Attachment" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "threadId" TEXT,
    "stepId" TEXT NOT NULL,
    "metadata" JSONB NOT NULL,
    "mime" TEXT,
    "name" TEXT NOT NULL,
    "objectKey" TEXT,
    "url" TEXT,

    CONSTRAINT "Attachment_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Participant" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB NOT NULL,
    "identifier" TEXT NOT NULL,
    "lastEngaged" TIMESTAMP(3),

    CONSTRAINT "Participant_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Score" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "stepId" TEXT,
    "type" "ScoreType" NOT NULL DEFAULT 'HUMAN',
    "name" TEXT NOT NULL,
    "value" DOUBLE PRECISION NOT NULL,
    "valueLabel" TEXT,
    "comment" TEXT,
    "scorer" TEXT,

    CONSTRAINT "Score_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Step" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "parentId" TEXT,
    "threadId" TEXT,
    "input" JSONB,
    "metadata" JSONB NOT NULL,
    "name" TEXT,
    "output" JSONB,
    "type" "StepType" NOT NULL,
    "startTime" TIMESTAMP(3) NOT NULL,
    "endTime" TIMESTAMP(3) NOT NULL,
    "rootRunId" TEXT,
    "variables" JSONB,
    "settings" JSONB,
    "tools" JSONB,

    CONSTRAINT "Step_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Thread" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" TIMESTAMP(3),
    "name" TEXT,
    "metadata" JSONB NOT NULL,
    "tokenCount" INTEGER NOT NULL DEFAULT 0,
    "participantId" TEXT,

    CONSTRAINT "Thread_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Attachment_stepId_idx" ON "Attachment"("stepId");

-- CreateIndex
CREATE INDEX "Attachment_threadId_idx" ON "Attachment"("threadId");

-- CreateIndex
CREATE INDEX "Participant_identifier_idx" ON "Participant"("identifier");

-- CreateIndex
CREATE INDEX "Score_createdAt_idx" ON "Score"("createdAt");

-- CreateIndex
CREATE INDEX "Score_name_idx" ON "Score"("name");

-- CreateIndex
CREATE INDEX "Score_stepId_idx" ON "Score"("stepId");

-- CreateIndex
CREATE INDEX "Score_value_idx" ON "Score"("value");

-- CreateIndex
CREATE INDEX "Score_name_value_idx" ON "Score"("name", "value");

-- CreateIndex
CREATE INDEX "Step_createdAt_idx" ON "Step"("createdAt");

-- CreateIndex
CREATE INDEX "Step_endTime_idx" ON "Step"("endTime");

-- CreateIndex
CREATE INDEX "Step_parentId_idx" ON "Step"("parentId");

-- CreateIndex
CREATE INDEX "Step_startTime_idx" ON "Step"("startTime");

-- CreateIndex
CREATE INDEX "Step_rootRunId_idx" ON "Step"("rootRunId");

-- CreateIndex
CREATE INDEX "Step_threadId_idx" ON "Step"("threadId");

-- CreateIndex
CREATE INDEX "Step_type_idx" ON "Step"("type");

-- CreateIndex
CREATE INDEX "Step_name_idx" ON "Step"("name");

-- CreateIndex
CREATE INDEX "Step_threadId_startTime_endTime_idx" ON "Step"("threadId", "startTime", "endTime");

-- CreateIndex
CREATE INDEX "Thread_createdAt_idx" ON "Thread"("createdAt");

-- CreateIndex
CREATE INDEX "Thread_tokenCount_idx" ON "Thread"("tokenCount");

-- AddForeignKey
ALTER TABLE "Attachment" ADD CONSTRAINT "Attachment_stepId_fkey" FOREIGN KEY ("stepId") REFERENCES "Step"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Attachment" ADD CONSTRAINT "Attachment_threadId_fkey" FOREIGN KEY ("threadId") REFERENCES "Thread"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Score" ADD CONSTRAINT "Score_stepId_fkey" FOREIGN KEY ("stepId") REFERENCES "Step"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Step" ADD CONSTRAINT "Step_rootRunId_fkey" FOREIGN KEY ("rootRunId") REFERENCES "Step"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Thread" ADD CONSTRAINT "Thread_participantId_fkey" FOREIGN KEY ("participantId") REFERENCES "Participant"("id") ON DELETE SET NULL ON UPDATE CASCADE;
