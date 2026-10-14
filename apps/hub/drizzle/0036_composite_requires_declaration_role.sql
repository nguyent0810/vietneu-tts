-- HIỆN VẬT HỢP NHẤT phải đến từ execution vai DECLARATION.
--
-- ## ĐƯỜNG CHẠY NÀO bị ảnh hưởng (nêu TRƯỚC dòng SQL đầu tiên)
--
-- Bài học lặp ba lần của 0029→0030 và 0031→0032→0033: nêu rõ phạm vi TRƯỚC khi
-- viết SQL, vì cây mã mang cả kiến trúc một lượt lẫn hai lượt.
--
--   * ÁP CHO: INSERT hàng `cursor_analysis_result` có `result_role='COMPOSITE'`
--     mà bản kê của nó KHÔNG mang vai `DECLARATION`.
--   * KHÔNG áp cho: hàng đã tồn tại (trigger chỉ chạy BEFORE INSERT — 32 hàng
--     một lượt trong database CHÍNH giữ nguyên hiệu lực, đúng như 0026 chủ ý).
--   * KHÔNG áp cho: đường hai lượt (vai DECLARATION) — không đổi một chữ.
--   * KHÔNG áp cho: hàng `result_role='ANALYSIS'` (văn xuôi đóng băng của lượt 1).
--
-- Đã kiểm trước khi viết: `run.ts` chỉ có thể ghi `role: 'ANALYSIS'` (kiểu của
-- `persistResult.role` là literal đúng một giá trị), và `composite.ts` là nơi
-- DUY NHẤT ghi `resultRole: 'COMPOSITE'`, luôn trên execution vai DECLARATION.
-- Nên migration này KHÔNG chặn đường ghi nào đang chạy.
--
-- ## Vì sao cần
--
-- `cursor_result_semantic_lineage` (0033) đặt TOÀN BỘ phần kiểm nghiêm ngặt —
-- lineage phân tích↔khai báo, băm tập nghĩa vụ, và sự TỒN TẠI của bản khai đã
-- lưu — bên trong `IF m.execution_role = 'DECLARATION'`.
--
-- (Đính chính: 0033 chỉ kiểm bản khai TỒN TẠI, KHÔNG so băm của nó với bản kê.
-- Câu trước đây ở đây nói quá phạm vi 0033. Phép so ấy được 0037 bổ sung.) Với một bản
-- kê vai ANALYSIS, mọi phép kiểm ấy bị BỎ QUA, và điều kiện còn lại chỉ là "có
-- một dòng `analysis_validation` chặng COMPOSITE với passed = true".
--
-- Cộng thêm hai giá trị mặc định — `analysis_validation.stage` DEFAULT
-- 'COMPOSITE' (0025) và `cursor_analysis_result.result_role` DEFAULT 'COMPOSITE'
-- (0026) — thì một script chỉ cần chèn ba hàng tối thiểu, KHÔNG nêu vai nào cả,
-- là sinh ra một "hiện vật chính thức" không có tập nghĩa vụ, không có bản khai,
-- không có lineage. Lặp N lần cho ra N hiện vật chính thức cạnh tranh nhau trên
-- cùng một kênh: hai trigger duy nhất đếm trùng lặp (0028/0032) đều `RETURN NEW`
-- ngay khi `analysis_execution_id IS NULL`, nên chúng mù với hình dạng này.
--
-- Đây là đường CẤP PHÉP không qua cổng — đúng thứ mà cả tầng này sinh ra để
-- chặn. Giữ tương thích ĐỌC cho dữ liệu cũ là đúng; để ngỏ đường GHI thì không.

CREATE OR REPLACE FUNCTION cursor_composite_requires_declaration_role()
RETURNS TRIGGER AS $$
DECLARE
  exec_role text;
BEGIN
  IF NEW.result_role <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  SELECT m.execution_role::text INTO exec_role
    FROM cursor_execution_manifest m
   WHERE m.llm_execution_id = NEW.llm_execution_id;

  -- Không tìm thấy bản kê: để `cursor_result_semantic_lineage` báo lỗi của nó,
  -- đừng che mất chẩn đoán cụ thể hơn bằng một lỗi chung chung ở đây.
  IF NOT FOUND THEN
    RETURN NEW;
  END IF;

  IF exec_role <> 'DECLARATION' THEN
    RAISE EXCEPTION
      'COMPOSITE_REQUIRES_DECLARATION_ROLE: execution % co vai % — hien vat hop nhat MOI phai den tu luot khai bao. Hang mot luot cu van hop le nhung khong duoc tao them.',
      NEW.llm_execution_id, exec_role;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cursor_composite_requires_declaration_role_trg ON cursor_analysis_result;
DROP TRIGGER IF EXISTS a_cursor_composite_requires_declaration_role_trg ON cursor_analysis_result;

-- Tên phải sắp xếp SAU `cursor_result_semantic_lineage`.
--
-- PostgreSQL gọi trigger BEFORE cùng bảng theo thứ tự TÊN. Bản đầu của migration
-- này đặt tiền tố `a_` để chạy TRƯỚC — sai, và 0033 đã cảnh báo trước đúng cái
-- bẫy ấy ("trigger riêng chạy theo thứ tự tên và sẽ che mất mọi chẩn đoán cụ thể
-- ở trên"). Hệ quả đo được: hai test đang đòi `RESULT_SCHEMA_MISMATCH` và
-- `RESULT_WITH_FAILED_VALIDATION` nhận về thông điệp về VAI, tức lỗi cụ thể bị
-- một lỗi tổng quát hơn che mất.
--
-- Chạy SAU thì mọi chẩn đoán hẹp hơn được báo trước, và phép kiểm vai chỉ lên
-- tiếng khi hàng đã hợp lệ về mọi mặt khác — đúng vai trò của nó.
CREATE TRIGGER cursor_z_composite_requires_declaration_role_trg
BEFORE INSERT ON cursor_analysis_result
FOR EACH ROW EXECUTE FUNCTION cursor_composite_requires_declaration_role();
