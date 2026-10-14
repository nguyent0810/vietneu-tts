-- Kết quả Cursor bất biến sau khi ghi.
--
-- Đề bài: "kết quả đã chốt phải bất biến; chạy lại tạo lần chạy mới và bản
-- revision mới". Sửa được kết quả nghĩa là phần đo độ ổn định vô nghĩa — không
-- ai còn phân biệt được "hai lần chạy cho kết quả giống nhau" với "một kết quả
-- đã bị sửa cho giống".

CREATE OR REPLACE FUNCTION enforce_cursor_result_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_CURSOR_RESULT: ket qua % la bat bien (thao tac: %)', OLD.id, TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER cursor_result_immutability
  BEFORE UPDATE OR DELETE ON cursor_analysis_result
  FOR EACH ROW EXECUTE FUNCTION enforce_cursor_result_immutability();
--> statement-breakpoint

-- Báo cáo kiểm định cũng bất biến: nó là bằng chứng về chất lượng của một lần
-- chạy, sửa được thì không còn là bằng chứng.
CREATE OR REPLACE FUNCTION enforce_validation_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_VALIDATION: bao cao kiem dinh % la bat bien (thao tac: %)', OLD.id, TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER analysis_validation_immutability
  BEFORE UPDATE OR DELETE ON analysis_validation
  FOR EACH ROW EXECUTE FUNCTION enforce_validation_immutability();
