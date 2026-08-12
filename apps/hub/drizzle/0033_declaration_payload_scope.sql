-- Thu hẹp phép kiểm "phải có bản khai" về ĐÚNG đường HAI LƯỢT.
--
-- 0032 gộp phép kiểm vào hàm lineage nhưng gắn điều kiện `NEW.result_role =
-- 'COMPOSITE'`. Sai phạm vi: kiến trúc MỘT LƯỢT cũng ghi kết quả vai COMPOSITE,
-- nhưng gắn trên execution vai ANALYSIS và KHÔNG BAO GIỜ có bản khai — theo
-- thiết kế, vì lượt khai báo chưa tồn tại ở kiến trúc đó. Phép kiểm vì thế chặn
-- nhầm 6 ca lưu trữ hợp lệ.
--
-- Điều kiện đúng là VAI EXECUTION: chỉ lượt KHAI BÁO mới bắt buộc có bản khai
-- đã lưu. Kịch bản mà rà soát đối kháng nêu (script dựng manifest DECLARATION
-- rồi xin cấp phép mà không ghi bản khai nào) vẫn bị chặn nguyên vẹn — nó đi
-- đúng vào nhánh này.
--
-- Đây là lần thứ ba trong cùng một chuỗi migration tôi phải thu hẹp một ràng
-- buộc vừa thêm. Bài học: một ràng buộc mới phải nêu rõ nó áp cho ĐƯỜNG CHẠY
-- NÀO trước khi viết, vì cây mã còn mang cả kiến trúc cũ lẫn kiến trúc mới.

DO $$
BEGIN
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_result_semantic_lineage')
     NOT LIKE '%RESULT_WITHOUT_DECLARATION_PAYLOAD%' THEN
    RAISE EXCEPTION 'PREFLIGHT_0033: chua chay 0032';
  END IF;
END $$;
--> statement-breakpoint

CREATE OR REPLACE FUNCTION cursor_result_semantic_lineage()
RETURNS TRIGGER AS $$
DECLARE
  m RECORD;
  validation_passed boolean;
  analysis_ok boolean;
  declaration_ok boolean;
  composite_ok boolean;
  ob RECORD;
BEGIN
  SELECT schema_version, execution_role, analysis_execution_id,
         analysis_payload_hash, obligation_set_hash
    INTO m
    FROM cursor_execution_manifest
   WHERE llm_execution_id = NEW.llm_execution_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'RESULT_WITHOUT_MANIFEST: execution % chua co ban ke',
      NEW.llm_execution_id;
  END IF;

  IF m.schema_version <> 'legacy' AND m.schema_version IS DISTINCT FROM NEW.schema_version THEN
    RAISE EXCEPTION
      'RESULT_SCHEMA_MISMATCH: ket qua schema % nhung ban ke execution la %',
      NEW.schema_version, m.schema_version;
  END IF;

  -- (1) Vai kết quả phải khớp vai execution.
  IF NEW.result_role = 'ANALYSIS' AND m.execution_role <> 'ANALYSIS' THEN
    RAISE EXCEPTION
      'RESULT_ROLE_MISMATCH: ket qua ANALYSIS nhung execution co vai %', m.execution_role;
  END IF;
  IF NEW.result_role = 'COMPOSITE' AND m.execution_role = 'DECLARATION'
     AND m.analysis_execution_id IS NULL THEN
    RAISE EXCEPTION 'RESULT_WITHOUT_ANALYSIS_LINK: ban ke luot khai bao thieu analysis_execution_id';
  END IF;

  -- (2) Phán quyết. Kết quả của kiến trúc MỘT LƯỢT (execution vai ANALYSIS mang
  -- kết quả COMPOSITE) vẫn chỉ cần một dòng COMPOSITE — giữ tương thích với dữ
  -- liệu và với đường chạy cũ.
  IF m.execution_role = 'DECLARATION' THEN
    SELECT passed INTO declaration_ok FROM analysis_validation
     WHERE llm_execution_id = NEW.llm_execution_id AND stage = 'DECLARATION';
    IF NOT FOUND THEN
      RAISE EXCEPTION 'RESULT_WITHOUT_DECLARATION_VALIDATION: execution % thieu phan quyet DECLARATION',
        NEW.llm_execution_id;
    END IF;
    IF declaration_ok IS NOT TRUE THEN
      RAISE EXCEPTION 'RESULT_WITH_FAILED_DECLARATION: execution % co chang DECLARATION KHONG dat',
        NEW.llm_execution_id;
    END IF;

    SELECT passed INTO analysis_ok FROM analysis_validation
     WHERE llm_execution_id = m.analysis_execution_id AND stage = 'ANALYSIS';
    IF NOT FOUND THEN
      RAISE EXCEPTION 'RESULT_WITHOUT_ANALYSIS_VALIDATION: luot phan tich % thieu phan quyet ANALYSIS',
        m.analysis_execution_id;
    END IF;
    IF analysis_ok IS NOT TRUE THEN
      RAISE EXCEPTION 'RESULT_WITH_FAILED_ANALYSIS: luot phan tich % co chang ANALYSIS KHONG dat',
        m.analysis_execution_id;
    END IF;

    -- (3) Băm neo phải khớp bản kê VÀ tập nghĩa vụ có thật.
    SELECT analysis_hash, obligation_set_hash INTO ob
      FROM cursor_claim_obligation
     WHERE analysis_execution_id = m.analysis_execution_id;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'RESULT_WITHOUT_OBLIGATION_SET: luot phan tich % chua co tap nghia vu',
        m.analysis_execution_id;
    END IF;
    IF ob.analysis_hash IS DISTINCT FROM NEW.analysis_payload_hash
    OR ob.obligation_set_hash IS DISTINCT FROM NEW.obligation_set_hash THEN
      RAISE EXCEPTION
        'RESULT_LINEAGE_DRIFT: bam neo cua ket qua khong khop tap nghia vu cua luot phan tich %',
        m.analysis_execution_id;
    END IF;
    IF m.analysis_payload_hash IS DISTINCT FROM NEW.analysis_payload_hash
    OR m.obligation_set_hash IS DISTINCT FROM NEW.obligation_set_hash THEN
      RAISE EXCEPTION
        'RESULT_MANIFEST_LINEAGE_DRIFT: bam neo cua ket qua khong khop ban ke luot khai bao';
    END IF;
  END IF;

  -- Phán quyết CỦA CHÍNH execution này, theo vai kết quả.
  IF NEW.result_role = 'ANALYSIS' THEN
    SELECT passed INTO validation_passed FROM analysis_validation
     WHERE llm_execution_id = NEW.llm_execution_id AND stage = 'ANALYSIS';
  ELSE
    SELECT passed INTO validation_passed FROM analysis_validation
     WHERE llm_execution_id = NEW.llm_execution_id AND stage = 'COMPOSITE';
  END IF;

  -- FAIL-CLOSED: thiếu dòng kiểm định cũng bị từ chối, không chỉ khi nó FALSE.
  IF NOT FOUND THEN
    RAISE EXCEPTION
      'RESULT_WITHOUT_VALIDATION: execution % chua co dong kiem dinh cho vai %',
      NEW.llm_execution_id, NEW.result_role;
  END IF;

  IF validation_passed IS NOT TRUE THEN
    RAISE EXCEPTION
      'RESULT_WITH_FAILED_VALIDATION: execution % co kiem dinh KHONG dat',
      NEW.llm_execution_id;
  END IF;

  -- CUỐI CÙNG: hiện vật hợp nhất phải có BẢN KHAI ĐÃ LƯU.
  --
  -- Đặt ở cuối, trong CÙNG hàm này, chứ không tách thành trigger riêng: trigger
  -- riêng chạy theo thứ tự tên và sẽ che mất mọi chẩn đoán cụ thể ở trên.
  IF m.execution_role = 'DECLARATION' AND NOT EXISTS (
    SELECT 1 FROM cursor_declaration_result d
    WHERE d.llm_execution_id = NEW.llm_execution_id
  ) THEN
    RAISE EXCEPTION
      'RESULT_WITHOUT_DECLARATION_PAYLOAD: execution % chua luu ban khai nao',
      NEW.llm_execution_id;
  END IF;

  RETURN NEW;
END;

$$ LANGUAGE plpgsql;
--> statement-breakpoint

DO $$
BEGIN
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_result_semantic_lineage')
     NOT LIKE '%m.execution_role = ''DECLARATION'' AND NOT EXISTS%' THEN
    RAISE EXCEPTION 'POSTCHECK_0033: pham vi phep kiem ban khai chua duoc thu hep';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_result_semantic_lineage')
     NOT LIKE '%RESULT_WITH_FAILED_ANALYSIS%' THEN
    RAISE EXCEPTION 'POSTCHECK_0033: mat chan doan cu';
  END IF;
END $$;
