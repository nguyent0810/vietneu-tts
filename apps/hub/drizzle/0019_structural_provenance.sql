-- Nguồn gốc PHIÊN BẢN thành cột thật, không nằm trong JSONB.
--
-- Trước đó, phiên bản schema/prompt và các băm mã nguồn chỉ tồn tại trong
-- `payload` (JSONB) hoặc trong log. Hệ quả:
--   * không truy vấn được "lô này chạy bằng validator nào";
--   * không ràng buộc được chuỗi retry phải cùng phiên bản;
--   * một worker cũ có thể tạo chuỗi retry TRỘN phiên bản mà không gì chặn.
--
-- Các cột dưới đây được gắn LÚC TẠO execution, không suy ngược từ artifact sau
-- khi chạy — suy ngược là tự đọc lại chính thứ mình vừa ghi.

ALTER TABLE "cursor_execution_manifest"
  ADD COLUMN IF NOT EXISTS "schema_version" text,
  ADD COLUMN IF NOT EXISTS "prompt_version" text,
  ADD COLUMN IF NOT EXISTS "validator_hash" text,
  ADD COLUMN IF NOT EXISTS "schema_hash" text,
  ADD COLUMN IF NOT EXISTS "prompt_source_hash" text;
--> statement-breakpoint

-- Dòng cũ (lô lexical) không có các giá trị này; đánh dấu rõ là 'legacy' thay
-- vì để NULL, để truy vấn phân biệt được "chưa có" với "không áp dụng".
UPDATE "cursor_execution_manifest"
  SET "schema_version" = COALESCE("schema_version", 'legacy'),
      "prompt_version" = COALESCE("prompt_version", 'legacy'),
      "validator_hash" = COALESCE("validator_hash", 'legacy'),
      "schema_hash" = COALESCE("schema_hash", 'legacy'),
      "prompt_source_hash" = COALESCE("prompt_source_hash", 'legacy');
--> statement-breakpoint

ALTER TABLE "cursor_execution_manifest"
  ALTER COLUMN "schema_version" SET NOT NULL,
  ALTER COLUMN "prompt_version" SET NOT NULL,
  ALTER COLUMN "validator_hash" SET NOT NULL,
  ALTER COLUMN "schema_hash" SET NOT NULL,
  ALTER COLUMN "prompt_source_hash" SET NOT NULL;
--> statement-breakpoint

CREATE INDEX IF NOT EXISTS "cursor_manifest_validator_hash_idx"
  ON "cursor_execution_manifest" ("validator_hash");
--> statement-breakpoint

-- CHUỖI RETRY KHÔNG ĐƯỢC TRỘN PHIÊN BẢN.
--
-- Ràng buộc ở tầng database, không chỉ ở ứng dụng: một worker cũ còn chạy song
-- song vẫn có thể ghi thẳng vào bảng. Trigger so từng giá trị với bản kê của
-- execution cha.
CREATE OR REPLACE FUNCTION cursor_repair_version_immutable()
RETURNS TRIGGER AS $$
DECLARE
  parent RECORD;
BEGIN
  IF NEW.parent_execution_id IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT schema_version, prompt_version, validator_hash, schema_hash, prompt_source_hash
    INTO parent
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.parent_execution_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'REPAIR_PARENT_MISSING: khong tim thay ban ke cua execution cha %',
      NEW.parent_execution_id;
  END IF;

  IF parent.schema_version   IS DISTINCT FROM NEW.schema_version
  OR parent.prompt_version   IS DISTINCT FROM NEW.prompt_version
  OR parent.validator_hash   IS DISTINCT FROM NEW.validator_hash
  OR parent.schema_hash      IS DISTINCT FROM NEW.schema_hash
  OR parent.prompt_source_hash IS DISTINCT FROM NEW.prompt_source_hash THEN
    RAISE EXCEPTION
      'MIXED_VERSION_REPAIR_CHAIN: lan sua loi dung phien ban khac execution cha %',
      NEW.parent_execution_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_repair_version_immutable ON "cursor_execution_manifest";
--> statement-breakpoint

CREATE TRIGGER cursor_repair_version_immutable
  BEFORE INSERT OR UPDATE ON "cursor_execution_manifest"
  FOR EACH ROW EXECUTE FUNCTION cursor_repair_version_immutable();
