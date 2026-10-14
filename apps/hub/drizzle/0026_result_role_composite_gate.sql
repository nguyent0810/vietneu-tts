-- CHỈ chặng COMPOSITE mới cấp phép cho một kết quả CHÍNH THỨC.
--
-- Hai loại kết quả:
--   ANALYSIS  — văn xuôi bất biến của lượt 1, giữ làm bằng chứng;
--   COMPOSITE — kết quả hợp nhất (văn xuôi + metricClaims), thứ duy nhất được
--               coi là kết quả của lần chạy.
--
-- Giữ CẢ HAI, không chỉ bản hợp nhất: nếu chỉ lưu bản hợp nhất thì không còn cách
-- nào chứng minh lượt khai báo đã không sửa một chữ nào của văn xuôi.
--
-- `cursor_result_execution_key` (UNIQUE trên llm_execution_id) GIỮ NGUYÊN và vẫn
-- đúng: hai kết quả gắn vào HAI execution khác nhau (lượt 1 và lượt 2), nên không
-- có xung đột. Không cần nới ràng buộc nào ở đây.

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
              WHERE table_name = 'cursor_analysis_result' AND column_name = 'result_role') THEN
    RAISE EXCEPTION 'PREFLIGHT_0026: cot result_role DA TON TAI';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name = 'analysis_validation' AND column_name = 'stage') THEN
    RAISE EXCEPTION 'PREFLIGHT_0026: chua chay 0025 — thu tu migration sai';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_result_semantic_lineage')
     NOT LIKE '%RESULT_WITHOUT_VALIDATION%' THEN
    RAISE EXCEPTION 'PREFLIGHT_0026: trigger 0022 khong o trang thai mong doi';
  END IF;
END $$;
--> statement-breakpoint

DO $$
BEGIN
  CREATE TYPE "cursor_result_role" AS ENUM ('ANALYSIS', 'COMPOSITE');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
--> statement-breakpoint

-- Kết quả cũ đều là phán quyết cuối của hợp đồng một lượt -> COMPOSITE.
ALTER TABLE "cursor_analysis_result"
  ADD COLUMN "result_role" "cursor_result_role" NOT NULL DEFAULT 'COMPOSITE';
--> statement-breakpoint

ALTER TABLE "cursor_analysis_result" ADD COLUMN "analysis_payload_hash" text;
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result" ADD COLUMN "obligation_set_hash" text;
--> statement-breakpoint

ALTER TABLE "cursor_analysis_result"
  ADD CONSTRAINT "cursor_result_lineage_hash_format" CHECK (
    ("analysis_payload_hash" IS NULL OR "analysis_payload_hash" ~ '^[0-9a-f]{64}$')
    AND ("obligation_set_hash" IS NULL OR "obligation_set_hash" ~ '^[0-9a-f]{64}$')
  );
--> statement-breakpoint

-- KHÔNG có CHECK "COMPOSITE phải có băm neo" — và đây là một quyết định, không
-- phải một thiếu sót.
--
-- Bản đầu của migration này có một CHECK như thế. Nó CHẠY ĐƯỢC trên TEST (rỗng)
-- và THẤT BẠI trên MAIN, nơi có 32 dòng kết quả của hợp đồng MỘT LƯỢT: chúng
-- nhận `result_role = 'COMPOSITE'` theo mặc định nhưng không có băm neo nào, vì
-- kiến trúc sinh ra chúng chưa có tập nghĩa vụ. Hai database phân kỳ ngay lần
-- áp đầu tiên.
--
-- Bài học không phải "nới CHECK cho dữ liệu cũ lọt". Bài học là điều kiện này
-- KHÔNG BIỂU DIỄN ĐƯỢC bằng CHECK: nó phụ thuộc vai của EXECUTION, mà vai đó nằm
-- ở bảng khác. CHECK chỉ nhìn thấy một hàng của chính bảng nó.
--
-- Trigger bên dưới cưỡng chế đúng điều kiện đó, và ĐÚNG PHẠM VI: khi và chỉ khi
-- execution có vai DECLARATION. Đường một lượt cũ đi qua nhánh khác và giữ
-- nguyên hành vi cũ.
--
-- KHOẢNG HỞ CÒN LẠI, ghi rõ: một kết quả COMPOSITE gắn vào execution vai
-- ANALYSIS (đúng hình dạng của đường MỘT LƯỢT) vẫn được chấp nhận mà không cần
-- băm neo. Điều đó là CỐ Ý để giữ lịch sử đọc được; đường hai lượt không bao giờ
-- sinh ra hình dạng ấy.

-- Trigger hợp nhất: mở rộng 0022 cho kiến trúc hai lượt.
--
-- Giữ nguyên mọi bất biến cũ (bản kê phải có, schema phải khớp, kiểm định phải
-- ĐẠT), và thêm ba điều:
--   1. vai kết quả phải khớp vai execution;
--   2. kết quả COMPOSITE đòi ĐỦ BA phán quyết ĐẠT, đúng execution;
--   3. băm neo phải khớp bản kê và tập nghĩa vụ.
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

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name = 'cursor_analysis_result'
                    AND column_name = 'result_role' AND is_nullable = 'NO') THEN
    RAISE EXCEPTION 'POSTCHECK_0026: result_role thieu hoac nullable';
  END IF;
  IF EXISTS (SELECT 1 FROM cursor_analysis_result WHERE result_role IS NULL) THEN
    RAISE EXCEPTION 'POSTCHECK_0026: con dong result_role NULL';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_result_semantic_lineage')
     NOT LIKE '%RESULT_WITHOUT_OBLIGATION_SET%' THEN
    RAISE EXCEPTION 'POSTCHECK_0026: trigger chua duoc cap nhat';
  END IF;
END $$;
