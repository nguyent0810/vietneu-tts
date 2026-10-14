-- Sửa HAI chỗ 0031 làm QUÁ TAY. Cả hai do bộ test bắt được, không phải do rà soát.
--
-- (A) `COMPOSITE_VERDICT_WITHOUT_LINEAGE` chặn nhầm TOÀN BỘ đường ghi cũ.
--
--     Cột `analysis_validation.stage` có DEFAULT `'COMPOSITE'`. Nghĩa là mọi lệnh
--     ghi kiểm định KHÔNG nêu `stage` — tức toàn bộ mã Phase 1–3 và fixture của
--     chúng — đều tạo ra một phán quyết COMPOSITE trên một execution không có
--     lineage lượt phân tích. 0031 biến điều đó thành lỗi cứng, làm hỏng 9 ca
--     kiểm thử lưu trữ vốn chẳng liên quan gì tới kiến trúc hai lượt.
--
--     0028 xử lý đúng: không có lineage thì phán quyết ấy KHÔNG thuộc phạm vi
--     quy tắc "một phán quyết ĐẠT cho mỗi lượt phân tích" — vì không có lượt
--     phân tích nào để quy về. Trả `NEW` như cũ. Điều này KHÔNG mở ra lỗ hổng:
--     một kết quả chính thức hai lượt còn phải qua `cursor_result_semantic_lineage`,
--     vốn đòi lineage trong bản kê một cách độc lập.
--
-- (B) Trigger MỚI che mất thông điệp lỗi của trigger CŨ, CHÍNH XÁC LÀ lỗi tôi đã
--     mắc ở 0029 và tưởng đã rút kinh nghiệm.
--
--     Postgres chạy trigger theo THỨ TỰ TÊN. `cursor_result_requires_declaration`
--     đứng trước `cursor_result_semantic_lineage`, nên một kết quả có kiểm định
--     ANALYSIS KHÔNG ĐẠT nay báo "thiếu bản khai" thay vì "phân tích không đạt".
--     Nguyên nhân thật bị giấu sau một nguyên nhân chung chung hơn.
--
--     Cách sửa: KHÔNG thêm trigger song song. Gộp phép kiểm mới vào CUỐI
--     `cursor_result_semantic_lineage`, sau các phép kiểm cụ thể. Thứ tự kiểm =
--     thứ tự chẩn đoán, và điều đó phải do MỘT hàm quyết định, không do bảng chữ cái.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cursor_result_requires_declaration') THEN
    RAISE EXCEPTION 'PREFLIGHT_0032: chua chay 0031';
  END IF;
END $$;
--> statement-breakpoint

-- (A) Không lineage => ngoài phạm vi quy tắc, không phải lỗi.
CREATE OR REPLACE FUNCTION cursor_single_composite_verdict()
RETURNS TRIGGER AS $$
DECLARE
  my_analysis uuid;
  competing uuid;
BEGIN
  IF NEW.stage <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  IF NEW.passed IS NOT TRUE THEN
    RETURN NEW;
  END IF;

  SELECT m.analysis_execution_id INTO my_analysis
  FROM cursor_execution_manifest m
  WHERE m.llm_execution_id = NEW.llm_execution_id;

  -- Đường ghi CŨ (một lượt): không có lineage nên quy tắc "một phán quyết ĐẠT
  -- cho mỗi lượt phân tích" không áp dụng được. Cấp phép kết quả hai lượt vẫn
  -- bị `cursor_result_semantic_lineage` chặn độc lập.
  IF my_analysis IS NULL THEN
    RETURN NEW;
  END IF;

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
    RETURN NEW;
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

-- (B) Gỡ trigger song song; phép kiểm sẽ nằm CUỐI hàm lineage.
DROP TRIGGER IF EXISTS cursor_result_requires_declaration ON "cursor_analysis_result";
--> statement-breakpoint
DROP FUNCTION IF EXISTS cursor_result_requires_declaration();
--> statement-breakpoint

CREATE OR REPLACE FUNCTION cursor_result_semantic_lineage()
RETURNS TRIGGER AS $$
DECLARE
  m RECORD;
  validation_passed boolean;
  analysis_ok boolean;
  declaration_ok boolean;
  composite_ok boolean;
  ob RECORD;
BEGIN
  SELECT schema_version, execution_role, analysis_execution_id,
         analysis_payload_hash, obligation_set_hash
    INTO m
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.llm_execution_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'RESULT_WITHOUT_MANIFEST: execution % chua co ban ke',
      NEW.llm_execution_id;
  END IF;

  IF m.schema_version <> 'legacy' AND m.schema_version IS DISTINCT FROM NEW.schema_version THEN
    RAISE EXCEPTION
      'RESULT_SCHEMA_MISMATCH: ket qua schema % nhung ban ke execution la %',
      NEW.schema_version, m.schema_version;
  END IF;

  -- (1) Vai kết quả phải khớp vai execution.
  IF NEW.result_role = 'ANALYSIS' AND m.execution_role <> 'ANALYSIS' THEN
    RAISE EXCEPTION
      'RESULT_ROLE_MISMATCH: ket qua ANALYSIS nhung execution co vai %', m.execution_role;
  END IF;
  IF NEW.result_role = 'COMPOSITE' AND m.execution_role = 'DECLARATION'
     AND m.analysis_execution_id IS NULL THEN
    RAISE EXCEPTION 'RESULT_WITHOUT_ANALYSIS_LINK: ban ke luot khai bao thieu analysis_execution_id';
  END IF;

  -- (2) Phán quyết. Kết quả của kiến trúc MỘT LƯỢT (execution vai ANALYSIS mang
  -- kết quả COMPOSITE) vẫn chỉ cần một dòng COMPOSITE — giữ tương thích với dữ
  -- liệu và với đường chạy cũ.
  IF m.execution_role = 'DECLARATION' THEN
    SELECT passed INTO declaration_ok FROM analysis_validation
     WHERE llm_execution_id = NEW.llm_execution_id AND stage = 'DECLARATION';
    IF NOT FOUND THEN
      RAISE EXCEPTION 'RESULT_WITHOUT_DECLARATION_VALIDATION: execution % thieu phan quyet DECLARATION',
        NEW.llm_execution_id;
    END IF;
    IF declaration_ok IS NOT TRUE THEN
      RAISE EXCEPTION 'RESULT_WITH_FAILED_DECLARATION: execution % co chang DECLARATION KHONG dat',
        NEW.llm_execution_id;
    END IF;

    SELECT passed INTO analysis_ok FROM analysis_validation
     WHERE llm_execution_id = m.analysis_execution_id AND stage = 'ANALYSIS';
    IF NOT FOUND THEN
      RAISE EXCEPTION 'RESULT_WITHOUT_ANALYSIS_VALIDATION: luot phan tich % thieu phan quyet ANALYSIS',
        m.analysis_execution_id;
    END IF;
    IF analysis_ok IS NOT TRUE THEN
      RAISE EXCEPTION 'RESULT_WITH_FAILED_ANALYSIS: luot phan tich % co chang ANALYSIS KHONG dat',
        m.analysis_execution_id;
    END IF;

    -- (3) Băm neo phải khớp bản kê VÀ tập nghĩa vụ có thật.
    SELECT analysis_hash, obligation_set_hash INTO ob
      FROM cursor_claim_obligation
     WHERE analysis_execution_id = m.analysis_execution_id;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'RESULT_WITHOUT_OBLIGATION_SET: luot phan tich % chua co tap nghia vu',
        m.analysis_execution_id;
    END IF;
    IF ob.analysis_hash IS DISTINCT FROM NEW.analysis_payload_hash
    OR ob.obligation_set_hash IS DISTINCT FROM NEW.obligation_set_hash THEN
      RAISE EXCEPTION
        'RESULT_LINEAGE_DRIFT: bam neo cua ket qua khong khop tap nghia vu cua luot phan tich %',
        m.analysis_execution_id;
    END IF;
    IF m.analysis_payload_hash IS DISTINCT FROM NEW.analysis_payload_hash
    OR m.obligation_set_hash IS DISTINCT FROM NEW.obligation_set_hash THEN
      RAISE EXCEPTION
        'RESULT_MANIFEST_LINEAGE_DRIFT: bam neo cua ket qua khong khop ban ke luot khai bao';
    END IF;
  END IF;

  -- Phán quyết CỦA CHÍNH execution này, theo vai kết quả.
  IF NEW.result_role = 'ANALYSIS' THEN
    SELECT passed INTO validation_passed FROM analysis_validation
     WHERE llm_execution_id = NEW.llm_execution_id AND stage = 'ANALYSIS';
  ELSE
    SELECT passed INTO validation_passed FROM analysis_validation
     WHERE llm_execution_id = NEW.llm_execution_id AND stage = 'COMPOSITE';
  END IF;

  -- FAIL-CLOSED: thiếu dòng kiểm định cũng bị từ chối, không chỉ khi nó FALSE.
  IF NOT FOUND THEN
    RAISE EXCEPTION
      'RESULT_WITHOUT_VALIDATION: execution % chua co dong kiem dinh cho vai %',
      NEW.llm_execution_id, NEW.result_role;
  END IF;

  IF validation_passed IS NOT TRUE THEN
    RAISE EXCEPTION
      'RESULT_WITH_FAILED_VALIDATION: execution % co kiem dinh KHONG dat',
      NEW.llm_execution_id;
  END IF;

  -- CUỐI CÙNG: hiện vật hợp nhất phải có BẢN KHAI ĐÃ LƯU.
  --
  -- Đặt ở cuối, trong CÙNG hàm này, chứ không tách thành trigger riêng: trigger
  -- riêng chạy theo thứ tự tên và sẽ che mất mọi chẩn đoán cụ thể ở trên.
  IF NEW.result_role = 'COMPOSITE' AND NOT EXISTS (
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

DO $$
BEGIN
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_single_composite_verdict')
     NOT LIKE '%pg_advisory_xact_lock%' THEN
    RAISE EXCEPTION 'POSTCHECK_0032: mat khoa chong dua';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_result_requires_declaration') THEN
    RAISE EXCEPTION 'POSTCHECK_0032: trigger song song van con';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_single_composite_verdict')
     LIKE '%COMPOSITE_VERDICT_WITHOUT_LINEAGE%' THEN
    RAISE EXCEPTION 'POSTCHECK_0032: van con loi cung chan duong ghi cu';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_result_semantic_lineage')
     NOT LIKE '%RESULT_WITHOUT_DECLARATION_PAYLOAD%' THEN
    RAISE EXCEPTION 'POSTCHECK_0032: phep kiem ban khai chua duoc gop vao ham lineage';
  END IF;
END $$;
