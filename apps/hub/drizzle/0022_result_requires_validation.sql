-- Kết quả BẮT BUỘC phải có dòng kiểm định ĐẠT, và payload phải khai schema.
--
-- 0021 mới chặn khi có dòng kiểm định KHÔNG đạt. Vắng mặt thì được cho qua:
--   ghi bản kê -> BỎ QUA kiểm định -> ghi kết quả  => database chấp nhận một
-- "kết quả đã kiểm định" chưa hề được kiểm định. Worker bình thường ghi đúng
-- thứ tự, nhưng ghi thẳng hoặc worker cũ thì lọt.
--
-- Tương tự, CHECK cũ cho phép `payload->>'schemaVersion' IS NULL`, nên một
-- payload hình dạng schema-1 (không có trường version) vẫn ghi được vào cột
-- khai 2.0.

ALTER TABLE "cursor_analysis_result"
  DROP CONSTRAINT IF EXISTS "cursor_result_schema_matches_payload";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result"
  ADD CONSTRAINT "cursor_result_schema_matches_payload" CHECK (
    "payload"->>'schemaVersion' IS NOT NULL
    AND "payload"->>'schemaVersion' = "schema_version"
  );
--> statement-breakpoint

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

  IF manifest_schema <> 'legacy' AND manifest_schema IS DISTINCT FROM NEW.schema_version THEN
    RAISE EXCEPTION
      'RESULT_SCHEMA_MISMATCH: ket qua schema % nhung ban ke execution la %',
      NEW.schema_version, manifest_schema;
  END IF;

  SELECT passed INTO validation_passed
    FROM analysis_validation
   WHERE llm_execution_id = NEW.llm_execution_id;

  -- FAIL-CLOSED: thiếu dòng kiểm định cũng bị từ chối, không chỉ khi nó FALSE.
  IF NOT FOUND THEN
    RAISE EXCEPTION
      'RESULT_WITHOUT_VALIDATION: execution % chua co dong kiem dinh',
      NEW.llm_execution_id;
  END IF;

  IF validation_passed IS NOT TRUE THEN
    RAISE EXCEPTION
      'RESULT_WITH_FAILED_VALIDATION: execution % co kiem dinh KHONG dat',
      NEW.llm_execution_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
