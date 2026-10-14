CREATE TYPE "public"."actor_type" AS ENUM('USER', 'WORKER', 'SYSTEM', 'AGENT');--> statement-breakpoint
CREATE TYPE "public"."algorithm_kind" AS ENUM('DETERMINISTIC', 'LLM', 'HYBRID', 'EXTERNAL');--> statement-breakpoint
CREATE TYPE "public"."analysis_result_kind" AS ENUM('DETERMINISTIC_EVIDENCE', 'LLM_ANALYSIS');--> statement-breakpoint
CREATE TYPE "public"."analysis_run_status" AS ENUM('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED');--> statement-breakpoint
CREATE TYPE "public"."analysis_subject_type" AS ENUM('CHANNEL', 'CONTENT_REVISION');--> statement-breakpoint
CREATE TYPE "public"."approval_state" AS ENUM('PENDING', 'APPROVED', 'REJECTED');--> statement-breakpoint
CREATE TYPE "public"."content_kind" AS ENUM('LONG_FORM', 'SHORT');--> statement-breakpoint
CREATE TYPE "public"."content_status" AS ENUM('DRAFT', 'IN_REVIEW', 'APPROVED', 'PRODUCTION_READY', 'PUBLISHED', 'ARCHIVED', 'REJECTED');--> statement-breakpoint
CREATE TYPE "public"."dimension_set" AS ENUM('CONTENT', 'ANALYSIS_RUBRIC');--> statement-breakpoint
CREATE TYPE "public"."evaluation_verdict" AS ENUM('ACCEPT', 'REVISE', 'REJECT');--> statement-breakpoint
CREATE TYPE "public"."evaluator" AS ENUM('DETERMINISTIC', 'CODEX', 'HUMAN');--> statement-breakpoint
CREATE TYPE "public"."llm_execution_status" AS ENUM('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'REJECTED_SCHEMA', 'TIMED_OUT');--> statement-breakpoint
CREATE TYPE "public"."llm_provider" AS ENUM('CURSOR_CLI', 'CODEX_CLI');--> statement-breakpoint
CREATE TYPE "public"."prompt_author" AS ENUM('HUMAN', 'CODEX', 'SYSTEM');--> statement-breakpoint
CREATE TYPE "public"."prompt_purpose" AS ENUM('ANALYSIS', 'CRITIQUE', 'REFINEMENT');--> statement-breakpoint
CREATE TYPE "public"."revision_state" AS ENUM('DRAFT', 'FROZEN');--> statement-breakpoint
CREATE TYPE "public"."sync_run_status" AS ENUM('RUNNING', 'SUCCEEDED', 'PARTIAL', 'FAILED');--> statement-breakpoint
CREATE TYPE "public"."token_scope" AS ENUM('READ', 'WRITE', 'APPROVE', 'ADMIN');--> statement-breakpoint
CREATE TYPE "public"."video_format" AS ENUM('LONG_FORM', 'SHORT', 'UNKNOWN');--> statement-breakpoint
CREATE TYPE "public"."worker_capability" AS ENUM('ANALYZE_CONTENT', 'SCORE_CONTENT', 'IMPROVE_CONTENT', 'SYNC_ANALYTICS', 'RUN_LLM_ANALYSIS');--> statement-breakpoint
CREATE TABLE "channel" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"label" text NOT NULL,
	"youtube_channel_id" text NOT NULL,
	"title" text NOT NULL,
	"reporting_timezone" text DEFAULT 'America/Los_Angeles' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "channel_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "channel_label_format" CHECK ("channel"."label" ~ '^[a-z][a-z0-9_]{1,62}$')
);
--> statement-breakpoint
CREATE TABLE "workspace" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "content_item" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"external_ref" text,
	"kind" "content_kind" NOT NULL,
	"title" text NOT NULL,
	"status" "content_status" DEFAULT 'DRAFT' NOT NULL,
	"published_video_id" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "content_item_id_workspace_key" UNIQUE("id","workspace_id")
);
--> statement-breakpoint
CREATE TABLE "content_revision" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"content_item_id" uuid NOT NULL,
	"workspace_id" uuid NOT NULL,
	"revision_number" integer NOT NULL,
	"state" "revision_state" DEFAULT 'DRAFT' NOT NULL,
	"audio_script" text NOT NULL,
	"seo" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"content_hash" text NOT NULL,
	"frozen_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "content_revision_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "content_revision_number_positive" CHECK ("content_revision"."revision_number" >= 1),
	CONSTRAINT "content_revision_hash_format" CHECK ("content_revision"."content_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "content_revision_frozen_consistency" CHECK (("content_revision"."state" = 'FROZEN') = ("content_revision"."frozen_at" IS NOT NULL))
);
--> statement-breakpoint
CREATE TABLE "algorithm" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"key" text NOT NULL,
	"name" text NOT NULL,
	"kind" "algorithm_kind" NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "algorithm_version" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"algorithm_id" uuid NOT NULL,
	"version" text NOT NULL,
	"spec" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"code_hash" text,
	"is_active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "analysis_result" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"kind" "analysis_result_kind" NOT NULL,
	"schema_version" text NOT NULL,
	"payload" jsonb NOT NULL,
	"payload_hash" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "analysis_result_id_run_key" UNIQUE("id","analysis_run_id"),
	CONSTRAINT "analysis_result_hash_format" CHECK ("analysis_result"."payload_hash" ~ '^[0-9a-f]{64}$')
);
--> statement-breakpoint
CREATE TABLE "analysis_run" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"subject_type" "analysis_subject_type" NOT NULL,
	"subject_id" uuid NOT NULL,
	"content_revision_id" uuid,
	"algorithm_id" uuid NOT NULL,
	"algorithm_version_id" uuid NOT NULL,
	"run_sequence" integer NOT NULL,
	"input_hash" text NOT NULL,
	"period_start" date NOT NULL,
	"period_end" date NOT NULL,
	"status" "analysis_run_status" DEFAULT 'PENDING' NOT NULL,
	"started_at" timestamp with time zone,
	"finished_at" timestamp with time zone,
	"error" jsonb,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "analysis_run_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "analysis_run_sequence_positive" CHECK ("analysis_run"."run_sequence" >= 1),
	CONSTRAINT "analysis_run_period_order" CHECK ("analysis_run"."period_end" >= "analysis_run"."period_start"),
	CONSTRAINT "analysis_run_input_hash_format" CHECK ("analysis_run"."input_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "analysis_run_subject_consistency" CHECK (("analysis_run"."subject_type" = 'CONTENT_REVISION') = ("analysis_run"."content_revision_id" IS NOT NULL))
);
--> statement-breakpoint
CREATE TABLE "evaluation" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"analysis_result_id" uuid NOT NULL,
	"rubric_version_id" uuid NOT NULL,
	"evaluator" "evaluator" NOT NULL,
	"total_score" numeric(8, 3),
	"verdict" "evaluation_verdict",
	"rationale" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "score" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"evaluation_id" uuid NOT NULL,
	"dimension_id" uuid NOT NULL,
	"value" numeric(6, 2) NOT NULL,
	"rationale" text,
	"evidence_refs" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "score_dimension" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"dimension_set" "dimension_set" NOT NULL,
	"key" text NOT NULL,
	"label" text NOT NULL,
	"description" text,
	"scale_min" numeric(6, 2) DEFAULT '0' NOT NULL,
	"scale_max" numeric(6, 2) DEFAULT '5' NOT NULL,
	"weight" numeric(6, 3) DEFAULT '1' NOT NULL,
	"sort_order" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "score_dimension_scale_order" CHECK ("score_dimension"."scale_max" > "score_dimension"."scale_min")
);
--> statement-breakpoint
CREATE TABLE "approval" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"entity_type" text NOT NULL,
	"entity_id" uuid NOT NULL,
	"state" "approval_state" DEFAULT 'PENDING' NOT NULL,
	"decided_by_type" "actor_type",
	"decided_by_id" text,
	"decided_at" timestamp with time zone,
	"reason" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "approval_decision_consistency" CHECK (("approval"."state" = 'PENDING') = ("approval"."decided_at" IS NULL AND "approval"."decided_by_type" IS NULL AND "approval"."decided_by_id" IS NULL)),
	CONSTRAINT "approval_decider_must_be_human" CHECK ("approval"."decided_by_type" IS NULL OR "approval"."decided_by_type" = 'USER')
);
--> statement-breakpoint
CREATE TABLE "audit_event" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"actor_type" "actor_type" NOT NULL,
	"actor_id" text NOT NULL,
	"action" text NOT NULL,
	"entity_type" text NOT NULL,
	"entity_id" uuid,
	"payload" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "prompt_revision" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"template_id" uuid NOT NULL,
	"workspace_id" uuid NOT NULL,
	"revision_number" integer NOT NULL,
	"body" text NOT NULL,
	"variables" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"content_hash" text NOT NULL,
	"authored_by" "prompt_author" NOT NULL,
	"parent_revision_id" uuid,
	"change_reason" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "prompt_revision_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "prompt_revision_number_positive" CHECK ("prompt_revision"."revision_number" >= 1),
	CONSTRAINT "prompt_revision_hash_format" CHECK ("prompt_revision"."content_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "prompt_revision_no_self_parent" CHECK ("prompt_revision"."parent_revision_id" IS DISTINCT FROM "prompt_revision"."id")
);
--> statement-breakpoint
CREATE TABLE "prompt_template" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"key" text NOT NULL,
	"purpose" "prompt_purpose" NOT NULL,
	"description" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "prompt_template_id_workspace_key" UNIQUE("id","workspace_id")
);
--> statement-breakpoint
CREATE TABLE "critique" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"llm_execution_id" uuid NOT NULL,
	"critiqued_prompt_revision_id" uuid NOT NULL,
	"proposed_prompt_revision_id" uuid,
	"findings" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"severity_summary" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"summary" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "llm_execution" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"prompt_revision_id" uuid NOT NULL,
	"provider" "llm_provider" NOT NULL,
	"model" text,
	"iteration" integer DEFAULT 1 NOT NULL,
	"status" "llm_execution_status" DEFAULT 'PENDING' NOT NULL,
	"raw_output_hash" text,
	"validation_error" jsonb,
	"analysis_result_id" uuid,
	"started_at" timestamp with time zone,
	"finished_at" timestamp with time zone,
	"duration_ms" integer,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "llm_execution_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "llm_execution_id_prompt_key" UNIQUE("id","prompt_revision_id"),
	CONSTRAINT "llm_execution_iteration_bounds" CHECK ("llm_execution"."iteration" >= 1 AND "llm_execution"."iteration" <= 3),
	CONSTRAINT "llm_execution_output_hash_format" CHECK ("llm_execution"."raw_output_hash" IS NULL OR "llm_execution"."raw_output_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "llm_execution_succeeded_has_result" CHECK ("llm_execution"."status" <> 'SUCCEEDED' OR "llm_execution"."analysis_result_id" IS NOT NULL),
	CONSTRAINT "llm_execution_rejected_has_error" CHECK ("llm_execution"."status" <> 'REJECTED_SCHEMA' OR "llm_execution"."validation_error" IS NOT NULL)
);
--> statement-breakpoint
CREATE TABLE "rate_limit_bucket" (
	"key" text PRIMARY KEY NOT NULL,
	"tokens" numeric(12, 4) NOT NULL,
	"refill_rate" numeric(12, 4) NOT NULL,
	"capacity" numeric(12, 4) NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "rate_limit_tokens_nonneg" CHECK ("rate_limit_bucket"."tokens" >= 0),
	CONSTRAINT "rate_limit_capacity_positive" CHECK ("rate_limit_bucket"."capacity" > 0),
	CONSTRAINT "rate_limit_refill_positive" CHECK ("rate_limit_bucket"."refill_rate" > 0)
);
--> statement-breakpoint
CREATE TABLE "user_account" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"email" text NOT NULL,
	"display_name" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"disabled_at" timestamp with time zone
);
--> statement-breakpoint
CREATE TABLE "user_api_token" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"label" text NOT NULL,
	"token_hash" text NOT NULL,
	"token_prefix" text NOT NULL,
	"scopes" "token_scope"[] NOT NULL,
	"expires_at" timestamp with time zone,
	"revoked_at" timestamp with time zone,
	"last_used_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "user_api_token_hash_format" CHECK ("user_api_token"."token_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "user_api_token_scopes_nonempty" CHECK (array_length("user_api_token"."scopes", 1) >= 1)
);
--> statement-breakpoint
CREATE TABLE "worker_machine" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"machine_label" text NOT NULL,
	"token_hash" text NOT NULL,
	"token_prefix" text NOT NULL,
	"capabilities" "worker_capability"[] NOT NULL,
	"last_seen_at" timestamp with time zone,
	"revoked_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "worker_machine_hash_format" CHECK ("worker_machine"."token_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "worker_machine_capabilities_nonempty" CHECK (array_length("worker_machine"."capabilities", 1) >= 1)
);
--> statement-breakpoint
ALTER TABLE "channel" ADD CONSTRAINT "channel_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "content_item" ADD CONSTRAINT "content_item_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "content_item" ADD CONSTRAINT "content_item_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "content_revision" ADD CONSTRAINT "content_revision_item_workspace_fk" FOREIGN KEY ("content_item_id","workspace_id") REFERENCES "public"."content_item"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "algorithm_version" ADD CONSTRAINT "algorithm_version_algorithm_id_algorithm_id_fk" FOREIGN KEY ("algorithm_id") REFERENCES "public"."algorithm"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_result" ADD CONSTRAINT "analysis_result_analysis_run_id_analysis_run_id_fk" FOREIGN KEY ("analysis_run_id") REFERENCES "public"."analysis_run"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_run" ADD CONSTRAINT "analysis_run_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_run" ADD CONSTRAINT "analysis_run_algorithm_id_algorithm_id_fk" FOREIGN KEY ("algorithm_id") REFERENCES "public"."algorithm"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_run" ADD CONSTRAINT "analysis_run_algorithm_version_id_algorithm_version_id_fk" FOREIGN KEY ("algorithm_version_id") REFERENCES "public"."algorithm_version"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_run" ADD CONSTRAINT "analysis_run_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_run" ADD CONSTRAINT "analysis_run_revision_workspace_fk" FOREIGN KEY ("content_revision_id","workspace_id") REFERENCES "public"."content_revision"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evaluation" ADD CONSTRAINT "evaluation_analysis_result_id_analysis_result_id_fk" FOREIGN KEY ("analysis_result_id") REFERENCES "public"."analysis_result"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evaluation" ADD CONSTRAINT "evaluation_rubric_version_id_algorithm_version_id_fk" FOREIGN KEY ("rubric_version_id") REFERENCES "public"."algorithm_version"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "score" ADD CONSTRAINT "score_evaluation_id_evaluation_id_fk" FOREIGN KEY ("evaluation_id") REFERENCES "public"."evaluation"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "score" ADD CONSTRAINT "score_dimension_id_score_dimension_id_fk" FOREIGN KEY ("dimension_id") REFERENCES "public"."score_dimension"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "approval" ADD CONSTRAINT "approval_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "audit_event" ADD CONSTRAINT "audit_event_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prompt_revision" ADD CONSTRAINT "prompt_revision_template_workspace_fk" FOREIGN KEY ("template_id","workspace_id") REFERENCES "public"."prompt_template"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prompt_template" ADD CONSTRAINT "prompt_template_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "critique" ADD CONSTRAINT "critique_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "critique" ADD CONSTRAINT "critique_execution_workspace_fk" FOREIGN KEY ("llm_execution_id","workspace_id") REFERENCES "public"."llm_execution"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "critique" ADD CONSTRAINT "critique_execution_prompt_fk" FOREIGN KEY ("llm_execution_id","critiqued_prompt_revision_id") REFERENCES "public"."llm_execution"("id","prompt_revision_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "critique" ADD CONSTRAINT "critique_proposed_prompt_workspace_fk" FOREIGN KEY ("proposed_prompt_revision_id","workspace_id") REFERENCES "public"."prompt_revision"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "llm_execution" ADD CONSTRAINT "llm_execution_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "llm_execution" ADD CONSTRAINT "llm_execution_run_workspace_fk" FOREIGN KEY ("analysis_run_id","workspace_id") REFERENCES "public"."analysis_run"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "llm_execution" ADD CONSTRAINT "llm_execution_prompt_workspace_fk" FOREIGN KEY ("prompt_revision_id","workspace_id") REFERENCES "public"."prompt_revision"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "llm_execution" ADD CONSTRAINT "llm_execution_result_run_fk" FOREIGN KEY ("analysis_result_id","analysis_run_id") REFERENCES "public"."analysis_result"("id","analysis_run_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_account" ADD CONSTRAINT "user_account_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_api_token" ADD CONSTRAINT "user_api_token_user_id_user_account_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user_account"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "worker_machine" ADD CONSTRAINT "worker_machine_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "channel_youtube_id_key" ON "channel" USING btree ("youtube_channel_id");--> statement-breakpoint
CREATE UNIQUE INDEX "channel_workspace_label_key" ON "channel" USING btree ("workspace_id","label");--> statement-breakpoint
CREATE INDEX "channel_workspace_idx" ON "channel" USING btree ("workspace_id");--> statement-breakpoint
CREATE UNIQUE INDEX "workspace_slug_key" ON "workspace" USING btree ("slug");--> statement-breakpoint
CREATE INDEX "content_item_workspace_idx" ON "content_item" USING btree ("workspace_id");--> statement-breakpoint
CREATE INDEX "content_item_channel_idx" ON "content_item" USING btree ("channel_id");--> statement-breakpoint
CREATE UNIQUE INDEX "content_item_external_ref_key" ON "content_item" USING btree ("workspace_id","external_ref") WHERE "content_item"."external_ref" IS NOT NULL;--> statement-breakpoint
CREATE UNIQUE INDEX "content_revision_item_number_key" ON "content_revision" USING btree ("content_item_id","revision_number");--> statement-breakpoint
CREATE INDEX "content_revision_item_idx" ON "content_revision" USING btree ("content_item_id");--> statement-breakpoint
CREATE UNIQUE INDEX "algorithm_key_key" ON "algorithm" USING btree ("key");--> statement-breakpoint
CREATE UNIQUE INDEX "algorithm_version_algo_version_key" ON "algorithm_version" USING btree ("algorithm_id","version");--> statement-breakpoint
CREATE INDEX "algorithm_version_algo_idx" ON "algorithm_version" USING btree ("algorithm_id");--> statement-breakpoint
CREATE UNIQUE INDEX "analysis_result_run_kind_key" ON "analysis_result" USING btree ("analysis_run_id","kind");--> statement-breakpoint
CREATE INDEX "analysis_result_run_idx" ON "analysis_result" USING btree ("analysis_run_id");--> statement-breakpoint
CREATE UNIQUE INDEX "analysis_run_sequence_key" ON "analysis_run" USING btree ("subject_type","subject_id","algorithm_version_id","run_sequence");--> statement-breakpoint
CREATE INDEX "analysis_run_workspace_idx" ON "analysis_run" USING btree ("workspace_id");--> statement-breakpoint
CREATE INDEX "analysis_run_channel_idx" ON "analysis_run" USING btree ("channel_id");--> statement-breakpoint
CREATE INDEX "analysis_run_subject_idx" ON "analysis_run" USING btree ("subject_type","subject_id");--> statement-breakpoint
CREATE UNIQUE INDEX "evaluation_result_rubric_evaluator_key" ON "evaluation" USING btree ("analysis_result_id","rubric_version_id","evaluator");--> statement-breakpoint
CREATE INDEX "evaluation_result_idx" ON "evaluation" USING btree ("analysis_result_id");--> statement-breakpoint
CREATE UNIQUE INDEX "score_evaluation_dimension_key" ON "score" USING btree ("evaluation_id","dimension_id");--> statement-breakpoint
CREATE INDEX "score_evaluation_idx" ON "score" USING btree ("evaluation_id");--> statement-breakpoint
CREATE UNIQUE INDEX "score_dimension_set_key_key" ON "score_dimension" USING btree ("dimension_set","key");--> statement-breakpoint
CREATE UNIQUE INDEX "approval_entity_key" ON "approval" USING btree ("entity_type","entity_id");--> statement-breakpoint
CREATE INDEX "approval_workspace_state_idx" ON "approval" USING btree ("workspace_id","state");--> statement-breakpoint
CREATE INDEX "audit_event_workspace_created_idx" ON "audit_event" USING btree ("workspace_id","created_at");--> statement-breakpoint
CREATE INDEX "audit_event_entity_idx" ON "audit_event" USING btree ("entity_type","entity_id");--> statement-breakpoint
CREATE UNIQUE INDEX "prompt_revision_template_number_key" ON "prompt_revision" USING btree ("template_id","revision_number");--> statement-breakpoint
CREATE INDEX "prompt_revision_template_idx" ON "prompt_revision" USING btree ("template_id");--> statement-breakpoint
CREATE INDEX "prompt_revision_parent_idx" ON "prompt_revision" USING btree ("parent_revision_id");--> statement-breakpoint
CREATE UNIQUE INDEX "prompt_template_workspace_key_key" ON "prompt_template" USING btree ("workspace_id","key");--> statement-breakpoint
CREATE UNIQUE INDEX "critique_execution_key" ON "critique" USING btree ("llm_execution_id");--> statement-breakpoint
CREATE INDEX "critique_workspace_idx" ON "critique" USING btree ("workspace_id");--> statement-breakpoint
CREATE UNIQUE INDEX "llm_execution_run_provider_iteration_key" ON "llm_execution" USING btree ("analysis_run_id","provider","iteration");--> statement-breakpoint
CREATE INDEX "llm_execution_run_idx" ON "llm_execution" USING btree ("analysis_run_id");--> statement-breakpoint
CREATE INDEX "llm_execution_prompt_idx" ON "llm_execution" USING btree ("prompt_revision_id");--> statement-breakpoint
CREATE UNIQUE INDEX "user_account_email_key" ON "user_account" USING btree ("email");--> statement-breakpoint
CREATE UNIQUE INDEX "user_api_token_hash_key" ON "user_api_token" USING btree ("token_hash");--> statement-breakpoint
CREATE INDEX "user_api_token_user_idx" ON "user_api_token" USING btree ("user_id");--> statement-breakpoint
CREATE UNIQUE INDEX "worker_machine_token_hash_key" ON "worker_machine" USING btree ("token_hash");--> statement-breakpoint
CREATE UNIQUE INDEX "worker_machine_workspace_label_key" ON "worker_machine" USING btree ("workspace_id","machine_label");