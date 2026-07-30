CREATE TABLE "analytics_api_call" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sync_run_id" uuid NOT NULL,
	"endpoint" text NOT NULL,
	"request_params" jsonb NOT NULL,
	"http_status" integer,
	"row_count" integer,
	"response_hash" text,
	"column_headers" jsonb,
	"duration_ms" integer,
	"fetched_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "analytics_api_call_hash_format" CHECK ("analytics_api_call"."response_hash" IS NULL OR "analytics_api_call"."response_hash" ~ '^[0-9a-f]{64}$')
);
--> statement-breakpoint
CREATE TABLE "channel_daily_metric" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"date" date NOT NULL,
	"views" bigint,
	"estimated_minutes_watched" numeric(16, 4),
	"average_view_duration_seconds" numeric(12, 3),
	"average_view_percentage" numeric(8, 4),
	"impressions" bigint,
	"impression_ctr" numeric(8, 4),
	"likes" integer,
	"dislikes" integer,
	"comments" integer,
	"shares" integer,
	"subscribers_gained" integer,
	"subscribers_lost" integer,
	"last_sync_run_id" uuid,
	"revision_count" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "channel_daily_metric_views_nonneg" CHECK ("channel_daily_metric"."views" IS NULL OR "channel_daily_metric"."views" >= 0)
);
--> statement-breakpoint
CREATE TABLE "sync_checkpoint" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"last_complete_date" date,
	"last_sync_run_id" uuid,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sync_run" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"status" "sync_run_status" DEFAULT 'RUNNING' NOT NULL,
	"requested_from" date NOT NULL,
	"requested_to" date NOT NULL,
	"worker_label" text,
	"videos_seen" integer DEFAULT 0 NOT NULL,
	"videos_upserted" integer DEFAULT 0 NOT NULL,
	"video_metric_rows_upserted" integer DEFAULT 0 NOT NULL,
	"channel_metric_rows_upserted" integer DEFAULT 0 NOT NULL,
	"metric_rows_revised" integer DEFAULT 0 NOT NULL,
	"warnings" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"error" jsonb,
	"started_at" timestamp with time zone DEFAULT now() NOT NULL,
	"finished_at" timestamp with time zone,
	CONSTRAINT "sync_run_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "sync_run_range_order" CHECK ("sync_run"."requested_to" >= "sync_run"."requested_from"),
	CONSTRAINT "sync_run_finished_consistency" CHECK (("sync_run"."status" = 'RUNNING') = ("sync_run"."finished_at" IS NULL)),
	CONSTRAINT "sync_run_failed_has_error" CHECK ("sync_run"."status" <> 'FAILED' OR "sync_run"."error" IS NOT NULL)
);
--> statement-breakpoint
CREATE TABLE "video" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"channel_id" uuid NOT NULL,
	"youtube_video_id" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"published_at" timestamp with time zone NOT NULL,
	"duration_seconds" integer,
	"format" "video_format" DEFAULT 'UNKNOWN' NOT NULL,
	"privacy_status" text,
	"published_hour_local" integer,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "video_id_workspace_key" UNIQUE("id","workspace_id"),
	CONSTRAINT "video_youtube_id_format" CHECK ("video"."youtube_video_id" ~ '^[A-Za-z0-9_-]{11}$'),
	CONSTRAINT "video_duration_nonneg" CHECK ("video"."duration_seconds" IS NULL OR "video"."duration_seconds" >= 0),
	CONSTRAINT "video_hour_range" CHECK ("video"."published_hour_local" IS NULL OR ("video"."published_hour_local" >= 0 AND "video"."published_hour_local" <= 23))
);
--> statement-breakpoint
CREATE TABLE "video_daily_metric" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"workspace_id" uuid NOT NULL,
	"video_id" uuid NOT NULL,
	"date" date NOT NULL,
	"views" bigint,
	"estimated_minutes_watched" numeric(16, 4),
	"average_view_duration_seconds" numeric(12, 3),
	"average_view_percentage" numeric(8, 4),
	"impressions" bigint,
	"impression_ctr" numeric(8, 4),
	"likes" integer,
	"dislikes" integer,
	"comments" integer,
	"shares" integer,
	"subscribers_gained" integer,
	"subscribers_lost" integer,
	"last_sync_run_id" uuid,
	"revision_count" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "video_daily_metric_views_nonneg" CHECK ("video_daily_metric"."views" IS NULL OR "video_daily_metric"."views" >= 0),
	CONSTRAINT "video_daily_metric_ctr_range" CHECK ("video_daily_metric"."impression_ctr" IS NULL OR ("video_daily_metric"."impression_ctr" >= 0 AND "video_daily_metric"."impression_ctr" <= 100)),
	CONSTRAINT "video_daily_metric_pct_range" CHECK ("video_daily_metric"."average_view_percentage" IS NULL OR ("video_daily_metric"."average_view_percentage" >= 0 AND "video_daily_metric"."average_view_percentage" <= 100))
);
--> statement-breakpoint
CREATE TABLE "video_daily_metric_history" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"metric_id" uuid NOT NULL,
	"video_id" uuid NOT NULL,
	"date" date NOT NULL,
	"views" bigint,
	"estimated_minutes_watched" numeric(16, 4),
	"average_view_duration_seconds" numeric(12, 3),
	"average_view_percentage" numeric(8, 4),
	"impressions" bigint,
	"impression_ctr" numeric(8, 4),
	"likes" integer,
	"dislikes" integer,
	"comments" integer,
	"shares" integer,
	"subscribers_gained" integer,
	"subscribers_lost" integer,
	"superseded_sync_run_id" uuid,
	"superseded_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "channel_daily_metric" ADD CONSTRAINT "channel_daily_metric_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "channel_daily_metric" ADD CONSTRAINT "channel_daily_metric_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sync_checkpoint" ADD CONSTRAINT "sync_checkpoint_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sync_checkpoint" ADD CONSTRAINT "sync_checkpoint_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sync_run" ADD CONSTRAINT "sync_run_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sync_run" ADD CONSTRAINT "sync_run_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "video" ADD CONSTRAINT "video_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "video" ADD CONSTRAINT "video_channel_workspace_fk" FOREIGN KEY ("channel_id","workspace_id") REFERENCES "public"."channel"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "video_daily_metric" ADD CONSTRAINT "video_daily_metric_workspace_id_workspace_id_fk" FOREIGN KEY ("workspace_id") REFERENCES "public"."workspace"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "video_daily_metric" ADD CONSTRAINT "video_daily_metric_video_workspace_fk" FOREIGN KEY ("video_id","workspace_id") REFERENCES "public"."video"("id","workspace_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "analytics_api_call_sync_run_idx" ON "analytics_api_call" USING btree ("sync_run_id");--> statement-breakpoint
CREATE UNIQUE INDEX "channel_daily_metric_channel_date_key" ON "channel_daily_metric" USING btree ("channel_id","date");--> statement-breakpoint
CREATE INDEX "channel_daily_metric_date_idx" ON "channel_daily_metric" USING btree ("date");--> statement-breakpoint
CREATE UNIQUE INDEX "sync_checkpoint_channel_key" ON "sync_checkpoint" USING btree ("channel_id");--> statement-breakpoint
CREATE INDEX "sync_run_channel_started_idx" ON "sync_run" USING btree ("channel_id","started_at");--> statement-breakpoint
CREATE UNIQUE INDEX "video_youtube_id_key" ON "video" USING btree ("youtube_video_id");--> statement-breakpoint
CREATE INDEX "video_channel_published_idx" ON "video" USING btree ("channel_id","published_at");--> statement-breakpoint
CREATE UNIQUE INDEX "video_daily_metric_video_date_key" ON "video_daily_metric" USING btree ("video_id","date");--> statement-breakpoint
CREATE INDEX "video_daily_metric_date_idx" ON "video_daily_metric" USING btree ("date");--> statement-breakpoint
CREATE INDEX "video_daily_metric_history_metric_idx" ON "video_daily_metric_history" USING btree ("metric_id");--> statement-breakpoint
CREATE INDEX "video_daily_metric_history_video_date_idx" ON "video_daily_metric_history" USING btree ("video_id","date");--> statement-breakpoint
ALTER TABLE "content_item" ADD CONSTRAINT "content_item_published_video_id_video_youtube_video_id_fk" FOREIGN KEY ("published_video_id") REFERENCES "public"."video"("youtube_video_id") ON DELETE restrict ON UPDATE no action;