-- TẬP NGHĨA VỤ KHAI BÁO — do ỨNG DỤNG sinh, bất biến, neo vào đúng một lượt phân tích.
--
-- Đây là tầng thay cho nhóm quy tắc R và ba trên bốn quy tắc nhóm U của hợp đồng
-- một lượt. Bảo đảm KHÔNG tự nhiên có: nó chuyển từ "mô hình phải làm đúng" sang
-- "database không cho phép làm sai", nên mọi bất biến phải nằm ở đây chứ không
-- chỉ trong mã ứng dụng.
--
-- O-INV-1: tập nghĩa vụ thuộc ĐÚNG lần phân tích -> UNIQUE + khoá ngoại phức hợp.
-- O-INV-4: bất biến kể từ khi lượt khai báo bắt đầu -> trigger chặn UPDATE/DELETE.

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'cursor_claim_obligation') THEN
    RAISE EXCEPTION 'PREFLIGHT_0024: bang cursor_claim_obligation DA TON TAI';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name = 'cursor_execution_manifest' AND column_name = 'execution_role') THEN
    RAISE EXCEPTION 'PREFLIGHT_0024: chua chay 0023 — thu tu migration sai';
  END IF;
END $$;
--> statement-breakpoint

CREATE TABLE "cursor_claim_obligation" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "workspace_id" uuid NOT NULL,
  "analysis_run_id" uuid NOT NULL,
  "channel_id" uuid NOT NULL,
  "request_id" uuid NOT NULL,
  -- Lượt PHÂN TÍCH đã sinh ra tập này. Một lượt -> đúng một tập.
  "analysis_execution_id" uuid NOT NULL,
  -- Băm bản phân tích đã đóng băng. Nền của O-INV-1 ở tầng ứng dụng.
  "analysis_hash" text NOT NULL,
  -- Băm chính tập này. Lượt khai báo phải khai lại đúng giá trị này (O-INV-4).
  "obligation_set_hash" text NOT NULL,
  "generator_version" text NOT NULL,
  "obligation_count" integer NOT NULL,
  "obligations" jsonb NOT NULL,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint

ALTER TABLE "cursor_claim_obligation"
  ADD CONSTRAINT "cursor_obligation_workspace_fk"
  FOREIGN KEY ("workspace_id") REFERENCES "workspace" ("id") ON DELETE restrict;
--> statement-breakpoint

-- Lượt phân tích phải thuộc ĐÚNG workspace và ĐÚNG lần phân tích của tập này.
ALTER TABLE "cursor_claim_obligation"
  ADD CONSTRAINT "cursor_obligation_execution_run_fk"
  FOREIGN KEY ("analysis_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id") ON DELETE restrict;
--> statement-breakpoint

-- Request phải cùng lần phân tích VÀ cùng kênh — bao trọn gói bằng chứng.
ALTER TABLE "cursor_claim_obligation"
  ADD CONSTRAINT "cursor_obligation_request_run_channel_fk"
  FOREIGN KEY ("request_id", "workspace_id", "analysis_run_id", "channel_id")
  REFERENCES "cursor_analysis_request" ("id", "workspace_id", "analysis_run_id", "channel_id")
  ON DELETE restrict;
--> statement-breakpoint

-- O-INV-1, tầng database: MỘT lượt phân tích -> ĐÚNG MỘT tập nghĩa vụ.
--
-- Chú ý điều này KHÔNG cấm nhiều lượt KHAI BÁO cùng dùng một tập: lượt khai báo
-- không xuất hiện ở bảng này. Một lần thử lại khai báo dùng lại đúng hàng cũ,
-- nên bất biến duy nhất vẫn nguyên vẹn.
CREATE UNIQUE INDEX "cursor_obligation_analysis_execution_key"
  ON "cursor_claim_obligation" USING btree ("analysis_execution_id");
--> statement-breakpoint

CREATE INDEX "cursor_obligation_request_idx"
  ON "cursor_claim_obligation" USING btree ("request_id");
--> statement-breakpoint

ALTER TABLE "cursor_claim_obligation"
  ADD CONSTRAINT "cursor_obligation_hash_format" CHECK (
    "analysis_hash" ~ '^[0-9a-f]{64}$' AND "obligation_set_hash" ~ '^[0-9a-f]{64}$'
  );
--> statement-breakpoint

-- Số nghĩa vụ phải khớp mảng thật. Cột đếm rời có thể lệch với JSONB, và một cột
-- đếm sai là cách âm thầm nhất để "đủ nghĩa vụ" trở thành sai.
ALTER TABLE "cursor_claim_obligation"
  ADD CONSTRAINT "cursor_obligation_count_matches" CHECK (
    "obligation_count" = jsonb_array_length("obligations" -> 'obligations')
  );
--> statement-breakpoint

-- Tập nghĩa vụ phải tự khai đúng băm bản phân tích của nó.
ALTER TABLE "cursor_claim_obligation"
  ADD CONSTRAINT "cursor_obligation_payload_hash_matches" CHECK (
    "obligations" ->> 'analysisHash' = "analysis_hash"
  );
--> statement-breakpoint

-- O-INV-4: BẤT BIẾN. Muốn đổi tập nghĩa vụ thì phải chạy lại LƯỢT PHÂN TÍCH.
-- Không có đường sửa tại chỗ, y như `cursor_analysis_result`.
CREATE OR REPLACE FUNCTION cursor_obligation_immutable()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_OBLIGATION_SET: tap nghia vu % la bat bien (thao tac: %)',
    OLD.id, TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER cursor_obligation_immutability
  BEFORE UPDATE OR DELETE ON "cursor_claim_obligation"
  FOR EACH ROW EXECUTE FUNCTION cursor_obligation_immutable();
--> statement-breakpoint

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes
                  WHERE indexname = 'cursor_obligation_analysis_execution_key') THEN
    RAISE EXCEPTION 'POSTCHECK_0024: thieu unique index analysis_execution';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_obligation_immutability') THEN
    RAISE EXCEPTION 'POSTCHECK_0024: thieu trigger bat bien';
  END IF;
END $$;
