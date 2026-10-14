-- CHẶNG KIỂM ĐỊNH: một execution có thể có nhiều dòng kiểm định, mỗi chặng một dòng.
--
-- ===================== MIGRATION RỦI RO CAO =====================
--
-- Đây là migration DUY NHẤT của loạt này NỚI LỎNG một ràng buộc duy nhất trên
-- bảng ĐANG CÓ DỮ LIỆU. Trước: một execution tối đa MỘT dòng kiểm định. Sau: tối
-- đa BA (ANALYSIS, DECLARATION, COMPOSITE).
--
-- Cái bẫy đã được xác minh trước khi viết tệp này: `analysis_validation_execution_key`
-- là một UNIQUE INDEX, KHÔNG phải một CONSTRAINT (`pg_constraint` rỗng ở cả hai
-- database). `DROP CONSTRAINT IF EXISTS` sẽ chạy "thành công" mà KHÔNG gỡ gì, rồi
-- index mới được dựng bên cạnh index cũ, và index cũ tiếp tục chặn dòng thứ hai —
-- một migration báo thành công trong khi kiến trúc ba chặng hỏng ngay lần ghi đầu.
-- Vì vậy: DROP INDEX, và HẬU KIỂM ngay trong cùng transaction.
--
-- Backfill: cột thêm với DEFAULT 'COMPOSITE' nên mọi dòng cũ nhận COMPOSITE mà
-- KHÔNG cần UPDATE nào. Điều đó quan trọng gấp đôi ở đây vì
-- `analysis_validation_immutability` (0011) chặn mọi UPDATE — 0017 đã từng phải
-- DISABLE trigger để backfill. Dùng DEFAULT thì không phải đụng vào trigger.
-- COMPOSITE là đúng nghĩa với dòng cũ: chúng là PHÁN QUYẾT CUỐI của hợp đồng
-- một lượt.

-- BƯỚC 1 — TIỀN KIỂM. Dừng nếu trạng thái tiền nhiệm khác mong đợi.
DO $$
DECLARE
  dup_count integer;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'analysis_validation_execution_key') THEN
    RAISE EXCEPTION 'PREFLIGHT_0025: khong tim thay index tien nhiem analysis_validation_execution_key';
  END IF;

  IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'analysis_validation_execution_stage_key') THEN
    RAISE EXCEPTION 'PREFLIGHT_0025: index moi DA TON TAI — migration nay da chay?';
  END IF;

  IF EXISTS (SELECT 1 FROM information_schema.columns
              WHERE table_name = 'analysis_validation' AND column_name = 'stage') THEN
    RAISE EXCEPTION 'PREFLIGHT_0025: cot stage DA TON TAI';
  END IF;

  SELECT count(*) INTO dup_count FROM (
    SELECT llm_execution_id FROM analysis_validation
     GROUP BY llm_execution_id HAVING count(*) > 1
  ) d;
  IF dup_count > 0 THEN
    RAISE EXCEPTION 'PREFLIGHT_0025: da co % execution trung dong kiem dinh', dup_count;
  END IF;
END $$;
--> statement-breakpoint

DO $$
BEGIN
  CREATE TYPE "validation_stage" AS ENUM ('ANALYSIS', 'DECLARATION', 'COMPOSITE');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
--> statement-breakpoint

-- Backfill TẤT ĐỊNH qua DEFAULT: không UPDATE, không đụng trigger bất biến.
ALTER TABLE "analysis_validation"
  ADD COLUMN "stage" "validation_stage" NOT NULL DEFAULT 'COMPOSITE';
--> statement-breakpoint

-- BƯỚC 2 — GỠ index cũ. DROP INDEX, KHÔNG phải DROP CONSTRAINT.
DROP INDEX IF EXISTS "analysis_validation_execution_key";
--> statement-breakpoint

-- BƯỚC 3 — HẬU KIỂM việc gỡ, TRONG CÙNG TRANSACTION.
-- Soi CẢ HAI catalog: một unique index có thể tồn tại mà không có constraint
-- tương ứng, và ngược lại.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'analysis_validation_execution_key') THEN
    RAISE EXCEPTION 'POSTCHECK_0025: index CU van con sau khi DROP — cuon lai';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'analysis_validation_execution_key') THEN
    RAISE EXCEPTION 'POSTCHECK_0025: constraint CU van con sau khi DROP — cuon lai';
  END IF;
END $$;
--> statement-breakpoint

CREATE UNIQUE INDEX "analysis_validation_execution_stage_key"
  ON "analysis_validation" USING btree ("llm_execution_id", "stage");
--> statement-breakpoint

-- BƯỚC 4 — HẬU KIỂM ĐỊNH NGHĨA index mới: đúng cột, đúng thứ tự, đúng UNIQUE,
-- và KHÔNG có điều kiện lọc (partial index sẽ chỉ cưỡng chế trên một phần bảng).
DO $$
DECLARE
  def text;
BEGIN
  SELECT indexdef INTO def FROM pg_indexes
   WHERE indexname = 'analysis_validation_execution_stage_key';
  IF def IS NULL THEN
    RAISE EXCEPTION 'POSTCHECK_0025: khong tao duoc index moi';
  END IF;
  IF def NOT LIKE 'CREATE UNIQUE INDEX%' THEN
    RAISE EXCEPTION 'POSTCHECK_0025: index moi KHONG unique: %', def;
  END IF;
  IF def NOT LIKE '%(llm_execution_id, stage)%' THEN
    RAISE EXCEPTION 'POSTCHECK_0025: index moi sai cot hoac sai thu tu: %', def;
  END IF;
  IF def LIKE '%WHERE%' THEN
    RAISE EXCEPTION 'POSTCHECK_0025: index moi la PARTIAL, chi cuong che mot phan bang: %', def;
  END IF;
  IF EXISTS (SELECT 1 FROM analysis_validation WHERE stage IS NULL) THEN
    RAISE EXCEPTION 'POSTCHECK_0025: con dong co stage NULL';
  END IF;
END $$;
