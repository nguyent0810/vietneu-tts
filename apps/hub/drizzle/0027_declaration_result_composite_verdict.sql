-- PAYLOAD của lượt KHAI BÁO, và MỘT phán quyết COMPOSITE duy nhất cho mỗi lần phân tích.
--
-- Hai thứ G4 còn thiếu, cả hai đều là điều kiện cần của chặng hợp nhất:
--
-- 1. Bản khai của lượt 2 chỉ tồn tại trong bộ nhớ. Chặng hợp nhất phải ĐỌC LẠI
--    nó từ database — nếu ghép từ object trong RAM thì không chứng minh được thứ
--    được ghép chính là thứ mô hình đã trả về và đã được kiểm định.
--
-- 2. `analysis_validation_execution_stage_key` chỉ cấm HAI dòng COMPOSITE trên
--    CÙNG một execution. Nó KHÔNG cấm hai lượt khai báo khác nhau của cùng một
--    lượt phân tích, mỗi lượt mang một phán quyết COMPOSITE riêng — tức hai kết
--    quả chính thức cạnh tranh nhau cho cùng một bài phân tích. Đó đúng là hình
--    dạng của "chạy lại tới khi được kết quả đẹp".
--
-- Bảng RIÊNG chứ không thêm giá trị vào `cursor_result_role`: `ALTER TYPE ... ADD
-- VALUE` có ràng buộc về transaction, và Drizzle chạy mỗi migration trong một
-- transaction. Bảng mới không có bẫy đó.

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'cursor_declaration_result') THEN
    RAISE EXCEPTION 'PREFLIGHT_0027: bang cursor_declaration_result DA TON TAI';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'cursor_claim_obligation') THEN
    RAISE EXCEPTION 'PREFLIGHT_0027: chua chay 0024 — thu tu migration sai';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name = 'analysis_validation' AND column_name = 'stage') THEN
    RAISE EXCEPTION 'PREFLIGHT_0027: chua chay 0025 — thu tu migration sai';
  END IF;
END $$;
--> statement-breakpoint

CREATE TABLE "cursor_declaration_result" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "workspace_id" uuid NOT NULL,
  "analysis_run_id" uuid NOT NULL,
  "channel_id" uuid NOT NULL,
  "request_id" uuid NOT NULL,
  -- Execution của lượt KHAI BÁO đã sinh ra bản khai này.
  "llm_execution_id" uuid NOT NULL,
  -- Lượt PHÂN TÍCH mà bản khai này phục vụ. Lặp lại ở đây (thay vì chỉ suy ra
  -- qua bản kê) để phép kiểm "một phán quyết duy nhất" đọc được trực tiếp.
  "analysis_execution_id" uuid NOT NULL,
  "analysis_payload_hash" text NOT NULL,
  "obligation_set_hash" text NOT NULL,
  "declaration_count" integer NOT NULL,
  "payload" jsonb NOT NULL,
  "payload_hash" text NOT NULL,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint

ALTER TABLE "cursor_declaration_result"
  ADD CONSTRAINT "cursor_declaration_workspace_fk"
  FOREIGN KEY ("workspace_id") REFERENCES "workspace" ("id") ON DELETE restrict;
--> statement-breakpoint

ALTER TABLE "cursor_declaration_result"
  ADD CONSTRAINT "cursor_declaration_execution_run_fk"
  FOREIGN KEY ("llm_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id") ON DELETE restrict;
--> statement-breakpoint

ALTER TABLE "cursor_declaration_result"
  ADD CONSTRAINT "cursor_declaration_analysis_run_fk"
  FOREIGN KEY ("analysis_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id") ON DELETE restrict;
--> statement-breakpoint

ALTER TABLE "cursor_declaration_result"
  ADD CONSTRAINT "cursor_declaration_request_run_channel_fk"
  FOREIGN KEY ("request_id", "workspace_id", "analysis_run_id", "channel_id")
  REFERENCES "cursor_analysis_request" ("id", "workspace_id", "analysis_run_id", "channel_id")
  ON DELETE restrict;
--> statement-breakpoint

-- Một execution khai báo -> đúng một bản khai đã lưu.
CREATE UNIQUE INDEX "cursor_declaration_execution_key"
  ON "cursor_declaration_result" USING btree ("llm_execution_id");
--> statement-breakpoint

CREATE INDEX "cursor_declaration_analysis_idx"
  ON "cursor_declaration_result" USING btree ("analysis_execution_id");
--> statement-breakpoint

ALTER TABLE "cursor_declaration_result"
  ADD CONSTRAINT "cursor_declaration_hash_format" CHECK (
    "analysis_payload_hash" ~ '^[0-9a-f]{64}$'
    AND "obligation_set_hash" ~ '^[0-9a-f]{64}$'
    AND "payload_hash" ~ '^[0-9a-f]{64}$'
  );
--> statement-breakpoint

ALTER TABLE "cursor_declaration_result"
  ADD CONSTRAINT "cursor_declaration_count_matches" CHECK (
    "declaration_count" = jsonb_array_length("payload" -> 'declarations')
  );
--> statement-breakpoint

-- Bản khai BẤT BIẾN, giống kết quả và giống tập nghĩa vụ.
CREATE OR REPLACE FUNCTION cursor_declaration_immutable()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_DECLARATION_RESULT: ban khai % la bat bien (thao tac: %)',
    OLD.id, TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER cursor_declaration_immutability
  BEFORE UPDATE OR DELETE ON "cursor_declaration_result"
  FOR EACH ROW EXECUTE FUNCTION cursor_declaration_immutable();
--> statement-breakpoint

-- MỘT phán quyết COMPOSITE cho MỖI lượt phân tích.
--
-- Không diễn đạt được bằng unique index: dòng COMPOSITE gắn vào execution KHAI
-- BÁO, còn thứ phải duy nhất là lượt PHÂN TÍCH đứng sau nó — quan hệ nằm ở bảng
-- khác. Trigger là chỗ duy nhất nhìn thấy cả hai.
CREATE OR REPLACE FUNCTION cursor_single_composite_verdict()
RETURNS TRIGGER AS $$
DECLARE
  my_analysis uuid;
  competing uuid;
BEGIN
  IF NEW.stage <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  SELECT analysis_execution_id INTO my_analysis
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.llm_execution_id;

  -- Đường MỘT LƯỢT cũ: không có lượt phân tích riêng, không có gì để so.
  IF my_analysis IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT v.llm_execution_id INTO competing
    FROM analysis_validation v
    JOIN cursor_execution_manifest m ON m.llm_execution_id = v.llm_execution_id
   WHERE v.stage = 'COMPOSITE'
     AND v.llm_execution_id <> NEW.llm_execution_id
     AND m.analysis_execution_id = my_analysis
   LIMIT 1;

  IF competing IS NOT NULL THEN
    RAISE EXCEPTION
      'COMPETING_COMPOSITE_VERDICT: luot phan tich % da co phan quyet COMPOSITE tu execution %',
      my_analysis, competing;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER analysis_validation_single_composite
  BEFORE INSERT ON "analysis_validation"
  FOR EACH ROW EXECUTE FUNCTION cursor_single_composite_verdict();
--> statement-breakpoint

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'cursor_declaration_execution_key') THEN
    RAISE EXCEPTION 'POSTCHECK_0027: thieu unique index ban khai';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_declaration_immutability') THEN
    RAISE EXCEPTION 'POSTCHECK_0027: thieu trigger bat bien ban khai';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'analysis_validation_single_composite') THEN
    RAISE EXCEPTION 'POSTCHECK_0027: thieu trigger phan quyet COMPOSITE duy nhat';
  END IF;
END $$;
