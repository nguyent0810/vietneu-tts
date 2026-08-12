-- BẢN KHAI ĐÃ LƯU phải KHỚP bản kê, không chỉ TỒN TẠI.
--
-- ## ĐƯỜNG CHẠY NÀO bị ảnh hưởng (nêu TRƯỚC dòng SQL đầu tiên)
--
--   * ÁP CHO: INSERT hàng `cursor_analysis_result` vai COMPOSITE trên execution
--     vai DECLARATION — tức ĐÚNG một đường: đường hai lượt đang chạy.
--   * KHÔNG áp cho: hàng đã tồn tại (BEFORE INSERT), hàng vai ANALYSIS, và
--     đường một lượt (0036 đã chặn ghi mới).
--
-- Đã kiểm trước khi viết: `run.ts` ghi bản kê lượt khai báo từ `declProvenance`
-- (`analysisPayloadHash`, `obligationSetHash`) và ghi `cursor_declaration_result`
-- từ CÙNG các giá trị ấy, `analysis_execution_id` cùng trỏ execution lượt phân
-- tích. Nên siết ở đây KHÔNG chặn đường ghi nào đang chạy.
--
-- ## Vì sao THÊM TRIGGER chứ không SỬA `cursor_result_semantic_lineage`
--
-- Bản nháp đầu của migration này viết lại cả hàm ấy. So lại danh sách ngoại lệ
-- thì bản viết lại đã ĐÁNH RƠI năm phép kiểm: `RESULT_LINEAGE_DRIFT`,
-- `RESULT_MANIFEST_LINEAGE_DRIFT`, `RESULT_WITHOUT_ANALYSIS_VALIDATION`,
-- `RESULT_WITHOUT_OBLIGATION_SET`, `RESULT_WITH_FAILED_ANALYSIS` — tức bản sửa
-- một lỗ đã tự mở năm lỗ khác. Đúng khuôn mẫu mà 0029→0030 và 0031→0032→0033
-- đã lặp ba lần.
--
-- Thêm một trigger HẸP thì không thể đánh rơi gì: nó chỉ cộng thêm điều kiện.
--
-- Tên sắp xếp SAU `cursor_result_semantic_lineage` để mọi chẩn đoán cụ thể hơn
-- của hàm ấy được báo trước.
--
-- ## Vì sao cần
--
-- 0033 kết thúc bằng một phép kiểm CHỈ hỏi "có tồn tại bản khai nào cho
-- execution này không". Nó KHÔNG so `analysis_execution_id`, KHÔNG so
-- `analysis_payload_hash`, KHÔNG so `obligation_set_hash` của hàng bản khai với
-- bản kê. Hệ quả: một bản khai trỏ sang lượt phân tích KHÁC, hoặc neo vào một
-- tập nghĩa vụ KHÁC, vẫn thoả điều kiện — rồi hàng kết quả COMPOSITE mang băm
-- của lượt phân tích ĐÚNG được cấp phép. "Bản khai được cấp phép" và "bản khai
-- được kiểm" là hai thứ khác nhau.
--
-- `composite.ts` có kiểm đủ các neo này, nhưng đó là đường ghi BÌNH THƯỜNG;
-- ràng buộc database tồn tại chính vì đường bất thường.

CREATE OR REPLACE FUNCTION cursor_declaration_row_matches_manifest()
RETURNS TRIGGER AS $$
DECLARE
  m RECORD;
  d RECORD;
BEGIN
  IF NEW.result_role <> 'COMPOSITE' THEN
    RETURN NEW;
  END IF;

  SELECT * INTO m FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.llm_execution_id;
  -- Không có bản kê: `cursor_result_semantic_lineage` đã báo, đừng che.
  IF NOT FOUND OR m.execution_role <> 'DECLARATION' THEN
    RETURN NEW;
  END IF;

  SELECT * INTO d FROM cursor_declaration_result
   WHERE llm_execution_id = NEW.llm_execution_id;
  -- Không có bản khai: đã có `RESULT_WITHOUT_DECLARATION_PAYLOAD`.
  IF NOT FOUND THEN
    RETURN NEW;
  END IF;

  IF d.analysis_execution_id IS DISTINCT FROM m.analysis_execution_id THEN
    RAISE EXCEPTION
      'DECLARATION_ANALYSIS_MISMATCH: ban khai tro toi luot phan tich % nhung ban ke tro toi %',
      d.analysis_execution_id, m.analysis_execution_id;
  END IF;
  IF d.analysis_payload_hash IS DISTINCT FROM m.analysis_payload_hash THEN
    RAISE EXCEPTION
      'DECLARATION_ANALYSIS_HASH_MISMATCH: ban khai neo bam phan tich % nhung ban ke neo %',
      d.analysis_payload_hash, m.analysis_payload_hash;
  END IF;
  IF d.obligation_set_hash IS DISTINCT FROM m.obligation_set_hash THEN
    RAISE EXCEPTION
      'DECLARATION_OBLIGATION_HASH_MISMATCH: ban khai neo bam nghia vu % nhung ban ke neo %',
      d.obligation_set_hash, m.obligation_set_hash;
  END IF;

  -- Hàng kết quả cũng phải neo về CÙNG bản phân tích và CÙNG tập nghĩa vụ.
  IF NEW.analysis_payload_hash IS NOT NULL
     AND NEW.analysis_payload_hash IS DISTINCT FROM m.analysis_payload_hash THEN
    RAISE EXCEPTION
      'RESULT_ANALYSIS_HASH_MISMATCH: ket qua neo bam phan tich % nhung ban ke neo %',
      NEW.analysis_payload_hash, m.analysis_payload_hash;
  END IF;
  IF NEW.obligation_set_hash IS NOT NULL
     AND NEW.obligation_set_hash IS DISTINCT FROM m.obligation_set_hash THEN
    RAISE EXCEPTION
      'RESULT_OBLIGATION_HASH_MISMATCH: ket qua neo bam nghia vu % nhung ban ke neo %',
      NEW.obligation_set_hash, m.obligation_set_hash;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cursor_zz_declaration_row_matches_manifest_trg ON cursor_analysis_result;

CREATE TRIGGER cursor_zz_declaration_row_matches_manifest_trg
BEFORE INSERT ON cursor_analysis_result
FOR EACH ROW EXECUTE FUNCTION cursor_declaration_row_matches_manifest();
