CREATE TYPE "public"."anomaly_kind" AS ENUM('VIEW_SPIKE', 'VIEW_COLLAPSE', 'RETENTION_OUTLIER', 'CTR_OUTLIER', 'ENGAGEMENT_OUTLIER', 'INCONSISTENT_VALUE', 'SUSPICIOUS_VALUE');--> statement-breakpoint
CREATE TYPE "public"."baseline_kind" AS ENUM('CHANNEL_ALL', 'CHANNEL_FORMAT', 'RECENT_WINDOW', 'MATURE_VIDEOS', 'COHORT', 'NONE');--> statement-breakpoint
CREATE TYPE "public"."cohort_kind" AS ENUM('PUBLISH_FORTNIGHT', 'FORMAT', 'DURATION_BUCKET', 'PUBLISH_HOUR_BUCKET', 'PUBLISH_WEEKDAY');--> statement-breakpoint
CREATE TYPE "public"."confidence_band" AS ENUM('HIGH', 'MEDIUM', 'LOW');--> statement-breakpoint
CREATE TYPE "public"."feature_direction" AS ENUM('HIGHER_IS_BETTER', 'LOWER_IS_BETTER', 'NEUTRAL');--> statement-breakpoint
CREATE TYPE "public"."feature_subject_type" AS ENUM('CHANNEL', 'VIDEO');--> statement-breakpoint
CREATE TYPE "public"."feature_unit" AS ENUM('COUNT', 'RATIO', 'PERCENT', 'SECONDS', 'MINUTES', 'PER_DAY', 'ZSCORE', 'RANK', 'HOUR_OF_DAY', 'DAY_OF_WEEK');--> statement-breakpoint
CREATE TYPE "public"."missing_reason" AS ENUM('METRIC_NOT_PROVIDED', 'INSUFFICIENT_AGE', 'INSUFFICIENT_SAMPLE', 'NO_METRIC_ROWS', 'DIVISION_BY_ZERO', 'DEPENDENCY_MISSING', 'OUTSIDE_WINDOW');--> statement-breakpoint
CREATE TYPE "public"."observation_kind" AS ENUM('TOP_PERFORMER', 'BOTTOM_PERFORMER', 'HIGH_RETENTION_LOW_REACH', 'HIGH_REACH_LOW_RETENTION', 'HIGH_CTR_LOW_WATCH', 'LOW_CTR_HIGH_RETENTION', 'SUBSCRIBER_EFFICIENT', 'COHORT_TREND', 'FORMAT_COMPARISON', 'PUBLISH_TIME_COMPARISON', 'CHANNEL_TREND_CHANGE', 'ANOMALY', 'DATA_QUALITY', 'HYPOTHESIS_CANDIDATE');--> statement-breakpoint
CREATE TYPE "public"."observation_polarity" AS ENUM('POSITIVE', 'NEGATIVE', 'NEUTRAL');--> statement-breakpoint
CREATE TABLE "analysis_package" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"schema_version" text NOT NULL,
	"payload" jsonb NOT NULL,
	"payload_hash" text NOT NULL,
	"package_bytes" integer NOT NULL,
	"raw_input_bytes" integer NOT NULL,
	"reduction_percent" numeric(6, 3) NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "analysis_package_hash_format" CHECK ("analysis_package"."payload_hash" ~ '^[0-9a-f]{64}$'),
	CONSTRAINT "analysis_package_bytes_positive" CHECK ("analysis_package"."package_bytes" > 0 AND "analysis_package"."raw_input_bytes" > 0)
);
--> statement-breakpoint
CREATE TABLE "analysis_quality" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"videos_total" integer NOT NULL,
	"videos_with_metrics" integer NOT NULL,
	"videos_immature" integer NOT NULL,
	"metric_rows" integer NOT NULL,
	"expected_dates" integer NOT NULL,
	"observed_dates" integer NOT NULL,
	"missing_dates" text[] DEFAULT ARRAY[]::text[] NOT NULL,
	"metric_coverage" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"revised_rows" integer DEFAULT 0 NOT NULL,
	"has_sync_gaps" boolean DEFAULT false NOT NULL,
	"confidence" numeric(5, 4) NOT NULL,
	"confidence_band" "confidence_band" NOT NULL,
	"limitations" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "analysis_quality_confidence_range" CHECK ("analysis_quality"."confidence" >= 0 AND "analysis_quality"."confidence" <= 1)
);
--> statement-breakpoint
CREATE TABLE "anomaly" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"video_id" uuid,
	"kind" "anomaly_kind" NOT NULL,
	"method" text NOT NULL,
	"score" numeric(12, 6) NOT NULL,
	"threshold" numeric(12, 6) NOT NULL,
	"observed_value" numeric(20, 6) NOT NULL,
	"median_value" numeric(20, 6) NOT NULL,
	"mad_value" numeric(20, 6),
	"sample_size" integer NOT NULL,
	"metric_key" text NOT NULL,
	"context" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"window_start" date NOT NULL,
	"window_end" date NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "anomaly_sample_size_min" CHECK ("anomaly"."sample_size" >= 0)
);
--> statement-breakpoint
CREATE TABLE "cohort_summary" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"kind" "cohort_kind" NOT NULL,
	"cohort_key" text NOT NULL,
	"video_count" integer NOT NULL,
	"median_views" numeric(20, 4),
	"p25_views" numeric(20, 4),
	"p75_views" numeric(20, 4),
	"median_avg_view_percentage" numeric(10, 4),
	"median_avg_view_duration" numeric(12, 3),
	"median_engagement_rate" numeric(12, 6),
	"median_subs_per_thousand_views" numeric(12, 6),
	"window_start" date NOT NULL,
	"window_end" date NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "cohort_video_count_positive" CHECK ("cohort_summary"."video_count" >= 0)
);
--> statement-breakpoint
CREATE TABLE "deterministic_observation" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"kind" "observation_kind" NOT NULL,
	"polarity" "observation_polarity" DEFAULT 'NEUTRAL' NOT NULL,
	"channel_id" uuid NOT NULL,
	"video_id" uuid,
	"statement" text NOT NULL,
	"metric_values" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"baseline_kind" "baseline_kind" DEFAULT 'NONE' NOT NULL,
	"baseline_value" numeric(20, 6),
	"observed_value" numeric(20, 6),
	"delta_ratio" numeric(12, 6),
	"percentile" numeric(6, 3),
	"window_start" date NOT NULL,
	"window_end" date NOT NULL,
	"confidence" numeric(5, 4) NOT NULL,
	"confidence_band" "confidence_band" NOT NULL,
	"sample_size" integer,
	"limitations" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"is_hypothesis" boolean DEFAULT false NOT NULL,
	"hypothesis_question" text,
	"rank_score" numeric(12, 6) DEFAULT '0' NOT NULL,
	"order_key" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "observation_confidence_range" CHECK ("deterministic_observation"."confidence" >= 0 AND "deterministic_observation"."confidence" <= 1),
	CONSTRAINT "observation_percentile_range" CHECK ("deterministic_observation"."percentile" IS NULL OR ("deterministic_observation"."percentile" >= 0 AND "deterministic_observation"."percentile" <= 100)),
	CONSTRAINT "observation_window_order" CHECK ("deterministic_observation"."window_end" >= "deterministic_observation"."window_start"),
	CONSTRAINT "observation_hypothesis_needs_question" CHECK ("deterministic_observation"."is_hypothesis" = false OR "deterministic_observation"."hypothesis_question" IS NOT NULL)
);
--> statement-breakpoint
CREATE TABLE "evidence_reference" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"observation_id" uuid NOT NULL,
	"ref_type" text NOT NULL,
	"ref_id" uuid,
	"ref_key" text,
	"detail" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "evidence_has_target" CHECK ("evidence_reference"."ref_id" IS NOT NULL OR "evidence_reference"."ref_key" IS NOT NULL)
);
--> statement-breakpoint
CREATE TABLE "feature_definition" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"key" text NOT NULL,
	"label" text NOT NULL,
	"description" text NOT NULL,
	"unit" "feature_unit" NOT NULL,
	"direction" "feature_direction" DEFAULT 'NEUTRAL' NOT NULL,
	"subject_type" "feature_subject_type" NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "feature_definition_key_format" CHECK ("feature_definition"."key" ~ '^[a-z][a-z0-9_]{2,63}$')
);
--> statement-breakpoint
CREATE TABLE "feature_value" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"analysis_run_id" uuid NOT NULL,
	"feature_version_id" uuid NOT NULL,
	"subject_type" "feature_subject_type" NOT NULL,
	"channel_id" uuid NOT NULL,
	"video_id" uuid,
	"window_start" date NOT NULL,
	"window_end" date NOT NULL,
	"numeric_value" numeric(20, 6),
	"missing_reason" "missing_reason",
	"sample_size" integer,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "feature_value_exactly_one_of_value_or_reason" CHECK (("feature_value"."numeric_value" IS NULL) <> ("feature_value"."missing_reason" IS NULL)),
	CONSTRAINT "feature_value_subject_consistency" CHECK (("feature_value"."subject_type" = 'VIDEO') = ("feature_value"."video_id" IS NOT NULL)),
	CONSTRAINT "feature_value_window_order" CHECK ("feature_value"."window_end" >= "feature_value"."window_start"),
	CONSTRAINT "feature_value_sample_nonneg" CHECK ("feature_value"."sample_size" IS NULL OR "feature_value"."sample_size" >= 0)
);
--> statement-breakpoint
CREATE TABLE "feature_version" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"definition_id" uuid NOT NULL,
	"version" text NOT NULL,
	"formula" text NOT NULL,
	"spec" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"required_metrics" text[] DEFAULT ARRAY[]::text[] NOT NULL,
	"code_hash" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "feature_version_id_def_key" UNIQUE("id","definition_id")
);
--> statement-breakpoint
ALTER TABLE "analysis_package" ADD CONSTRAINT "analysis_package_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_package" ADD CONSTRAINT "analysis_package_analysis_run_id_analysis_run_id_fk" FOREIGN KEY ("analysis_run_id") REFERENCES "public"."analysis_run"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_package" ADD CONSTRAINT "analysis_package_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_quality" ADD CONSTRAINT "analysis_quality_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_quality" ADD CONSTRAINT "analysis_quality_analysis_run_id_analysis_run_id_fk" FOREIGN KEY ("analysis_run_id") REFERENCES "public"."analysis_run"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_quality" ADD CONSTRAINT "analysis_quality_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "anomaly" ADD CONSTRAINT "anomaly_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "anomaly" ADD CONSTRAINT "anomaly_analysis_run_id_analysis_run_id_fk" FOREIGN KEY ("analysis_run_id") REFERENCES "public"."analysis_run"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "anomaly" ADD CONSTRAINT "anomaly_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "anomaly" ADD CONSTRAINT "anomaly_video_workspace_fk" FOREIGN KEY ("video_id","workspace_id") REFERENCES "public"."video"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "cohort_summary" ADD CONSTRAINT "cohort_summary_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "cohort_summary" ADD CONSTRAINT "cohort_summary_analysis_run_id_analysis_run_id_fk" FOREIGN KEY ("analysis_run_id") REFERENCES "public"."analysis_run"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "cohort_summary" ADD CONSTRAINT "cohort_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "deterministic_observation" ADD CONSTRAINT "deterministic_observation_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "deterministic_observation" ADD CONSTRAINT "deterministic_observation_analysis_run_id_analysis_run_id_fk" FOREIGN KEY ("analysis_run_id") REFERENCES "public"."analysis_run"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "deterministic_observation" ADD CONSTRAINT "observation_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "deterministic_observation" ADD CONSTRAINT "observation_video_workspace_fk" FOREIGN KEY ("video_id","workspace_id") REFERENCES "public"."video"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evidence_reference" ADD CONSTRAINT "evidence_reference_observation_id_deterministic_observation_id_fk" FOREIGN KEY ("observation_id") REFERENCES "public"."deterministic_observation"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feature_value" ADD CONSTRAINT "feature_value_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feature_value" ADD CONSTRAINT "feature_value_analysis_run_id_analysis_run_id_fk" FOREIGN KEY ("analysis_run_id") REFERENCES "public"."analysis_run"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feature_value" ADD CONSTRAINT "feature_value_feature_version_id_feature_version_id_fk" FOREIGN KEY ("feature_version_id") REFERENCES "public"."feature_version"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feature_value" ADD CONSTRAINT "feature_value_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feature_value" ADD CONSTRAINT "feature_value_video_workspace_fk" FOREIGN KEY ("video_id","workspace_id") REFERENCES "public"."video"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feature_version" ADD CONSTRAINT "feature_version_definition_id_feature_definition_id_fk" FOREIGN KEY ("definition_id") REFERENCES "public"."feature_definition"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "analysis_package_run_channel_key" ON "analysis_package" USING btree ("analysis_run_id","channel_id");--> statement-breakpoint
CREATE UNIQUE INDEX "analysis_quality_run_channel_key" ON "analysis_quality" USING btree ("analysis_run_id","channel_id");--> statement-breakpoint
CREATE INDEX "anomaly_run_idx" ON "anomaly" USING btree ("analysis_run_id");--> statement-breakpoint
CREATE UNIQUE INDEX "cohort_run_channel_kind_key" ON "cohort_summary" USING btree ("analysis_run_id","channel_id","kind","cohort_key");--> statement-breakpoint
CREATE UNIQUE INDEX "observation_run_order_key" ON "deterministic_observation" USING btree ("analysis_run_id","order_key");--> statement-breakpoint
CREATE INDEX "observation_run_kind_idx" ON "deterministic_observation" USING btree ("analysis_run_id","kind");--> statement-breakpoint
CREATE INDEX "evidence_observation_idx" ON "evidence_reference" USING btree ("observation_id");--> statement-breakpoint
CREATE UNIQUE INDEX "feature_definition_key_key" ON "feature_definition" USING btree ("key");--> statement-breakpoint
CREATE UNIQUE INDEX "feature_value_run_feature_subject_key" ON "feature_value" USING btree ("analysis_run_id","feature_version_id","subject_type","channel_id","video_id");--> statement-breakpoint
CREATE INDEX "feature_value_run_idx" ON "feature_value" USING btree ("analysis_run_id");--> statement-breakpoint
CREATE INDEX "feature_value_feature_idx" ON "feature_value" USING btree ("feature_version_id");--> statement-breakpoint
CREATE UNIQUE INDEX "feature_version_def_version_key" ON "feature_version" USING btree ("definition_id","version");