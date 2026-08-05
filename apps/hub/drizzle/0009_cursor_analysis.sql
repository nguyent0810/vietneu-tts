-- Thứ tự BẮT BUỘC: tạo bảng -> tạo UNIQUE đích -> thêm khoá ngoại ghép.
-- drizzle-kit sinh UNIQUE sau FK, PostgreSQL từ chối với "no unique constraint
-- matching given keys". Đã sắp lại thủ công.

CREATE TYPE "public"."cursor_failure_class" AS ENUM('NONE', 'INVALID_JSON', 'PROSE_OUTSIDE_JSON', 'SCHEMA_MISMATCH', 'MISSING_REQUIRED_FIELD', 'TRUNCATED_OUTPUT', 'UNSUPPORTED_SCHEMA_VERSION', 'CLI_NONZERO_EXIT', 'CLI_TIMEOUT', 'OUTPUT_TOO_LARGE', 'UNSUPPORTED_CLAIM', 'EVIDENCE_UNRESOLVED');
--> statement-breakpoint
CREATE TYPE "public"."validation_severity" AS ENUM('BLOCKER', 'HIGH', 'MEDIUM', 'LOW');
--> statement-breakpoint
CREATE TABLE "analysis_validation" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"llm_execution_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"passed" boolean NOT NULL,
	"failure_class" "cursor_failure_class" DEFAULT 'NONE' NOT NULL,
	"structural_issues" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"evidence_issues" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"claim_issues" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"quality_issues" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"evidence_resolution_rate" numeric(5, 4),
	"total_evidence_refs" integer DEFAULT 0 NOT NULL,
	"unresolved_evidence_refs" integer DEFAULT 0 NOT NULL,
	"causal_violations" integer DEFAULT 0 NOT NULL,
	"ctr_violations" integer DEFAULT 0 NOT NULL,
	"unsupported_metric_violations" integer DEFAULT 0 NOT NULL,
	"finding_count" integer DEFAULT 0 NOT NULL,
	"hypothesis_count" integer DEFAULT 0 NOT NULL,
	"recommendation_count" integer DEFAULT 0 NOT NULL,
	"experiment_count" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "analysis_validation_rate_range" CHECK ("analysis_validation"."evidence_resolution_rate" IS NULL OR ("analysis_validation"."evidence_resolution_rate" >= 0 AND "analysis_validation"."evidence_resolution_rate" <= 1))
);
--> statement-breakpoint
CREATE TABLE "cursor_analysis_request" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"analysis_package_id" uuid NOT NULL,
	"package_hash" text NOT NULL,
	"prompt_revision_id" uuid NOT NULL,
	"prompt_hash" text NOT NULL,
	"prompt_bytes" integer NOT NULL,
	"omissions" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "cursor_request_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "cursor_request_package_hash_format" CHECK ("cursor_analysis_request"."package_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "cursor_request_prompt_hash_format" CHECK ("cursor_analysis_request"."prompt_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "cursor_request_prompt_bytes_positive" CHECK ("cursor_analysis_request"."prompt_bytes" > 0)
);
--> statement-breakpoint
CREATE TABLE "cursor_execution_manifest" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"llm_execution_id" uuid NOT NULL,
	"request_id" uuid NOT NULL,
	"attempt_number" integer NOT NULL,
	"parent_execution_id" uuid,
	"tool_name" text NOT NULL,
	"tool_version" text,
	"model" text,
	"flags" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"started_at" timestamp with time zone NOT NULL,
	"finished_at" timestamp with time zone,
	"duration_ms" integer,
	"exit_code" integer,
	"timed_out" boolean DEFAULT false NOT NULL,
	"stdout_hash" text,
	"stdout_bytes" integer,
	"stderr_hash" text,
	"stderr_excerpt" text,
	"output_schema_version" text,
	"failure_class" "cursor_failure_class" DEFAULT 'NONE' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "cursor_manifest_attempt_bounds" CHECK ("cursor_execution_manifest"."attempt_number" >= 1 AND "cursor_execution_manifest"."attempt_number" <= 3),
	CONSTRAINT "cursor_manifest_stdout_hash_format" CHECK ("cursor_execution_manifest"."stdout_hash" IS NULL OR "cursor_execution_manifest"."stdout_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "cursor_manifest_stderr_hash_format" CHECK ("cursor_execution_manifest"."stderr_hash" IS NULL OR "cursor_execution_manifest"."stderr_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "cursor_manifest_no_self_parent" CHECK ("cursor_execution_manifest"."parent_execution_id" IS DISTINCT FROM "cursor_execution_manifest"."llm_execution_id")
);
--> statement-breakpoint
ALTER TABLE "analysis_package" ADD CONSTRAINT "analysis_package_id_workspace_key" UNIQUE("id","workspace_id");
--> statement-breakpoint
ALTER TABLE "analysis_validation" ADD CONSTRAINT "analysis_validation_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "analysis_validation" ADD CONSTRAINT "analysis_validation_execution_workspace_fk" FOREIGN KEY ("llm_execution_id","workspace_id") REFERENCES "public"."llm_execution"("id","workspace_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "analysis_validation" ADD CONSTRAINT "analysis_validation_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cursor_analysis_request" ADD CONSTRAINT "cursor_analysis_request_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cursor_analysis_request" ADD CONSTRAINT "cursor_request_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cursor_analysis_request" ADD CONSTRAINT "cursor_request_run_workspace_channel_fk" FOREIGN KEY ("analysis_run_id","workspace_id","channel_id") REFERENCES "public"."analysis_run"("id","workspace_id","channel_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cursor_analysis_request" ADD CONSTRAINT "cursor_request_package_workspace_fk" FOREIGN KEY ("analysis_package_id","workspace_id") REFERENCES "public"."analysis_package"("id","workspace_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD CONSTRAINT "cursor_execution_manifest_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD CONSTRAINT "cursor_manifest_execution_workspace_fk" FOREIGN KEY ("llm_execution_id","workspace_id") REFERENCES "public"."llm_execution"("id","workspace_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD CONSTRAINT "cursor_manifest_request_workspace_fk" FOREIGN KEY ("request_id","workspace_id") REFERENCES "public"."cursor_analysis_request"("id","workspace_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
CREATE UNIQUE INDEX "analysis_validation_execution_key" ON "analysis_validation" USING btree ("llm_execution_id");
--> statement-breakpoint
CREATE INDEX "cursor_request_package_idx" ON "cursor_analysis_request" USING btree ("analysis_package_id");
--> statement-breakpoint
CREATE UNIQUE INDEX "cursor_manifest_execution_key" ON "cursor_execution_manifest" USING btree ("llm_execution_id");
--> statement-breakpoint
CREATE INDEX "cursor_manifest_request_idx" ON "cursor_execution_manifest" USING btree ("request_id");
