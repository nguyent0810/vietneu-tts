-- LƯỢT KHAI BÁO: vai của execution + nguồn gốc SÁU HỢP ĐỒNG.
--
-- Kiến trúc hai lượt: lượt PHÂN TÍCH sinh văn xuôi, lượt KHAI BÁO điền ngữ nghĩa
-- cho tập nghĩa vụ do ứng dụng sinh. Hai lượt là hai execution, nối với nhau
-- bằng `analysis_execution_id` — KHÔNG bằng `parent_execution_id`.
--
-- Vì sao phân biệt hai cột: `parent_execution_id` là chuỗi THỬ LẠI trong cùng
-- một lượt, và trigger `cursor_repair_version_immutable` (0020) đòi cha–con cùng
-- phiên bản. Nối lượt khai báo vào lượt phân tích bằng cột đó sẽ khiến 0020 từ
-- chối (hai lượt dùng prompt khác nhau) — và 0020 từ chối là ĐÚNG, vì nó được
-- viết cho chuỗi sửa lỗi. Nên ta thêm một quan hệ MỚI thay vì nới quan hệ cũ.
--
-- TIỀN KIỂM: dừng nếu trạng thái tiền nhiệm không như mong đợi.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables
                  WHERE table_name = 'cursor_execution_manifest') THEN
    RAISE EXCEPTION 'PREFLIGHT_0023: khong tim thay bang cursor_execution_manifest';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
              WHERE table_name = 'cursor_execution_manifest' AND column_name = 'execution_role') THEN
    RAISE EXCEPTION 'PREFLIGHT_0023: cot execution_role DA TON TAI — migration nay da chay?';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cursor_repair_version_immutable') THEN
    RAISE EXCEPTION 'PREFLIGHT_0023: thieu trigger 0020 — thu tu migration sai';
  END IF;
END $$;
--> statement-breakpoint

DO $$
BEGIN
  CREATE TYPE "cursor_execution_role" AS ENUM ('ANALYSIS', 'DECLARATION');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
--> statement-breakpoint

-- Mọi execution cũ là lượt PHÂN TÍCH: chúng sinh ra văn xuôi kèm claim của
-- hợp đồng một lượt. Mặc định này là TẤT ĐỊNH và không cần UPDATE nào.
ALTER TABLE "cursor_execution_manifest"
  ADD COLUMN "execution_role" "cursor_execution_role" NOT NULL DEFAULT 'ANALYSIS';
--> statement-breakpoint

ALTER TABLE "cursor_execution_manifest" ADD COLUMN "analysis_execution_id" uuid;
--> statement-breakpoint

-- NGUỒN GỐC: sáu hợp đồng, sáu phiên bản. `schema_version`/`prompt_version`/
-- `validator_hash`/`schema_hash`/`prompt_source_hash` đã có từ 0019 và giữ
-- nguyên vai trò cho lượt PHÂN TÍCH. Bốn cột dưới đây là phần của lượt KHAI BÁO
-- và của bộ sinh nghĩa vụ; hai cột băm cuối là băm DỮ LIỆU, không phải mã.
--
-- Nullable vì chỉ lượt khai báo mới có; CHECK bên dưới cưỡng chế "có khi cần".
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "obligation_generator_version" text;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "declaration_prompt_version" text;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "declaration_prompt_source_hash" text;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "composite_validator_version" text;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "analysis_payload_hash" text;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "obligation_set_hash" text;
--> statement-breakpoint

-- Lượt khai báo phải trỏ tới một execution CÓ THẬT, CÙNG workspace và CÙNG lần
-- phân tích. Khoá ngoại đơn theo id sẽ cho phép trỏ sang lần chạy khác.
ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_analysis_execution_run_fk"
  FOREIGN KEY ("analysis_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id")
  ON DELETE restrict ON UPDATE no action;
--> statement-breakpoint

-- Vai và lineage phải khớp nhau, cả hai chiều:
--   DECLARATION -> BẮT BUỘC có analysis_execution_id và bộ nguồn gốc lượt 2;
--   ANALYSIS    -> KHÔNG được có (nếu có thì nó đang tự nhận là lượt khai báo).
ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_role_lineage" CHECK (
    (
      "execution_role" = 'DECLARATION'
      AND "analysis_execution_id" IS NOT NULL
      AND "obligation_generator_version" IS NOT NULL
      AND "declaration_prompt_version" IS NOT NULL
      AND "declaration_prompt_source_hash" IS NOT NULL
      AND "composite_validator_version" IS NOT NULL
      AND "analysis_payload_hash" IS NOT NULL
      AND "obligation_set_hash" IS NOT NULL
    )
    OR (
      "execution_role" = 'ANALYSIS'
      AND "analysis_execution_id" IS NULL
    )
  );
--> statement-breakpoint

-- Băm phải đúng định dạng sha256, giống `cursor_manifest_hash_format` của 0019.
ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_declaration_hash_format" CHECK (
    ("declaration_prompt_source_hash" IS NULL OR "declaration_prompt_source_hash" ~ '^[0-9a-f]{64}$')
    AND ("analysis_payload_hash" IS NULL OR "analysis_payload_hash" ~ '^[0-9a-f]{64}$')
    AND ("obligation_set_hash" IS NULL OR "obligation_set_hash" ~ '^[0-9a-f]{64}$')
  );
--> statement-breakpoint

-- 0020 nay so CẢ SÁU hợp đồng, không chỉ năm cột cũ.
--
-- Đây là thay đổi CỘNG THÊM, không đổi phạm vi: trigger vẫn chỉ chạy khi
-- `parent_execution_id` khác NULL, tức vẫn chỉ áp cho chuỗi THỬ LẠI. Một lần sửa
-- lỗi đổi bộ sinh nghĩa vụ hay prompt khai báo là đang sửa một bài toán khác, và
-- phải bị chặn y như đổi validator.
CREATE OR REPLACE FUNCTION cursor_repair_version_immutable()
RETURNS TRIGGER AS $$
DECLARE
  parent RECORD;
BEGIN
  IF NEW.parent_execution_id IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT schema_version, prompt_version, validator_hash, schema_hash,
         prompt_source_hash, request_id, analysis_run_id, execution_role,
         obligation_generator_version, declaration_prompt_version,
         declaration_prompt_source_hash, composite_validator_version
    INTO parent
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.parent_execution_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'REPAIR_PARENT_MISSING: khong tim thay ban ke cua execution cha %',
      NEW.parent_execution_id;
  END IF;

  IF parent.schema_version     IS DISTINCT FROM NEW.schema_version
  OR parent.prompt_version     IS DISTINCT FROM NEW.prompt_version
  OR parent.validator_hash     IS DISTINCT FROM NEW.validator_hash
  OR parent.schema_hash        IS DISTINCT FROM NEW.schema_hash
  OR parent.prompt_source_hash IS DISTINCT FROM NEW.prompt_source_hash
  OR parent.obligation_generator_version   IS DISTINCT FROM NEW.obligation_generator_version
  OR parent.declaration_prompt_version     IS DISTINCT FROM NEW.declaration_prompt_version
  OR parent.declaration_prompt_source_hash IS DISTINCT FROM NEW.declaration_prompt_source_hash
  OR parent.composite_validator_version    IS DISTINCT FROM NEW.composite_validator_version THEN
    RAISE EXCEPTION
      'MIXED_VERSION_REPAIR_CHAIN: lan sua loi dung phien ban khac execution cha %',
      NEW.parent_execution_id;
  END IF;

  -- Chuỗi thử lại phải ở CÙNG MỘT LƯỢT. Một lần "sửa lỗi" đổi vai là đang nối
  -- hai việc khác nhau vào một chuỗi.
  IF parent.execution_role IS DISTINCT FROM NEW.execution_role THEN
    RAISE EXCEPTION
      'MIXED_ROLE_REPAIR_CHAIN: lan sua loi vai % nhung execution cha vai %',
      NEW.execution_role, parent.execution_role;
  END IF;

  -- Cùng request => cùng gói bằng chứng, cùng kênh, cùng lần phân tích.
  IF parent.request_id IS DISTINCT FROM NEW.request_id THEN
    RAISE EXCEPTION
      'REPAIR_REQUEST_DRIFT: lan sua loi thuoc request khac (% vs %)',
      NEW.request_id, parent.request_id;
  END IF;

  IF parent.analysis_run_id IS DISTINCT FROM NEW.analysis_run_id THEN
    RAISE EXCEPTION
      'REPAIR_RUN_DRIFT: lan sua loi thuoc lan phan tich khac (% vs %)',
      NEW.analysis_run_id, parent.analysis_run_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

-- HẬU KIỂM trong CÙNG transaction: sai thì cả tệp cuộn lại.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name = 'cursor_execution_manifest'
                    AND column_name = 'execution_role' AND is_nullable = 'NO') THEN
    RAISE EXCEPTION 'POSTCHECK_0023: execution_role thieu hoac nullable';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint
                  WHERE conname = 'cursor_manifest_analysis_execution_run_fk') THEN
    RAISE EXCEPTION 'POSTCHECK_0023: thieu khoa ngoai analysis_execution';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'cursor_manifest_role_lineage') THEN
    RAISE EXCEPTION 'POSTCHECK_0023: thieu CHECK role/lineage';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_repair_version_immutable')
     NOT LIKE '%MIXED_ROLE_REPAIR_CHAIN%' THEN
    RAISE EXCEPTION 'POSTCHECK_0023: trigger 0020 chua duoc cap nhat';
  END IF;
END $$;
