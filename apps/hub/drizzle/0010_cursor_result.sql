CREATE TABLE "cursor_analysis_result" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"llm_execution_id" uuid NOT NULL,
	"request_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"schema_version" text NOT NULL,
	"payload" jsonb NOT NULL,
	"payload_hash" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "cursor_result_hash_format" CHECK ("cursor_analysis_result"."payload_hash" ~ '^[0-9a-f]{64}$')
);
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result" ADD CONSTRAINT "cursor_analysis_result_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "cursor_analysis_result" ADD CONSTRAINT "cursor_result_execution_workspace_fk" FOREIGN KEY ("llm_execution_id","workspace_id") REFERENCES "public"."llm_execution"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "cursor_analysis_result" ADD CONSTRAINT "cursor_result_request_workspace_fk" FOREIGN KEY ("request_id","workspace_id") REFERENCES "public"."cursor_analysis_request"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "cursor_analysis_result" ADD CONSTRAINT "cursor_result_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "cursor_result_execution_key" ON "cursor_analysis_result" USING btree ("llm_execution_id");--> statement-breakpoint
CREATE INDEX "cursor_result_request_idx" ON "cursor_analysis_result" USING btree ("request_id");