-- BĂM MÃ NGUỒN còn thiếu cột — để so được ở mức LÔ, không chỉ ghi vào tệp.
--
-- ## ĐƯỜNG CHẠY NÀO bị ảnh hưởng (nêu TRƯỚC dòng SQL đầu tiên)
--
-- Bài học lặp ba lần của 0029→0030 và 0031→0032→0033: một thay đổi lược đồ phải
-- nói rõ nó áp cho đường chạy nào TRƯỚC khi viết SQL, vì cây mã mang cả kiến
-- trúc một lượt lẫn hai lượt.
--
-- Migration này áp cho **KHÔNG đường chạy nào** theo nghĩa hiệu lực: nó chỉ THÊM
-- năm cột `text` cho phép NULL, không ràng buộc, không trigger, không index,
-- không giá trị mặc định. Hàng cũ giữ NULL và vẫn hợp lệ y như trước; phép so ở
-- mức lô lọc `IS NOT NULL` nên hàng cũ không tạo ra báo động giả. Không đường
-- ghi nào trở nên bất hợp lệ vì migration này.
--
-- ## Vì sao cần (M-3)
--
-- `CONTRACT_PROVENANCE` mang mười băm hợp đồng, nhưng bản kê execution chỉ có
-- cột cho bốn: `validator_hash`, `schema_hash`, `prompt_source_hash`,
-- `declaration_prompt_source_hash`. Năm băm còn lại chỉ tồn tại trong `_meta`
-- của hiện vật và trong `INDEX.json` — tức chúng được GHI LẠI nhưng không được
-- ĐỐI CHIẾU.
--
-- Hệ quả cụ thể, không phải giả định: sửa `sensitive.ts` giữa kênh thứ nhất và
-- kênh thứ hai của một lô đổi `sensitive_lexicon_hash`, tức đổi ĐỊNH NGHĨA "ô
-- nào phải khai báo" giữa chừng. Bảng lần thử so băm theo cột database; không có
-- cột thì không có gì để so, và lô trộn hai định nghĩa vẫn in "sạch".
--
-- `obligation_generator_hash` và `composite_source_hash` cùng loại thiếu sót nên
-- được thêm trong cùng migration: cả hai đều là mã QUYẾT ĐỊNH kết quả.

ALTER TABLE "cursor_execution_manifest" ADD COLUMN "obligation_generator_hash" text;
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "composite_source_hash" text;
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "sensitive_lexicon_hash" text;
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "identity_source_hash" text;
ALTER TABLE "cursor_execution_manifest" ADD COLUMN "provenance_source_hash" text;
