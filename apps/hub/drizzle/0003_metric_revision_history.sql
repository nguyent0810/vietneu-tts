-- Lịch sử SCD-2 cho chỉ số theo ngày.
--
-- YouTube sửa lại số liệu trong 48-72h sau khi công bố. Nếu chỉ UPSERT đè lên
-- thì một phân tích chạy hôm qua không còn tái lập được: con số nó đã đọc đã
-- biến mất khỏi database, và không có cách nào biết nó từng là bao nhiêu.
--
-- Trigger ghi GIÁ TRỊ CŨ vào bảng history mỗi khi có chỉ số thay đổi thật sự.
-- Đặt ở tầng DB chứ không ở tầng ứng dụng: đường ghi nào cũng phải sinh lịch
-- sử, kể cả khi sau này thêm một route mới hoặc chạy tay một câu UPDATE.
--
-- `IS DISTINCT FROM` (không phải `<>`) là bắt buộc: mọi cột chỉ số đều
-- nullable, và `NULL <> NULL` cho ra NULL chứ không phải TRUE, nên dùng `<>`
-- sẽ bỏ sót đúng những lần chuyển đổi có-dữ-liệu <-> không-có-dữ-liệu.

CREATE OR REPLACE FUNCTION record_video_metric_revision()
RETURNS TRIGGER AS $$
BEGIN
  IF (
    NEW.views                          IS DISTINCT FROM OLD.views
    OR NEW.estimated_minutes_watched    IS DISTINCT FROM OLD.estimated_minutes_watched
    OR NEW.average_view_duration_seconds IS DISTINCT FROM OLD.average_view_duration_seconds
    OR NEW.average_view_percentage      IS DISTINCT FROM OLD.average_view_percentage
    OR NEW.impressions                  IS DISTINCT FROM OLD.impressions
    OR NEW.impression_ctr               IS DISTINCT FROM OLD.impression_ctr
    OR NEW.likes                        IS DISTINCT FROM OLD.likes
    OR NEW.dislikes                     IS DISTINCT FROM OLD.dislikes
    OR NEW.comments                     IS DISTINCT FROM OLD.comments
    OR NEW.shares                       IS DISTINCT FROM OLD.shares
    OR NEW.subscribers_gained           IS DISTINCT FROM OLD.subscribers_gained
    OR NEW.subscribers_lost             IS DISTINCT FROM OLD.subscribers_lost
  ) THEN
    INSERT INTO video_daily_metric_history (
      metric_id, video_id, date,
      views, estimated_minutes_watched, average_view_duration_seconds,
      average_view_percentage, impressions, impression_ctr,
      likes, dislikes, comments, shares,
      subscribers_gained, subscribers_lost,
      superseded_sync_run_id, superseded_at
    ) VALUES (
      OLD.id, OLD.video_id, OLD.date,
      OLD.views, OLD.estimated_minutes_watched, OLD.average_view_duration_seconds,
      OLD.average_view_percentage, OLD.impressions, OLD.impression_ctr,
      OLD.likes, OLD.dislikes, OLD.comments, OLD.shares,
      OLD.subscribers_gained, OLD.subscribers_lost,
      OLD.last_sync_run_id, now()
    );

    NEW.revision_count := OLD.revision_count + 1;
    NEW.updated_at := now();
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER video_daily_metric_revision
  BEFORE UPDATE ON video_daily_metric
  FOR EACH ROW EXECUTE FUNCTION record_video_metric_revision();
--> statement-breakpoint

-- Cấp kênh chỉ cần đếm số lần sửa; giá trị cũ ở cấp video đã đủ để truy vết,
-- và chỉ số kênh là tổng hợp nên không dùng để quy trách nhiệm cho video nào.
CREATE OR REPLACE FUNCTION record_channel_metric_revision()
RETURNS TRIGGER AS $$
BEGIN
  IF (
    NEW.views                          IS DISTINCT FROM OLD.views
    OR NEW.estimated_minutes_watched    IS DISTINCT FROM OLD.estimated_minutes_watched
    OR NEW.average_view_duration_seconds IS DISTINCT FROM OLD.average_view_duration_seconds
    OR NEW.average_view_percentage      IS DISTINCT FROM OLD.average_view_percentage
    OR NEW.impressions                  IS DISTINCT FROM OLD.impressions
    OR NEW.impression_ctr               IS DISTINCT FROM OLD.impression_ctr
    OR NEW.likes                        IS DISTINCT FROM OLD.likes
    OR NEW.dislikes                     IS DISTINCT FROM OLD.dislikes
    OR NEW.comments                     IS DISTINCT FROM OLD.comments
    OR NEW.shares                       IS DISTINCT FROM OLD.shares
    OR NEW.subscribers_gained           IS DISTINCT FROM OLD.subscribers_gained
    OR NEW.subscribers_lost             IS DISTINCT FROM OLD.subscribers_lost
  ) THEN
    NEW.revision_count := OLD.revision_count + 1;
    NEW.updated_at := now();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER channel_daily_metric_revision
  BEFORE UPDATE ON channel_daily_metric
  FOR EACH ROW EXECUTE FUNCTION record_channel_metric_revision();
--> statement-breakpoint

-- Lịch sử là append-only: sửa được lịch sử thì nó không còn là bằng chứng cho
-- việc "số liệu từng là bao nhiêu".
CREATE OR REPLACE FUNCTION enforce_metric_history_append_only()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_METRIC_HISTORY: video_daily_metric_history la append-only (thao tac: %)', TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER video_daily_metric_history_append_only
  BEFORE UPDATE OR DELETE ON video_daily_metric_history
  FOR EACH ROW EXECUTE FUNCTION enforce_metric_history_append_only();
