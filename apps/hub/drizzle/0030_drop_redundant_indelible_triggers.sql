-- Gỡ bỏ 0029: nó bảo vệ một thứ ĐÃ ĐƯỢC BẢO VỆ.
--
-- 0029 thêm `cursor_result_indelible` và `analysis_validation_composite_indelible`
-- để chặn mồ côi phán quyết ĐẠT và kết quả chính thức. Cả hai thừa: từ trước đã
-- có `cursor_result_immutability` (IMMUTABLE_CURSOR_RESULT) và
-- `analysis_validation_immutability` (IMMUTABLE_VALIDATION), chặn MỌI UPDATE và
-- DELETE trên hai bảng đó — rộng hơn hẳn phần 0029 định chặn.
--
-- Sai sót khi viết 0029: chỉ tìm trigger xoá trong 0026–0028 rồi kết luận "chưa
-- có gì bảo vệ". Bảo vệ nằm ở migration cũ hơn. Bộ test mới là thứ phát hiện ra,
-- vì nó đòi thông điệp lỗi của 0029 mà nhận về thông điệp của trigger cũ.
--
-- Vì sao GỠ chứ không để đó cho chắc: hai trigger cùng canh một bảng thì trigger
-- chạy trước quyết định thông điệp lỗi, và ở đây trigger THỪA lại thắng về thứ
-- tự tên. Người đọc log sẽ thấy thông báo của một ràng buộc phụ và đi tìm sai
-- chỗ. Một ràng buộc thật, một thông điệp thật.
--
-- 0029 vẫn nằm trong nhật ký. Đó là chủ ý: một migration đã áp lên database
-- thật thì lịch sử phải cho thấy nó từng tồn tại và đã được gỡ, chứ không phải
-- bị xoá khỏi ký ức.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_result_immutability') THEN
    RAISE EXCEPTION 'PREFLIGHT_0030: khong tim thay trigger bat bien ket qua CU — khong duoc go 0029';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'analysis_validation_immutability') THEN
    RAISE EXCEPTION 'PREFLIGHT_0030: khong tim thay trigger bat bien kiem dinh CU — khong duoc go 0029';
  END IF;
END $$;
--> statement-breakpoint

DROP TRIGGER IF EXISTS cursor_result_indelible ON "cursor_analysis_result";
--> statement-breakpoint
DROP TRIGGER IF EXISTS analysis_validation_composite_indelible ON "analysis_validation";
--> statement-breakpoint
DROP FUNCTION IF EXISTS cursor_result_indelible();
--> statement-breakpoint
DROP FUNCTION IF EXISTS cursor_composite_verdict_indelible();
--> statement-breakpoint

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname IN
             ('cursor_result_indelible', 'analysis_validation_composite_indelible')) THEN
    RAISE EXCEPTION 'POSTCHECK_0030: trigger thua van con';
  END IF;
  -- Bảo vệ THẬT phải còn nguyên. Gỡ phần thừa mà làm mất phần thật thì tệ hơn
  -- nhiều so với việc cứ để cả hai.
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'cursor_result_immutability') THEN
    RAISE EXCEPTION 'POSTCHECK_0030: da lam mat trigger bat bien ket qua';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'analysis_validation_immutability') THEN
    RAISE EXCEPTION 'POSTCHECK_0030: da lam mat trigger bat bien kiem dinh';
  END IF;
END $$;
