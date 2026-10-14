-- Cưỡng chế BẤT BIẾN ở tầng DB.
--
-- Vì sao không chỉ chặn ở tầng ứng dụng: một revision đã FROZEN mà vẫn sửa
-- được thì mọi điểm số, phê duyệt và kết quả phân tích trỏ vào nó đều mất ý
-- nghĩa -- và bất biến S-0 ("freeze trước khi audit") không còn kiểm chứng
-- được. Route có thể bị bỏ qua bởi script chạy tay, migration, hoặc một
-- đường ghi mới thêm sau này; trigger thì không.
--
-- Mã lỗi: RAISE EXCEPTION mặc định (SQLSTATE P0001) kèm tiền tố 'IMMUTABLE_'
-- trong message để src/lib/errors.ts ánh xạ sang REVISION_FROZEN.

CREATE OR REPLACE FUNCTION enforce_content_revision_immutability()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.state = 'FROZEN' THEN
    RAISE EXCEPTION 'IMMUTABLE_CONTENT_REVISION: revision % da FROZEN, khong the sua', OLD.id;
  END IF;

  -- Khi còn DRAFT, các cột định danh vẫn không được đổi.
  IF NEW.content_item_id <> OLD.content_item_id OR NEW.revision_number <> OLD.revision_number THEN
    RAISE EXCEPTION 'IMMUTABLE_CONTENT_REVISION: khong duoc doi content_item_id/revision_number';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER content_revision_immutability
  BEFORE UPDATE ON content_revision
  FOR EACH ROW EXECUTE FUNCTION enforce_content_revision_immutability();
--> statement-breakpoint

-- Xoá một revision đã FROZEN bị cấm TUYỆT ĐỐI: nó là bằng chứng cho các kết
-- quả phân tích đã sinh ra từ nó.
--
-- Bản đầu tiên có `WHEN (pg_trigger_depth() = 0)` để cho ON DELETE CASCADE từ
-- content_item đi qua. Đó là một lỗ hổng: chỉ cần xoá content_item cha là quét
-- sạch mọi revision FROZEN cùng lịch sử của chúng — đúng thứ mà trigger này
-- sinh ra để ngăn. Nay bỏ hẳn điều kiện depth, và khoá ngoại từ content_revision
-- đổi sang ON DELETE RESTRICT (xem schema/content.ts), nên không còn đường vòng.
--
-- Muốn "bỏ" một nội dung thì đổi content_item.status sang ARCHIVED, không xoá.
CREATE OR REPLACE FUNCTION enforce_content_revision_no_delete()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.state = 'FROZEN' THEN
    RAISE EXCEPTION 'IMMUTABLE_CONTENT_REVISION: khong the xoa revision da FROZEN (%)', OLD.id;
  END IF;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER content_revision_no_delete
  BEFORE DELETE ON content_revision
  FOR EACH ROW EXECUTE FUNCTION enforce_content_revision_no_delete();
--> statement-breakpoint

-- prompt_revision: bất biến hoàn toàn ngay từ khi tạo.
--
-- Phase 5 bắt buộc "giữ lại mọi phiên bản prompt, kết quả, critique và đánh
-- giá". Tinh chỉnh prompt phải tạo hàng MỚI trỏ về parent_revision_id, không
-- bao giờ sửa hàng cũ -- nếu không thì so sánh "trước/sau" giữa hai vòng lặp
-- không còn ý nghĩa.
-- Chặn cả UPDATE lẫn DELETE. Chỉ chặn UPDATE là chưa đủ: xoá rồi ghi lại vẫn
-- xoá được lịch sử, và cây phả hệ prompt (parent_revision_id) sẽ đứt ở giữa.
CREATE OR REPLACE FUNCTION enforce_prompt_revision_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_PROMPT_REVISION: prompt revision % la bat bien (thao tac: %)', OLD.id, TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER prompt_revision_immutability
  BEFORE UPDATE OR DELETE ON prompt_revision
  FOR EACH ROW EXECUTE FUNCTION enforce_prompt_revision_immutability();
--> statement-breakpoint

-- audit_event: append-only. Một dòng audit sửa được thì nó không còn là bằng chứng.
CREATE OR REPLACE FUNCTION enforce_audit_append_only()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_AUDIT_EVENT: audit_event la append-only (thao tac: %)', TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER audit_event_append_only
  BEFORE UPDATE OR DELETE ON audit_event
  FOR EACH ROW EXECUTE FUNCTION enforce_audit_append_only();
--> statement-breakpoint

-- analysis_result: bất biến sau khi ghi.
--
-- Chạy lại phân tích thì tạo analysis_run mới (run_sequence tăng), không ghi
-- đè kết quả cũ. Nếu ghi đè được thì lịch sử so sánh giữa các vòng tinh chỉnh
-- của Phase 5 sẽ bị viết lại phía sau lưng.
-- Chặn cả UPDATE lẫn DELETE, và khoá ngoại tới analysis_run đã đổi sang
-- RESTRICT (xem schema/analysis.ts) — nếu để cascade thì xoá run là xoá luôn
-- kết quả, vòng qua đúng trigger này.
CREATE OR REPLACE FUNCTION enforce_analysis_result_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_ANALYSIS_RESULT: ket qua % la bat bien (thao tac: %)', OLD.id, TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER analysis_result_immutability
  BEFORE UPDATE OR DELETE ON analysis_result
  FOR EACH ROW EXECUTE FUNCTION enforce_analysis_result_immutability();
