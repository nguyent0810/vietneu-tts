-- Bất biến: llm_execution ở trạng thái SUCCEEDED PHẢI có một kết quả đã validate.
--
-- Trước đây là CHECK trên `analysis_result_id`. Nhưng kết quả của Cursor nằm ở
-- `cursor_analysis_result` (khoá theo LẦN CHẠY, để các lần chạy lặp lại phục vụ
-- đo độ ổn định không ghi đè nhau), mà CHECK thì không nhìn sang bảng khác.
--
-- Trigger giữ nguyên sức mạnh của bất biến — SUCCEEDED nghĩa là THẬT SỰ có kết
-- quả — đồng thời chấp nhận cả hai nơi lưu.

CREATE OR REPLACE FUNCTION enforce_execution_succeeded_has_result()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'SUCCEEDED'
     AND NEW.analysis_result_id IS NULL
     AND NOT EXISTS (
       SELECT 1 FROM cursor_analysis_result r WHERE r.llm_execution_id = NEW.id
     )
  THEN
    RAISE EXCEPTION
      'EXECUTION_SUCCEEDED_WITHOUT_RESULT: execution % dat SUCCEEDED nhung khong co ket qua da validate', NEW.id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER llm_execution_succeeded_has_result_trg
  BEFORE INSERT OR UPDATE ON llm_execution
  FOR EACH ROW EXECUTE FUNCTION enforce_execution_succeeded_has_result();
