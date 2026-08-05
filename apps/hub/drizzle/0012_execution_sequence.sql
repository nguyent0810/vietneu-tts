DROP INDEX "llm_execution_run_provider_iteration_key";--> statement-breakpoint
ALTER TABLE "llm_execution" ADD COLUMN "execution_sequence" integer DEFAULT 1 NOT NULL;--> statement-breakpoint
CREATE UNIQUE INDEX "llm_execution_run_provider_sequence_key" ON "llm_execution" USING btree ("analysis_run_id","provider","execution_sequence");