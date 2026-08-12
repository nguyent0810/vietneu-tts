-- Bốn lỗ hổng ở tầng CẤP PHÉP, tìm ra bởi rà soát đối kháng G8.
--
-- Điểm chung: mọi phép kiểm hiện có đều nằm ở TypeScript hoặc dựa vào ảnh chụp
-- (snapshot) của một giao dịch. Cả hai đều bỏ trống đúng chỗ mà một hiện vật
-- "chính thức" được sinh ra.
--
--   1. ĐUA GIỮA HAI GIAO DỊCH — nghiêm trọng nhất. Trigger 0028 làm "SELECT rồi
--      INSERT". Ở mức cô lập mặc định (READ COMMITTED), hai giao dịch đồng thời
--      ghi phán quyết ĐẠT cho hai lượt khai báo của CÙNG một lượt phân tích đều
--      không thấy hàng chưa commit của bên kia, nên CẢ HAI qua. Kết quả: hai
--      phán quyết ĐẠT và hai hiện vật chính thức — đúng cái 0028 sinh ra để
--      chặn. Không unique index nào chặn được vì `analysis_execution_id` không
--      phải cột của hai bảng đó.
--
--   2. CẤP PHÉP KHI KHÔNG CÓ BẢN KHAI. Trigger cấp phép đọc phán quyết và tập
--      nghĩa vụ, nhưng KHÔNG đòi `cursor_declaration_result` tồn tại. Một script
--      ghi thẳng database dựng đủ phán quyết rồi INSERT kết quả — không có bản
--      khai nào — vẫn được cấp phép.
--
--   3. "LƯỢT PHÂN TÍCH" KHÔNG ĐƯỢC KIỂM LÀ LƯỢT PHÂN TÍCH. `analysis_execution_id`
--      chỉ có khoá ngoại tới `llm_execution`, nên nó trỏ được vào một execution
--      mang vai DECLARATION. Cả một chuỗi giả có thể tự nhất quán.
--
--   4. TRẦN LẦN THỬ KHÔNG PHẢI LÀ TRẦN. CHECK `attempt_number BETWEEN 1 AND 3`
--      giới hạn GIÁ TRỊ của từng hàng, không giới hạn SỐ HÀNG. Một script tạo
--      100 lượt khai báo cùng `attempt_number = 1` rồi chọn lần đẹp nhất để xin
--      phán quyết ĐẠT — đúng định nghĩa của gian lận thử lại.
--
-- HẠN CHẾ, nói thẳng: đây vẫn là ràng buộc trong database, không phải
-- attestation. Superuser vẫn tắt được trigger. Nó chặn sự cố, chặn mã sai và
-- chặn script ghi thẳng; nó không chặn người cố tình có toàn quyền.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cursor_single_composite_verdict') THEN
    RAISE EXCEPTION 'PREFLIGHT_0031: chua chay 0028';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cursor_result_semantic_lineage') THEN
    RAISE EXCEPTION 'PREFLIGHT_0031: chua chay 0026';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_single_composite_verdict')
     LIKE '%pg_advisory_xact_lock%' THEN
    RAISE EXCEPTION 'PREFLIGHT_0031: migration nay da chay?';
  END IF;
END $$;
--> statement-breakpoint

-- (1) KHOÁ theo lượt phân tích, lấy TRƯỚC khi đọc.
--
-- `pg_advisory_xact_lock` tuần tự hoá đúng những giao dịch tranh nhau cùng một
-- lượt phân tích, và tự nhả khi giao dịch kết thúc. Đặt trong THÂN TRIGGER nên
-- mọi người ghi đều lấy nó — kể cả script ghi thẳng, vốn là kẻ ta lo nhất.
CREATE OR REPLACE FUNCTION cursor_single_composite_verdict()
RETURNS TRIGGER AS $$
DECLARE
  my_analysis uuid;
  competing uuid;
BEGIN
  IF NEW.stage <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  -- Phán quyết KHÔNG ĐẠT là BẰNG CHỨNG, không phải quyền. Ghi bao nhiêu cũng được.
  IF NEW.passed IS NOT TRUE THEN
    RETURN NEW;
  END IF;

  SELECT m.analysis_execution_id INTO my_analysis
  FROM cursor_execution_manifest m
  WHERE m.llm_execution_id = NEW.llm_execution_id;

  IF my_analysis IS NULL THEN
    RAISE EXCEPTION
      'COMPOSITE_VERDICT_WITHOUT_LINEAGE: execution % khong co lineage luot phan tich',
      NEW.llm_execution_id;
  END IF;

  -- Tuần tự hoá TRƯỚC khi đọc. Không có dòng này thì phép đọc dưới đây chạy
  -- trên một ảnh chụp không thấy đối thủ, và cả hai bên cùng kết luận "chưa ai
  -- có quyền".
  PERFORM pg_advisory_xact_lock(hashtextextended(my_analysis::text, 0));

  SELECT v.llm_execution_id INTO competing
  FROM analysis_validation v
  JOIN cursor_execution_manifest m2 ON m2.llm_execution_id = v.llm_execution_id
  WHERE v.stage = 'COMPOSITE'
    AND v.passed = true
    AND m2.analysis_execution_id = my_analysis
    AND v.llm_execution_id <> NEW.llm_execution_id
  LIMIT 1;

  IF competing IS NOT NULL THEN
    RAISE EXCEPTION
      'COMPETING_COMPOSITE_VERDICT: luot phan tich % da co phan quyet DAT tu execution %',
      my_analysis, competing;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE OR REPLACE FUNCTION cursor_single_authoritative_result()
RETURNS TRIGGER AS $$
DECLARE
  my_analysis uuid;
  competing uuid;
BEGIN
  IF NEW.result_role <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  SELECT m.analysis_execution_id INTO my_analysis
  FROM cursor_execution_manifest m
  WHERE m.llm_execution_id = NEW.llm_execution_id;

  IF my_analysis IS NULL THEN
    RAISE EXCEPTION
      'AUTHORITATIVE_RESULT_WITHOUT_LINEAGE: execution % khong co lineage luot phan tich',
      NEW.llm_execution_id;
  END IF;

  PERFORM pg_advisory_xact_lock(hashtextextended(my_analysis::text, 0));

  SELECT r.llm_execution_id INTO competing
  FROM cursor_analysis_result r
  JOIN cursor_execution_manifest m2 ON m2.llm_execution_id = r.llm_execution_id
  WHERE r.result_role = 'COMPOSITE'
    AND m2.analysis_execution_id = my_analysis
    AND r.llm_execution_id <> NEW.llm_execution_id
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

-- (2)+(3) Bản khai PHẢI tồn tại; "lượt phân tích" PHẢI mang vai ANALYSIS.
CREATE OR REPLACE FUNCTION cursor_declaration_lineage_sound()
RETURNS TRIGGER AS $$
DECLARE
  parent_role cursor_execution_role;
BEGIN
  IF NEW.execution_role <> 'DECLARATION' THEN
    RETURN NEW;
  END IF;

  IF NEW.analysis_execution_id IS NULL THEN
    RAISE EXCEPTION 'DECLARATION_WITHOUT_ANALYSIS: manifest % thieu analysis_execution_id', NEW.llm_execution_id;
  END IF;

  SELECT m.execution_role INTO parent_role
  FROM cursor_execution_manifest m
  WHERE m.llm_execution_id = NEW.analysis_execution_id;

  IF parent_role IS NULL THEN
    RAISE EXCEPTION
      'DECLARATION_ANALYSIS_NOT_FOUND: khong co manifest cho analysis_execution_id %',
      NEW.analysis_execution_id;
  END IF;

  IF parent_role <> 'ANALYSIS' THEN
    RAISE EXCEPTION
      'DECLARATION_ANALYSIS_WRONG_ROLE: analysis_execution_id % mang vai %, phai la ANALYSIS',
      NEW.analysis_execution_id, parent_role;
  END IF;

  -- (4) TRẦN theo SỐ LƯỢNG, không theo giá trị cột.
  --
  -- Khoá trước khi đếm, cùng lý do như trên: hai giao dịch đồng thời đều đếm
  -- được 3 rồi cùng chèn hàng thứ tư.
  PERFORM pg_advisory_xact_lock(hashtextextended(NEW.analysis_execution_id::text, 1));

  IF (
    SELECT count(*)
    FROM cursor_execution_manifest m
    WHERE m.analysis_execution_id = NEW.analysis_execution_id
      AND m.execution_role = 'DECLARATION'
      AND m.llm_execution_id <> NEW.llm_execution_id
  ) >= 3 THEN
    RAISE EXCEPTION
      'DECLARATION_ATTEMPT_CAP: luot phan tich % da co 3 lan thu khai bao — tran chung, khong dat lai duoc',
      NEW.analysis_execution_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_manifest_declaration_lineage ON "cursor_execution_manifest";
--> statement-breakpoint

CREATE TRIGGER cursor_manifest_declaration_lineage
  BEFORE INSERT ON "cursor_execution_manifest"
  FOR EACH ROW EXECUTE FUNCTION cursor_declaration_lineage_sound();
--> statement-breakpoint

-- (2) Kết quả chính thức đòi BẢN KHAI ĐÃ LƯU.
CREATE OR REPLACE FUNCTION cursor_result_requires_declaration()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.result_role <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM cursor_declaration_result d
    WHERE d.llm_execution_id = NEW.llm_execution_id
  ) THEN
    RAISE EXCEPTION
      'RESULT_WITHOUT_DECLARATION_PAYLOAD: execution % chua luu ban khai nao',
      NEW.llm_execution_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_result_requires_declaration ON "cursor_analysis_result";
--> statement-breakpoint

CREATE TRIGGER cursor_result_requires_declaration
  BEFORE INSERT ON "cursor_analysis_result"
  FOR EACH ROW EXECUTE FUNCTION cursor_result_requires_declaration();
--> statement-breakpoint

DO $$
BEGIN
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_single_composite_verdict')
     NOT LIKE '%pg_advisory_xact_lock%' THEN
    RAISE EXCEPTION 'POSTCHECK_0031: phan quyet chua lay khoa';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_single_authoritative_result')
     NOT LIKE '%pg_advisory_xact_lock%' THEN
    RAISE EXCEPTION 'POSTCHECK_0031: ket qua chua lay khoa';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_manifest_declaration_lineage') THEN
    RAISE EXCEPTION 'POSTCHECK_0031: thieu trigger lineage khai bao';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_result_requires_declaration') THEN
    RAISE EXCEPTION 'POSTCHECK_0031: thieu trigger doi ban khai';
  END IF;
END $$;
