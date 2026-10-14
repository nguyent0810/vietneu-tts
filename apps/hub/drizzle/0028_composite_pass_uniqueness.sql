-- MỘT phán quyết COMPOSITE **ĐẠT** cho mỗi lượt phân tích — không phải một dòng.
--
-- 0027 chặn MỌI phán quyết COMPOSITE thứ hai của cùng một lượt phân tích. Chặt
-- quá, và chặt sai chỗ: nó khiến một lần khai báo hỏng vì ngữ nghĩa KHÔNG thể
-- được ghi lại, nên cũng không thể thử lại — lần thử thứ hai bị trigger từ chối
-- trước cả khi ai kịp đọc nó hỏng vì sao.
--
-- Hai thứ khác nhau bị gộp làm một:
--
--   * BẰNG CHỨNG  — mọi lần khai báo, kể cả hỏng, phải lưu lại được và đọc lại
--     được. Đây đúng là yêu cầu "giữ lại mọi lần thử" của cả Phase 4.
--   * QUYỀN — chỉ MỘT phán quyết ĐẠT được phép tồn tại, vì chỉ nó cấp phép cho
--     kết quả chính thức. Hai phán quyết ĐẠT là hai kết quả cạnh tranh nhau cho
--     cùng một bài phân tích, tức "chạy lại tới khi được số đẹp".
--
-- Bản này chỉ ràng buộc cái thứ hai. Phán quyết KHÔNG ĐẠT được ghi thoải mái.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cursor_single_composite_verdict') THEN
    RAISE EXCEPTION 'PREFLIGHT_0028: chua chay 0027 — thu tu migration sai';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_single_composite_verdict')
     LIKE '%NEW.passed%' THEN
    RAISE EXCEPTION 'PREFLIGHT_0028: trigger DA phan biet passed — migration nay da chay?';
  END IF;
END $$;
--> statement-breakpoint

CREATE OR REPLACE FUNCTION cursor_single_composite_verdict()
RETURNS TRIGGER AS $$
DECLARE
  my_analysis uuid;
  competing uuid;
BEGIN
  IF NEW.stage <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  -- Phán quyết KHÔNG ĐẠT là BẰNG CHỨNG, không phải quyền. Ghi bao nhiêu cũng được:
  -- mỗi lần khai báo hỏng phải để lại dấu vết đọc được.
  IF NEW.passed IS NOT TRUE THEN
    RETURN NEW;
  END IF;

  SELECT analysis_execution_id INTO my_analysis
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.llm_execution_id;

  -- Đường MỘT LƯỢT cũ: không có lượt phân tích riêng, không có gì để so.
  IF my_analysis IS NULL THEN
    RETURN NEW;
  END IF;

  -- Chỉ tính các phán quyết ĐẠT: đó mới là thứ cấp phép cho kết quả.
  SELECT v.llm_execution_id INTO competing
    FROM analysis_validation v
    JOIN cursor_execution_manifest m ON m.llm_execution_id = v.llm_execution_id
   WHERE v.stage = 'COMPOSITE'
     AND v.passed IS TRUE
     AND v.llm_execution_id <> NEW.llm_execution_id
     AND m.analysis_execution_id = my_analysis
   LIMIT 1;

  IF competing IS NOT NULL THEN
    RAISE EXCEPTION
      'COMPETING_COMPOSITE_VERDICT: luot phan tich % da co phan quyet COMPOSITE DAT tu execution %',
      my_analysis, competing;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

-- Hàng rào THỨ HAI, độc lập: ĐÚNG MỘT kết quả chính thức cho mỗi lượt phân tích.
--
-- Suy ra được từ trigger trên (kết quả đòi phán quyết ĐẠT, mà phán quyết ĐẠT chỉ
-- có một). Nhưng "suy ra được" không phải "được cưỡng chế": nếu ai đó về sau nới
-- trigger kia thì tầng kết quả mất bảo vệ mà không có gì báo. Hai hàng rào cho
-- một bất biến quan trọng là có chủ đích, không phải thừa.
CREATE OR REPLACE FUNCTION cursor_single_authoritative_result()
RETURNS TRIGGER AS $$
DECLARE
  my_analysis uuid;
  competing uuid;
BEGIN
  IF NEW.result_role <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  SELECT analysis_execution_id INTO my_analysis
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.llm_execution_id;

  IF my_analysis IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT r.llm_execution_id INTO competing
    FROM cursor_analysis_result r
    JOIN cursor_execution_manifest m ON m.llm_execution_id = r.llm_execution_id
   WHERE r.result_role = 'COMPOSITE'
     AND r.llm_execution_id <> NEW.llm_execution_id
     AND m.analysis_execution_id = my_analysis
   LIMIT 1;

  IF competing IS NOT NULL THEN
    RAISE EXCEPTION
      'COMPETING_AUTHORITATIVE_RESULT: luot phan tich % da co ket qua chinh thuc tu execution %',
      my_analysis, competing;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_result_single_authoritative ON "cursor_analysis_result";
--> statement-breakpoint

CREATE TRIGGER cursor_result_single_authoritative
  BEFORE INSERT ON "cursor_analysis_result"
  FOR EACH ROW EXECUTE FUNCTION cursor_single_authoritative_result();
--> statement-breakpoint

DO $$
BEGIN
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_single_composite_verdict')
     NOT LIKE '%NEW.passed IS NOT TRUE%' THEN
    RAISE EXCEPTION 'POSTCHECK_0028: trigger phan quyet chua phan biet passed';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_result_single_authoritative') THEN
    RAISE EXCEPTION 'POSTCHECK_0028: thieu trigger ket qua chinh thuc duy nhat';
  END IF;
END $$;
