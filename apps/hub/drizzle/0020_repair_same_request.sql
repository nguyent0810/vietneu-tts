-- Lần SỬA LỖI phải thuộc CÙNG MỘT YÊU CẦU với execution cha.
--
-- 0019 đã chặn trộn phiên bản schema/prompt/validator. Nhưng băm GÓI, KÊNH và
-- LẦN PHÂN TÍCH nằm ở `cursor_analysis_request`, không nằm ở bản kê — nên một
-- lần sửa lỗi vẫn có thể trỏ sang một request khác trong cùng lần chạy và đổi
-- gói bằng chứng dưới chân chính nó.
--
-- Ràng buộc "cùng request" bao trọn cả ba: request đã bị khoá vào (workspace,
-- run, channel) và mang package_hash + prompt_hash của riêng nó. Đây là bất
-- biến mạnh nhất mà cũng đơn giản nhất: một chuỗi retry là các lần thử LẠI CÙNG
-- MỘT việc, không phải một việc khác.

CREATE OR REPLACE FUNCTION cursor_repair_version_immutable()
RETURNS TRIGGER AS $$
DECLARE
  parent RECORD;
BEGIN
  IF NEW.parent_execution_id IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT schema_version, prompt_version, validator_hash, schema_hash,
         prompt_source_hash, request_id, analysis_run_id
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
  OR parent.prompt_source_hash IS DISTINCT FROM NEW.prompt_source_hash THEN
    RAISE EXCEPTION
      'MIXED_VERSION_REPAIR_CHAIN: lan sua loi dung phien ban khac execution cha %',
      NEW.parent_execution_id;
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
