-- Bất biến cho kết quả phân tích.
--
-- Đề bài: "kết quả phải append-only hoặc có revision; KHÔNG ghi đè output cũ".
-- Tính lại thì tạo `analysis_run` mới (run_sequence tăng); kết quả cũ giữ
-- nguyên, nên một phân tích chạy tháng trước vẫn tái lập được nguyên vẹn.
--
-- `feature_version` cũng bất biến: nếu sửa được công thức tại chỗ thì mọi giá
-- trị lịch sử trỏ vào nó sẽ âm thầm đổi ý nghĩa — đúng thứ versioning sinh ra
-- để ngăn.

CREATE OR REPLACE FUNCTION enforce_feature_version_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_FEATURE_VERSION: dinh nghia cong thuc % la bat bien; tang version thay vi sua', OLD.id;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER feature_version_immutability
  BEFORE UPDATE OR DELETE ON feature_version
  FOR EACH ROW EXECUTE FUNCTION enforce_feature_version_immutability();
--> statement-breakpoint

CREATE OR REPLACE FUNCTION enforce_feature_value_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_FEATURE_VALUE: gia tri feature % la bat bien; tao analysis_run moi', OLD.id;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER feature_value_immutability
  BEFORE UPDATE OR DELETE ON feature_value
  FOR EACH ROW EXECUTE FUNCTION enforce_feature_value_immutability();
--> statement-breakpoint

CREATE OR REPLACE FUNCTION enforce_observation_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_OBSERVATION: quan sat % la bat bien (thao tac: %)', OLD.id, TG_OP;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER observation_immutability
  BEFORE UPDATE OR DELETE ON deterministic_observation
  FOR EACH ROW EXECUTE FUNCTION enforce_observation_immutability();
--> statement-breakpoint

CREATE OR REPLACE FUNCTION enforce_analysis_package_immutability()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'IMMUTABLE_ANALYSIS_PACKAGE: goi % la bat bien; tao run moi', OLD.id;
END;
$$ LANGUAGE plpgsql;
--> statement-breakpoint

CREATE TRIGGER analysis_package_immutability
  BEFORE UPDATE OR DELETE ON analysis_package
  FOR EACH ROW EXECUTE FUNCTION enforce_analysis_package_immutability();
