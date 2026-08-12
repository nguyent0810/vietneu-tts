-- BẢN KÊ EXECUTION là BẤT BIẾN — bảng cuối cùng trong chuỗi còn sửa/xoá được.
--
-- Rà soát độc lập chỉ ra: trong toàn bộ chuỗi cấp phép, bốn bảng đã được khoá
-- (`analysis_validation`, `cursor_analysis_result`, `cursor_claim_obligation`,
-- `cursor_declaration_result` — tất cả đều có trigger BEFORE UPDATE OR DELETE),
-- nhưng `cursor_execution_manifest` thì KHÔNG:
--
--   * `cursor_manifest_declaration_lineage` (0031) chỉ chạy BEFORE **INSERT**;
--   * `cursor_repair_version_immutable` (0023) có chạy trên UPDATE nhưng trả
--     `NEW` ngay nếu `parent_execution_id IS NULL`, tức bỏ qua mọi hàng gốc;
--   * KHÔNG khoá ngoại nào trỏ tới bảng này, nên DELETE không bị cản.
--
-- Hai đường khai thác cụ thể, cả hai đều vô hiệu hoá công sức của 0031:
--
--   (A) VƯỢT TRẦN LẦN THỬ. Chèn bản kê với vai ANALYSIS (trigger 0031 trả NEW
--       ngay vì vai không phải DECLARATION), rồi UPDATE nó thành DECLARATION kèm
--       lineage. Trần đếm-theo-số-hàng không bao giờ được xét. Lặp lại tuỳ ý:
--       đúng kiểu "tạo 100 lượt khai báo rồi chọn cái đẹp nhất" mà 0031 sinh ra
--       để chặn. Cùng đường này cũng lách được `DECLARATION_ANALYSIS_WRONG_ROLE`.
--
--   (B) XOÁ BẰNG CHỨNG + ĐẶT LẠI TRẦN. `DELETE FROM cursor_execution_manifest
--       WHERE analysis_execution_id = A AND execution_role = 'DECLARATION'` chạy
--       trót lọt. Các phán quyết trượt vẫn còn (chúng được khoá), nhưng mọi truy
--       vấn dựng lại "lần thử đó là gì" đều JOIN qua bản kê — nên bằng chứng trở
--       thành không đọc được, VÀ trần lần thử về 0.
--
-- Cách sửa: bất biến TOÀN PHẦN, giống hệt bốn bảng kia. Không nơi nào trong mã
-- sửa hay xoá bản kê (đã kiểm bằng grep trên `src/`, `tests/`, `*.mjs`), nên
-- khoá toàn phần không chặn đường ghi hợp lệ nào. Dọn dữ liệu test dùng TRUNCATE,
-- vốn không kích hoạt trigger hàng.
--
-- HẠN CHẾ, nói thẳng: đây là ràng buộc trong database, không phải attestation.
-- Superuser vẫn `ALTER TABLE ... DISABLE TRIGGER` được.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_manifest_declaration_lineage') THEN
    RAISE EXCEPTION 'PREFLIGHT_0034: chua chay 0031';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_manifest_immutability') THEN
    RAISE EXCEPTION 'PREFLIGHT_0034: migration nay da chay?';
  END IF;
END $$;
--> statement-breakpoint

CREATE OR REPLACE FUNCTION enforce_cursor_manifest_immutability()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION
      'IMMUTABLE_CURSOR_MANIFEST: khong duoc xoa ban ke % (vai %, lan thu %)',
      OLD.llm_execution_id, OLD.execution_role, OLD.attempt_number;
  END IF;
  RAISE EXCEPTION
    'IMMUTABLE_CURSOR_MANIFEST: khong duoc sua ban ke % (vai %, lan thu %)',
    OLD.llm_execution_id, OLD.execution_role, OLD.attempt_number;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_manifest_immutability ON "cursor_execution_manifest";
--> statement-breakpoint

CREATE TRIGGER cursor_manifest_immutability
  BEFORE UPDATE OR DELETE ON "cursor_execution_manifest"
  FOR EACH ROW EXECUTE FUNCTION enforce_cursor_manifest_immutability();
--> statement-breakpoint

DO $$
DECLARE
  mask smallint;
BEGIN
  SELECT tgtype INTO mask FROM pg_trigger WHERE tgname = 'cursor_manifest_immutability';
  IF mask IS NULL THEN
    RAISE EXCEPTION 'POSTCHECK_0034: thieu trigger bat bien ban ke';
  END IF;
  -- bit 3 = DELETE (8), bit 4 = UPDATE (16). Phải có CẢ HAI.
  IF (mask & 8) = 0 THEN
    RAISE EXCEPTION 'POSTCHECK_0034: trigger khong chay tren DELETE (tgtype=%)', mask;
  END IF;
  IF (mask & 16) = 0 THEN
    RAISE EXCEPTION 'POSTCHECK_0034: trigger khong chay tren UPDATE (tgtype=%)', mask;
  END IF;
  -- Trigger cua 0031 phai con nguyen: no canh duong INSERT.
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_manifest_declaration_lineage') THEN
    RAISE EXCEPTION 'POSTCHECK_0034: da lam mat trigger lineage cua 0031';
  END IF;
END $$;
