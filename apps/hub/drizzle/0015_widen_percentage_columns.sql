ALTER TABLE "channel_daily_metric" ALTER COLUMN "average_view_percentage" SET DATA TYPE numeric(12, 4);--> statement-breakpoint
ALTER TABLE "channel_daily_metric" ALTER COLUMN "impression_ctr" SET DATA TYPE numeric(12, 4);--> statement-breakpoint
ALTER TABLE "video_daily_metric" ALTER COLUMN "average_view_percentage" SET DATA TYPE numeric(12, 4);--> statement-breakpoint
ALTER TABLE "video_daily_metric" ALTER COLUMN "impression_ctr" SET DATA TYPE numeric(12, 4);--> statement-breakpoint
ALTER TABLE "video_daily_metric_history" ALTER COLUMN "average_view_percentage" SET DATA TYPE numeric(12, 4);--> statement-breakpoint
ALTER TABLE "video_daily_metric_history" ALTER COLUMN "impression_ctr" SET DATA TYPE numeric(12, 4);