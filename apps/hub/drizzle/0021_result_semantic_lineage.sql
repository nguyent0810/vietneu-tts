-- Dòng KẾT QUẢ phải nhất quán về NGỮ NGHĨA với execution sinh ra nó.
--
-- Các khoá ngoại phức hợp ở 0016-0018 chứng minh được QUAN HỆ HUYẾT THỐNG giữa
-- các dòng, nhưng không chứng minh được tính hợp lệ về nội dung. Cụ thể, trước
-- migration này vẫn ghi được:
--
--   * kết quả `schema_version = '2.0'` trong khi payload JSONB là schema 1;
--   * kết quả schema-1 gắn vào một execution schema-2;
--   * kết quả "thành công" mà không có dòng kiểm định ĐẠT nào;
--   * kết quả có schema khác với bản kê của chính execution đó.
--
-- Tất cả đều lọt vào quần thể "đã đạt" khi đo ổn định, và làm sai mọi con số.
-- Ràng buộc ở tầng database vì một worker cũ hoặc một lệnh ghi thẳng đều bỏ qua
-- kiểm tra ở tầng ứng dụng.

-- 1. Băm phải đúng ĐỊNH DẠNG. Không chứng minh được băm ĐÚNG, nhưng loại bỏ
--    được giá trị rác và chỗ giữ chỗ.
ALTER TABLE "cursor_execution_manifest"
  DROP CONSTRAINT IF EXISTS "cursor_manifest_hash_format";
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_hash_format" CHECK (
    ("validator_hash" = 'legacy' OR "validator_hash" ~ '^[0-9a-f]{64}$|^unavailable$')
    AND ("schema_hash" = 'legacy' OR "schema_hash" ~ '^[0-9a-f]{64}$|^unavailable$')
    AND ("prompt_source_hash" = 'legacy' OR "prompt_source_hash" ~ '^[0-9a-f]{64}$|^unavailable$')
  );
--> statement-breakpoint

-- 2. `schema_version` của kết quả phải KHỚP payload thật.
--
-- Đây là chỗ dễ nói dối nhất: khai 2.0 ở cột, nhét payload 1.0 vào JSONB.
ALTER TABLE "cursor_analysis_result"
  DROP CONSTRAINT IF EXISTS "cursor_result_schema_matches_payload";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result"
  ADD CONSTRAINT "cursor_result_schema_matches_payload" CHECK (
    "payload"->>'schemaVersion' IS NULL
    OR "payload"->>'schemaVersion' = "schema_version"
  );
--> statement-breakpoint

-- 3. Kết quả phải cùng SCHEMA với bản kê của execution, và execution phải có
--    kiểm định ĐẠT. Dùng trigger vì CHECK không nhìn được sang bảng khác.
CREATE OR REPLACE FUNCTION cursor_result_semantic_lineage()
RETURNS TRIGGER AS $$
DECLARE
  manifest_schema text;
  validation_passed boolean;
BEGIN
  SELECT schema_version INTO manifest_schema
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.llm_execution_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'RESULT_WITHOUT_MANIFEST: execution % chua co ban ke',
      NEW.llm_execution_id;
  END IF;

  -- Bản kê cũ ('legacy') thuộc các lô lexical; không áp luật schema lên chúng.
  IF manifest_schema <> 'legacy' AND manifest_schema IS DISTINCT FROM NEW.schema_version THEN
    RAISE EXCEPTION
      'RESULT_SCHEMA_MISMATCH: ket qua schema % nhung ban ke execution la %',
      NEW.schema_version, manifest_schema;
  END IF;

  SELECT passed INTO validation_passed
    FROM analysis_validation
   WHERE llm_execution_id = NEW.llm_execution_id;

  IF FOUND AND validation_passed IS FALSE THEN
    RAISE EXCEPTION
      'RESULT_WITH_FAILED_VALIDATION: execution % co kiem dinh KHONG dat',
      NEW.llm_execution_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_result_semantic_lineage ON "cursor_analysis_result";
--> statement-breakpoint

CREATE TRIGGER cursor_result_semantic_lineage
  BEFORE INSERT OR UPDATE ON "cursor_analysis_result"
  FOR EACH ROW EXECUTE FUNCTION cursor_result_semantic_lineage();
