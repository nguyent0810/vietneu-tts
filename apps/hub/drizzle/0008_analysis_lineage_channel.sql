-- Thứ tự BẮT BUỘC: bỏ khoá ngoại cũ -> tạo UNIQUE đích -> thêm khoá ngoại mới.
--
-- drizzle-kit sinh phần UNIQUE ở CUỐI, nên PostgreSQL từ chối với
-- "no unique constraint matching given keys" — khoá ngoại không thể tham chiếu
-- một unique chưa tồn tại. Đã sắp lại thủ công.

ALTER TABLE "analysis_package" DROP CONSTRAINT "analysis_package_run_workspace_fk";
--> statement-breakpoint
ALTER TABLE "analysis_quality" DROP CONSTRAINT "analysis_quality_run_workspace_fk";
--> statement-breakpoint
ALTER TABLE "anomaly" DROP CONSTRAINT "anomaly_run_workspace_fk";
--> statement-breakpoint
ALTER TABLE "cohort_summary" DROP CONSTRAINT "cohort_run_workspace_fk";
--> statement-breakpoint
ALTER TABLE "deterministic_observation" DROP CONSTRAINT "observation_run_workspace_fk";
--> statement-breakpoint
ALTER TABLE "feature_value" DROP CONSTRAINT "feature_value_run_workspace_fk";
--> statement-breakpoint
ALTER TABLE "analysis_run" ADD CONSTRAINT "analysis_run_id_workspace_channel_key" UNIQUE("id","workspace_id","channel_id");
--> statement-breakpoint
ALTER TABLE "analysis_package" ADD CONSTRAINT "analysis_package_run_workspace_fk" FOREIGN KEY ("analysis_run_id","workspace_id","channel_id") REFERENCES "public"."analysis_run"("id","workspace_id","channel_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "analysis_quality" ADD CONSTRAINT "analysis_quality_run_workspace_fk" FOREIGN KEY ("analysis_run_id","workspace_id","channel_id") REFERENCES "public"."analysis_run"("id","workspace_id","channel_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "anomaly" ADD CONSTRAINT "anomaly_run_workspace_fk" FOREIGN KEY ("analysis_run_id","workspace_id","channel_id") REFERENCES "public"."analysis_run"("id","workspace_id","channel_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "cohort_summary" ADD CONSTRAINT "cohort_run_workspace_fk" FOREIGN KEY ("analysis_run_id","workspace_id","channel_id") REFERENCES "public"."analysis_run"("id","workspace_id","channel_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "deterministic_observation" ADD CONSTRAINT "observation_run_workspace_fk" FOREIGN KEY ("analysis_run_id","workspace_id","channel_id") REFERENCES "public"."analysis_run"("id","workspace_id","channel_id") ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "feature_value" ADD CONSTRAINT "feature_value_run_workspace_fk" FOREIGN KEY ("analysis_run_id","workspace_id","channel_id") REFERENCES "public"."analysis_run"("id","workspace_id","channel_id") ON DELETE restrict ON UPDATE no action;
