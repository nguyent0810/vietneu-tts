-- Phán quyết ĐẠT và kết quả chính thức KHÔNG THỂ BỊ MỒ CÔI.
--
-- 0028 lo phần "không được có hai cái". Còn thiếu phần đối xứng: không được
-- MẤT cái đang có. Hôm nay xoá được ba thứ mà không ai cản:
--
--   * dòng phán quyết COMPOSITE ĐẠT — kết quả chính thức vẫn nằm đó, nhưng cái
--     cấp phép cho nó thì biến mất. Nhìn vào database sẽ thấy một hiện vật
--     "chính thức" mà không tra ra được ai cho phép nó thành chính thức.
--   * hàng kết quả chính thức — phán quyết ĐẠT vẫn còn, nên trigger 0028 vẫn
--     coi lượt phân tích này "đã có quyền", trong khi hiện vật đã mất. Ghi lại
--     là không được, mà đọc cũng chẳng có gì.
--   * SỬA một trong hai — tệ hơn xoá, vì không để lại khoảng trống nào để thấy.
--
-- Cả ba đều là mất bằng chứng IM LẶNG. Toàn bộ lập luận của Phase 4 dựa trên
-- việc mọi lần thử đều truy được; một hàng biến mất không tiếng động thì lô đo
-- còn lại không tự chứng minh được nữa.
--
-- Chỉ chặn ĐÚNG dòng mang quyền. Phán quyết KHÔNG ĐẠT vẫn xoá được: chúng là
-- bằng chứng thao tác, không phải bằng chứng cấp phép, và giữ cứng chúng sẽ
-- khiến dọn dữ liệu test thành bất khả thi mà chẳng bảo vệ được gì.
--
-- HẠN CHẾ, nói thẳng: đây là ràng buộc trong database, KHÔNG phải attestation.
-- Ai có quyền superuser vẫn `ALTER TABLE ... DISABLE TRIGGER` được. Nó chặn
-- được sự cố và chặn được mã sai; nó không chặn được người cố tình.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cursor_single_authoritative_result') THEN
    RAISE EXCEPTION 'PREFLIGHT_0029: chua chay 0028 — thu tu migration sai';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_result_indelible') THEN
    RAISE EXCEPTION 'PREFLIGHT_0029: trigger DA ton tai — migration nay da chay?';
  END IF;
END $$;
--> statement-breakpoint

-- Kết quả chính thức: BẤT BIẾN và KHÔNG XOÁ ĐƯỢC.
CREATE OR REPLACE FUNCTION cursor_result_indelible()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION
      'AUTHORITATIVE_RESULT_INDELIBLE: khong duoc xoa ket qua chinh thuc % (luot phan tich %)',
      OLD.id, OLD.analysis_run_id;
  END IF;
  RAISE EXCEPTION
    'AUTHORITATIVE_RESULT_IMMUTABLE: khong duoc sua ket qua chinh thuc %', OLD.id;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_result_indelible ON "cursor_analysis_result";
--> statement-breakpoint

CREATE TRIGGER cursor_result_indelible
  BEFORE UPDATE OR DELETE ON "cursor_analysis_result"
  FOR EACH ROW EXECUTE FUNCTION cursor_result_indelible();
--> statement-breakpoint

-- Phán quyết COMPOSITE ĐẠT: giữ chừng nào kết quả nó cấp phép còn sống.
--
-- Điều kiện gắn với SỰ TỒN TẠI của kết quả, không phải cấm tuyệt đối: nếu chưa
-- có hiện vật nào được cấp phép thì dòng này chưa cấp quyền cho ai, và giữ cứng
-- nó chỉ làm khó việc dọn dẹp.
CREATE OR REPLACE FUNCTION cursor_composite_verdict_indelible()
RETURNS TRIGGER AS $$
DECLARE
  bound uuid;
BEGIN
  IF OLD.stage <> 'COMPOSITE' OR OLD.passed IS NOT TRUE THEN
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
  END IF;

  SELECT r.id INTO bound
  FROM cursor_analysis_result r
  WHERE r.llm_execution_id = OLD.llm_execution_id
    AND r.result_role = 'COMPOSITE'
  LIMIT 1;

  IF bound IS NOT NULL THEN
    RAISE EXCEPTION
      'COMPOSITE_VERDICT_INDELIBLE: phan quyet DAT % dang cap phep cho ket qua %',
      OLD.id, bound;
  END IF;

  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

DROP TRIGGER IF EXISTS analysis_validation_composite_indelible ON "analysis_validation";
--> statement-breakpoint

CREATE TRIGGER analysis_validation_composite_indelible
  BEFORE UPDATE OR DELETE ON "analysis_validation"
  FOR EACH ROW EXECUTE FUNCTION cursor_composite_verdict_indelible();
--> statement-breakpoint

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_result_indelible') THEN
    RAISE EXCEPTION 'POSTCHECK_0029: thieu trigger bat bien ket qua';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'analysis_validation_composite_indelible') THEN
    RAISE EXCEPTION 'POSTCHECK_0029: thieu trigger bat bien phan quyet DAT';
  END IF;
  IF (SELECT prosrc FROM pg_proc WHERE proname = 'cursor_composite_verdict_indelible')
     NOT LIKE '%OLD.passed IS NOT TRUE%' THEN
    RAISE EXCEPTION 'POSTCHECK_0029: trigger phan quyet khong phan biet DAT/KHONG DAT';
  END IF;
END $$;
