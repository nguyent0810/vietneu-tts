"""Lõi judge-panel dùng chung cho MỌI generator Short "sự thật tính toán
được" (lịch hoàng đạo, 12 vị Thần, con giáp hợp/kỵ, màu mệnh Ngũ Hành...).

Tách ra từ lich_hoang_dao_generator.py (bản gốc đã kiểm chứng thật: sửa từ
thiết kế sequential-revise không hội tụ sang judge-panel 3 phương án +
fact-check cứng, PASS ngay vòng 1 trên pilot thật) -- các generator MỚI chỉ
cần cung cấp `facts` (dict bất kỳ, nguồn sự thật của riêng nó) + 2 prompt
template (generate/judge), KHÔNG copy lại phần engine.

Nguyên tắc bắt buộc giữ nguyên cho MỌI generator dùng module này: facts
PHẢI do generator tự tính toán/tra cứu từ nguồn đáng tin (không phải agy tự
nhớ/suy luận), Codex chỉ được fact-check đối chiếu ĐÚNG facts đã đưa, không
được tự thêm/bịa số liệu ngoài."""
import json
import os
import re
import sys

from content_seo import ContentSeoError, _extract_json, _run_agy, _run_codex

MAX_ITERATIONS = 3
HOOK_PASS_THRESHOLD = 8

_VALID_STRATEGIES = frozenset({"A", "B", "C"})
_PILOT_STRATEGIES_ABCD = frozenset({"A", "B", "C", "D"})  # dùng riêng cho 1 generator thí điểm strategy D -- KHÔNG đụng _VALID_STRATEGIES, 9 generator còn lại không bị ảnh hưởng.

# Quy tắc retention (giữ chân người xem) DÙNG CHUNG cho MỌI generator --
# thêm sau khi rà soát THẬT 8 short đã đăng (xem phiên làm việc): đo dữ
# liệu audio thật (duration/wpm/độ dài câu hook tính bằng giây) và đối
# chiếu benchmark ngành thật (hook phải vào điểm nhấn trong ~3 giây đầu,
# 170-200 wpm là tốc độ phù hợp cho Short-form, câu cuối nên tạo cảm giác
# muốn xem lại) -- phát hiện 6/8 video mở đầu bằng mệnh đề phụ dài (kiểu
# "Trong khi X thì Y...", "Nếu... thì... thì sao?") khiến điểm nhấn đến
# chậm (4-8 giây thay vì ~3 giây), và 5/8 video kết thúc bằng 1 chi tiết
# phụ rời rạc không quay lại chủ đề hook, không tạo cảm giác đáng nhớ.
# Judge-panel TRƯỚC ĐÓ chỉ chấm fact-check + "hook có hấp dẫn không" một
# cách định tính, KHÔNG có tiêu chí cụ thể cho nhịp độ/cấu trúc câu mở-kết
# -- bổ sung 2 quy tắc CỤ THỂ, ĐO ĐƯỢC dưới đây, tiêm vào MỌI prompt
# generate/judge qua _inject_block() (xem bên dưới) để không phải sửa tay
# từng file trong 10 generator hiện có (và tự động áp dụng cho generator
# mới sau này, không cần nhớ thêm thủ công).
_RETENTION_RULES_BLOCK = """
QUY TẮC NHỊP ĐỘ/GIỮ CHÂN NGƯỜI XEM (retention, ÁP DỤNG THÊM CHO TẤT CẢ CÁC PHƯƠNG ÁN, ngoài mọi quy tắc riêng ở trên):
- Câu đầu tiên (hook) PHẢI vào thẳng chủ thể/điểm nhấn chính NGAY LẬP TỨC -- KHÔNG mở đầu bằng mệnh đề phụ dài kiểu "Trong khi X thì Y...", "Nếu... thì... thì sao?" (2 lớp giả định chồng nhau) khiến điểm nhấn đến chậm. Câu đầu nên tối đa ~12 từ (đọc xong trong khoảng 3 giây, đúng nhịp Short-form).
- Câu cuối PHẢI quay lại/echo ý của câu hook đầu tiên, HOẶC chốt bằng 1 câu ngắn gọn, đáng nhớ, có thể trích dẫn lại -- KHÔNG được là 1 chi tiết phụ rời rạc, thông tin thêm không liên quan trực tiếp tới hook.
- BẤT KỲ câu nào ở phần giữa (không phải câu đầu, không phải câu cuối) PHẢI tạo TIẾN TRIỂN thật -- bổ sung thông tin/góc nhìn/hệ quả MỚI gắn với lời hứa của câu hook, KHÔNG chỉ nhắc lại/diễn giải lại/trang trí điều đã nói. CHỈ CẦN 1 câu giữa không mang giá trị mới (dù các câu giữa khác có mới hay không) là đã vi phạm -- 1 câu mới ở cuối KHÔNG "bù" được cho 1 câu giữa bị lãng phí trước đó. TRƯỜNG HỢP MINH HOẠ CỤ THỂ (không phải toàn bộ định nghĩa): nếu câu hook đặt 1 lời hứa cụ thể (VD tên/danh sách được hỏi trực tiếp) và câu thứ hai giải đáp NGAY TRỌN VẸN lời hứa đó -- ĐIỀU NÀY KHÔNG TỰ ĐỘNG SAI -- nhưng khi đó MỌI câu GIỮA còn lại (không tính câu cuối/closer -- câu cuối do rule (b) riêng chi phối) đều phải tự mình mở ra giá trị MỚI (vì sao, thứ tự ưu tiên, ngoại lệ, hệ quả, đối lập, ứng dụng thực tế...), KHÔNG được chỉ nhắc lại tên/danh sách đã nêu dưới dạng khác (kể cả đổi tên thường sang Can Chi hay ngược lại, nếu không kèm thông tin/quan hệ mới). Mục tiêu là nhịp độ tự nhiên của 1 câu chuyện/lý giải mạch lạc, KHÔNG phải một mánh câu view giả tạo hay việc giấu thông tin không cần thiết.
- (THAM KHẢO, không cưỡng chế) Nếu câu hook là câu hỏi có lời hứa xác định được (vì sao/khi nào/làm sao/là gì/nếu-thì-sao/ai/ở đâu/bao nhiêu/có-hay-không), cố gắng để thân bài trả lời ĐÚNG LOẠI câu hỏi đó (khi nào -> dấu hiệu/tiêu chí cụ thể; làm sao -> hành động/quy trình; vì sao -> chuỗi nguyên nhân; là gì -> đặc điểm phân biệt) -- không chỉ nội dung liên quan chủ đề chung chung.
- (THAM KHẢO, không cưỡng chế) Mỗi câu nên dễ hiểu ngay lần nghe đầu tiên (người nghe audio KHÔNG tua lại) -- tránh dồn đồng thời nhiều tên riêng/thuật ngữ ít phổ biến + khái niệm trừu tượng mới + mốc thời gian/số liệu + chữ viết tắt vào cùng 1 câu; tách thành 2 câu nếu cần.
"""

_RETENTION_CHECK_BLOCK = """
BƯỚC RETENTION (áp dụng SAU fact-check, TRƯỚC khi chấm hook_score cuối): với MỖI phương án còn lại sau fact-check, kiểm tra thêm: (a) câu đầu có mở bằng mệnh đề phụ dài trước khi vào điểm nhấn không (ước lượng: quá ~12 từ trước khi chạm chủ thể/ý chính) -- nếu có, KHÔNG được cho hook_score >= 8 dù fact-check PASS; (b) câu cuối có quay lại chủ đề hook hoặc chốt bằng câu đáng nhớ không, hay chỉ là chi tiết phụ rời rạc -- nếu chỉ là chi tiết phụ, cũng KHÔNG được cho hook_score >= 8. Đây là tiêu chí GIẢM ĐIỂM (không phải fact-check, không LOẠI phương án), chỉ giới hạn trần hook_score.
(c) XÉT TỪNG câu ở phần giữa RIÊNG LẺ: câu đó có tạo tiến triển thật (thông tin/góc nhìn/hệ quả MỚI gắn với lời hứa của hook) hay chỉ nhắc lại/diễn giải lại/trang trí nội dung ĐÃ XUẤT HIỆN Ở BẤT KỲ CÂU NÀO TRƯỚC ĐÓ (không chỉ so với câu liền trước -- 1 câu lặp lại đúng nội dung câu 2 vẫn tính là vi phạm dù không lặp câu 3) không? CHỈ CẦN 1 câu giữa (bất kỳ vị trí nào, không riêng câu 2) không mang giá trị mới là đã vi phạm (c) -- 1 câu giữa khác có giá trị mới, hoặc câu cuối có chi tiết mới, KHÔNG bù được cho câu giữa bị lãng phí đó. TRƯỜNG HỢP MINH HOẠ: nếu câu hook đặt 1 lời hứa cụ thể và câu thứ hai giải đáp NGAY TRỌN VẸN lời hứa đó, MỌI câu GIỮA còn lại (không tính câu cuối/closer) đều phải tự mình mang giá trị mới (không chỉ 1 trong số đó) -- nếu BẤT KỲ câu nào trong số đó chỉ nhắc lại/liệt kê lại cùng thông tin đã cho ở câu 2 dưới dạng khác (kể cả đổi tên thường sang Can Chi hay ngược lại mà không kèm quan hệ/lý do mới), KHÔNG được cho hook_score >= 8, CÙNG mức giảm điểm như (a)/(b), độc lập với (a) và (b).
Khi áp dụng trần điểm ở (a)/(b)/(c), hãy nêu rõ trong "feedback" tiêu chí nào đã khiến hook_score bị ép trần -- phục vụ audit thủ công định kỳ (đọc lại feedback qua nhiều lần chạy để ước lượng tần suất rule (c) bị vi phạm), KHÔNG yêu cầu field JSON mới, KHÔNG được code tự động parse/validate nội dung này.
(d) [GHI CHÚ, KHÔNG ép điểm] Nếu câu hook là câu hỏi có lời hứa xác định được (vì sao/khi nào/làm sao/là gì/nếu-thì-sao/ai/ở đâu/bao nhiêu/có-hay-không) -- ghi vào "feedback" xem thân bài có trả lời ĐÚNG LOẠI câu hỏi đó không (khi nào -> dấu hiệu cụ thể; làm sao -> hành động/quy trình; vì sao -> chuỗi nguyên nhân; là gì -> đặc điểm phân biệt). Nếu hook KHÔNG phải câu hỏi có lời hứa xác định (câu hỏi tu từ, câu khẳng định), bỏ qua (d). ĐÂY LÀ GHI CHÚ THAM KHẢO CHO AUDIT SAU NÀY -- KHÔNG dùng (d) để ép trần hook_score (khác hẳn (a)/(b)/(c) đã có cơ chế ép trần), vì chưa đủ tin cậy để dùng như tiêu chí loại/giảm điểm.
(e) [GHI CHÚ, KHÔNG ép điểm] Với mỗi câu, tự hỏi: người nghe (không đọc lại được) có hiểu trọn vẹn ngay lần nghe đầu, ở tốc độ đọc bình thường không? Nếu 1 câu dồn nhiều thành phần mới cùng lúc (tên riêng lạ + khái niệm trừu tượng mới + số liệu/mốc thời gian + chữ viết tắt) khiến khó hiểu ngay, ghi chú vào "feedback". ĐÂY CŨNG LÀ GHI CHÚ THAM KHẢO -- KHÔNG ép trần hook_score, chưa đủ bằng chứng để dùng như tiêu chí chấm điểm chính thức.
"""

_RETURN_JSON_MARKER = "Trả về CHỈ 1 JSON object"
# Ngưỡng RỘNG RÃI (xem _validate_verdict()) -- chỉ bắt câu hook thật sự
# cồng kềnh (mệnh đề phụ dài trước điểm nhấn), không chặn nhầm câu hơi dài
# nhưng vẫn ổn. Không dùng số ~12 từ "lý tưởng" trong _RETENTION_RULES_BLOCK
# làm ngưỡng CƯỠNG CHẾ -- ngưỡng lý tưởng nên mềm (hướng dẫn qua prompt),
# ngưỡng cưỡng chế trong code nên rộng hơn hẳn để tránh false positive.
HOOK_MAX_FIRST_SENTENCE_WORDS = 20


def _first_sentence_word_count(script: str) -> int:
    clean = re.sub(r"\*\*", "", script)
    match = re.search(r"[.?!]", clean)
    first_sentence = clean[:match.start()] if match else clean
    return len(first_sentence.split())


def _inject_retention_block(template: str, block: str) -> str:
    """Chèn `block` (quy tắc retention dùng chung) NGAY TRƯỚC dòng "Trả về
    CHỈ 1 JSON object" -- điểm neo giống hệt ở MỌI generator hiện có (đã
    kiểm tra thật: xuất hiện đúng 1 lần trong mỗi _GENERATE_CANDIDATES_
    PROMPT/_JUDGE_PROMPT, kể cả 2 file có thêm 1 prompt trích chủ đề riêng
    với cùng cụm này -- không ảnh hưởng vì mỗi lần gọi chỉ nhận ĐÚNG 1
    template, không phải cả file). Chèn TRƯỚC hướng dẫn "giờ hãy trả lời"
    thay vì nối cuối chuỗi -- nối cuối sẽ rơi SAU chỉ dẫn định dạng, dễ bị
    mô hình bỏ qua/coi là ghi chú thừa. Nếu không tìm thấy điểm neo (template
    tương lai đổi cấu trúc), fallback nối cuối thay vì lỗi cứng."""
    idx = template.find(_RETURN_JSON_MARKER)
    if idx == -1:
        return template + "\n" + block
    return template[:idx] + block + "\n" + template[idx:]


# BUG THẬT phát hiện qua Codex CLI review độc lập (xem phiên làm việc):
# generate_candidates()/judge_candidates() trước đây tin thẳng cấu trúc
# JSON agy/Codex trả về (result["candidates"], c['strategy'], c['script'],
# verdict.get("hook_score")...) -- JSON hợp lệ nhưng THIẾU/SAI KIỂU field
# (vd hook_score trả về chuỗi "8" thay vì số, candidates rỗng, thiếu key
# "script") sẽ raise KeyError/TypeError THẲNG, không phải ContentSeoError,
# nên "except ContentSeoError" ở generate_verified_script() KHÔNG bắt được
# -- crash cả tiến trình thay vì retry vòng sau như thiết kế. Validate rõ
# ràng, raise ContentSeoError cho MỌI sai lệch cấu trúc để cơ chế retry đã
# có thực sự phát huy tác dụng khi chạy không giám sát (cron/launchd).
def _validate_candidates(result, valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> list[dict]:
    if not isinstance(result, dict) or not isinstance(result.get("candidates"), list) or not result["candidates"]:
        raise ContentSeoError(f"agy trả về cấu trúc candidates không hợp lệ (thiếu/rỗng 'candidates'): {result!r}"[:500])
    candidates = result["candidates"]
    for c in candidates:
        if not isinstance(c, dict) or not isinstance(c.get("strategy"), str) or not isinstance(c.get("script"), str) or not c.get("script", "").strip():
            raise ContentSeoError(f"1 candidate thiếu/sai kiểu 'strategy' hoặc 'script': {c!r}"[:500])
    # BUG THẬT phát hiện qua Codex CLI review LẦN 2 (đối chiếu lại code sau
    # khi sửa lần 1 -- Codex tự chạy thử adversarial case, không chỉ đọc
    # code): validate ban đầu KHÔNG kiểm tra strategy có đúng đủ 3 giá trị
    # A/B/C duy nhất hay không (chấp nhận cả strategy="X", trùng lặp,
    # thiếu). Hệ quả dây chuyền: _validate_verdict() tìm strategy_beat theo
    # winner có thể ra None (không candidate nào khớp), và trước khi sửa
    # đây SILENT SKIP toàn bộ bước so khớp Jaccard thay vì FAIL -- verdict
    # chọn 1 "winner" không hề tồn tại trong candidates thật vẫn được chấp
    # nhận. Chặn ngay từ gốc: BẮT BUỘC đúng đủ bộ strategy hợp lệ (mặc định A/B/C, có thể mở rộng qua valid_strategies), không
    # thiếu/thừa/trùng.
    strategies = [c["strategy"] for c in candidates]
    if set(strategies) != valid_strategies or len(strategies) != len(valid_strategies):
        raise ContentSeoError(f"agy trả về strategy không đúng bộ {sorted(valid_strategies)} duy nhất (nhận: {strategies}): {result!r}"[:500])
    return candidates


def _validate_verdict(verdict, candidates: list[dict], valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> dict:
    if not isinstance(verdict, dict):
        raise ContentSeoError(f"Codex trả về verdict không phải object: {verdict!r}"[:500])
    winner = verdict.get("winner")
    if winner not in valid_strategies and winner != "NONE":
        raise ContentSeoError(f"Codex trả về 'winner' không hợp lệ (phải là {'/'.join(sorted(valid_strategies))}/NONE): {winner!r}")
    if winner in valid_strategies:
        winner_script = verdict.get("winner_script")
        if not isinstance(winner_script, str) or not winner_script.strip():
            raise ContentSeoError(f"winner={winner} nhưng 'winner_script' rỗng/thiếu -- verdict không đáng tin: {verdict!r}"[:500])
        # winner_script PHẢI xuất phát từ đúng 1 trong các candidate đã đưa
        # (Codex có thể giữ nguyên dấu ** hoặc chỉnh nhẹ khoảng trắng khi
        # trả lại) -- chặn trường hợp Codex tự bịa 1 script hoàn toàn khác
        # rồi tự nhận "winner". So khớp theo TỪ (Jaccard trên tập từ), KHÔNG
        # theo bảng chữ cái xuất hiện -- đã test thật: so theo ký tự đơn lẻ
        # gần như luôn "giống" vì mọi câu tiếng Việt đều dùng chung 1 bảng
        # chữ cái, không phát hiện được nội dung bịa hoàn toàn khác.
        # BUG THẬT phát hiện qua Codex CLI review LẦN 2: trước đây nếu
        # strategy_beat is None (winner không khớp candidate nào -- có thể
        # xảy ra khi validate candidates lỏng lẻo, xem _validate_candidates)
        # thì SILENT SKIP toàn bộ bước so khớp Jaccard thay vì FAIL. Giờ
        # candidates đã ép đúng đủ bộ valid_strategies nên None không còn xảy ra trong
        # luồng bình thường, nhưng vẫn giữ hard-fail thay vì skip -- phòng
        # thủ theo chiều sâu, đúng tinh thần "verdict tham chiếu 1 candidate
        # không tồn tại là dấu hiệu KHÔNG đáng tin", không phải trường hợp
        # bỏ qua được.
        strategy_beat = next((c for c in candidates if c.get("strategy") == winner), None)
        if strategy_beat is None:
            raise ContentSeoError(f"verdict chọn winner={winner} nhưng KHÔNG có candidate nào mang strategy đó -- verdict không đáng tin: {verdict!r}"[:500])
        word_set = lambda s: set(re.findall(r"\w+", s.lower(), re.UNICODE))  # noqa: E731
        original_words, winner_words = word_set(strategy_beat["script"]), word_set(winner_script)
        union = original_words | winner_words
        jaccard = len(original_words & winner_words) / len(union) if union else 0.0
        if jaccard < 0.4:
            raise ContentSeoError(
                f"winner_script khác quá xa candidate {winner} gốc đã đưa cho Codex chấm "
                f"(trùng {jaccard:.0%} số từ) -- nghi ngờ Codex tự bịa thay vì chấm đúng bản đã có."
            )
        try:
            score = float(verdict.get("hook_score", 0))
        except (TypeError, ValueError):
            raise ContentSeoError(f"'hook_score' không phải số: {verdict.get('hook_score')!r}") from None
        # BUG THẬT phát hiện qua Codex CLI review LẦN 2: hook_score chỉ được
        # kiểm tra "coerce được về số", KHÔNG kiểm tra nằm trong khoảng hợp
        # lệ -- Codex tự test hook_score="999" vẫn lọt qua (một dấu hiệu rõ
        # ràng verdict không đáng tin, thang điểm thiết kế 1-10).
        if not (0 <= score <= 10):
            raise ContentSeoError(f"'hook_score'={score} nằm ngoài khoảng hợp lệ 0-10 -- verdict không đáng tin: {verdict!r}"[:500])
        # BUG THẬT phát hiện qua Codex CLI review LẦN 2 (đợt kiểm tra thứ 2,
        # sau khi đã sửa xong bản đầu -- Codex tự adversarial-test tiếp và
        # phát hiện bản sửa đầu CHỈ chặn fact_check.<winner> bắt đầu bằng
        # "FAIL", nhưng KHÔNG bắt buộc phải CÓ fact_check hợp lệ -- verdict
        # thiếu hẳn 'fact_check', fact_check thiếu key winner, hoặc giá trị
        # sai kiểu (vd False thay vì chuỗi) đều lọt qua vì check cũ chỉ phủ
        # định "FAIL", không đòi hỏi tích cực phải là "PASS". Đổi sang yêu
        # cầu DƯƠNG TÍNH: fact_check PHẢI là dict, fact_check[winner] PHẢI
        # là chuỗi bắt đầu bằng "PASS" rõ ràng -- đối chiếu chéo để bắt các
        # verdict không nhất quán nội bộ, không chỉ tin field "winner" đơn lẻ.
        fact_check = verdict.get("fact_check")
        if not isinstance(fact_check, dict):
            raise ContentSeoError(f"verdict thiếu/sai kiểu 'fact_check' (phải là object) -- verdict không đáng tin: {verdict!r}"[:500])
        winner_fact_check = fact_check.get(winner)
        if not isinstance(winner_fact_check, str) or not winner_fact_check.strip().upper().startswith("PASS"):
            raise ContentSeoError(f"verdict chọn winner={winner} nhưng fact_check.{winner} không phải 'PASS' rõ ràng (nhận: {winner_fact_check!r}) -- verdict không đáng tin: {verdict!r}"[:500])
        # BUG THẬT phát hiện qua Codex CLI review (đợt retention, xem phiên
        # làm việc): quy tắc "hook mở đầu bằng mệnh đề phụ dài thì KHÔNG
        # được cho hook_score >= 8" (_RETENTION_CHECK_BLOCK) TRƯỚC ĐÂY chỉ
        # là hướng dẫn trong prompt, KHÔNG có cơ chế cưỡng chế trong code --
        # Codex tự adversarial-test: verdict claim hook_score=10 cho 1
        # winner_script có câu đầu rất dài vẫn được _validate_verdict()
        # chấp nhận nguyên vẹn -- CÙNG LỚP lỗ hổng với fact_check/hook_score
        # range đã sửa trước đó (prompt policy không tự validate được). Đếm
        # số từ câu ĐẦU TIÊN của winner_script làm proxy khách quan, vượt
        # ngưỡng RỘNG RÃI thì ÉP TRẦN hook_score xuống 7, bất kể Codex tự
        # chấm bao nhiêu -- không raise lỗi (retention không nghiêm trọng
        # như bịa sự thật), chỉ đảm bảo điểm không tự động đạt ngưỡng PASS.
        first_sentence_words = _first_sentence_word_count(winner_script)
        if first_sentence_words > HOOK_MAX_FIRST_SENTENCE_WORDS and score >= 8:
            print(f"CẢNH BÁO: câu hook đầu tiên dài {first_sentence_words} từ (>{HOOK_MAX_FIRST_SENTENCE_WORDS}) nhưng verdict cho hook_score={score} -- ép trần xuống 7 (retention).", file=sys.stderr)
            score = 7.0
            verdict["hook_score"] = score
    return verdict


def generate_candidates(facts: dict, generate_prompt_template: str, prior_feedback: str | None = None,
                         valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> list[dict]:
    revision_note = (
        f"\n=== PHẢN HỒI VÒNG TRƯỚC -- TRÁNH LẶP LẠI ĐIỂM YẾU NÀY ===\n{prior_feedback}\n"
        if prior_feedback else ""
    )
    template = _inject_retention_block(generate_prompt_template, _RETENTION_RULES_BLOCK)
    prompt = template.format(facts_json=json.dumps(facts, ensure_ascii=False, indent=2), revision_note=revision_note)
    result = _extract_json(_run_agy(prompt))
    return _validate_candidates(result, valid_strategies=valid_strategies)


def judge_candidates(facts: dict, candidates: list[dict], judge_prompt_template: str,
                      valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> dict:
    candidates_text = "\n\n".join(f"--- Phương án {c['strategy']} ---\n{c['script']}" for c in candidates)
    template = _inject_retention_block(judge_prompt_template, _RETENTION_CHECK_BLOCK)
    prompt = template.format(facts_json=json.dumps(facts, ensure_ascii=False, indent=2), candidates_text=candidates_text)
    verdict = _extract_json(_run_codex(prompt))
    return _validate_verdict(verdict, candidates, valid_strategies=valid_strategies)


def generate_verified_script(
    facts: dict, generate_prompt_template: str, judge_prompt_template: str,
    max_rounds: int = MAX_ITERATIONS, hook_pass_threshold: int = HOOK_PASS_THRESHOLD,
    valid_strategies: frozenset[str] = _VALID_STRATEGIES,
) -> dict:
    # LỐI TẮT THEO YÊU CẦU RÕ RÀNG CỦA NGƯỜI DÙNG (2026-09-04): codex hết
    # timeout liên tục + cursor-agent (fallback) hết quota, chặn toàn bộ
    # judge_candidates()/_run_codex() bên dưới. Người dùng đã được cảnh báo
    # rõ (KHÔNG áp dụng cho kênh Hình Sự -- xem criminal_law_short_generator.py/
    # cl_case_batch.py, KHÔNG đọc biến này) và xác nhận chấp nhận rủi ro CHỈ
    # cho FS/BUD (không liên quan người thật/pháp lý): bỏ hẳn bước judge/
    # fact-check qua Codex, dùng THẲNG phương án A (đầu tiên) từ agy, không
    # qua bất kỳ vòng chấm điểm/đối chiếu nào. KHÔNG dùng biến này làm mặc
    # định lâu dài -- chỉ bật thủ công khi cursor/codex thật sự nghẽn.
    if os.environ.get("VIETNEU_SKIP_JUDGE_PANEL") == "1":
        candidates = generate_candidates(facts, generate_prompt_template, valid_strategies=valid_strategies)
        script = candidates[0]["script"]
        print("CẢNH BÁO: VIETNEU_SKIP_JUDGE_PANEL=1 -- bỏ qua judge/fact-check Codex, dùng thẳng phương án A từ agy, KHÔNG qua kiểm chứng.", file=sys.stderr)
        return {"script": script, "passed": True, "hook_score": None, "iterations_used": 1,
                "history": [{"round": 1, "candidates": candidates, "skipped_judge": True}], "needs_human_review": False}

    history = []
    best_script, best_score, best_feedback = None, None, None

    for round_i in range(1, max_rounds + 1):
        try:
            candidates = generate_candidates(facts, generate_prompt_template, prior_feedback=best_feedback,
                                              valid_strategies=valid_strategies)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: agy soạn lỗi vòng {round_i} ({exc}).", file=sys.stderr)
            history.append({"round": round_i, "stage": "generate", "error": str(exc)})
            continue

        try:
            verdict = judge_candidates(facts, candidates, judge_prompt_template, valid_strategies=valid_strategies)
        except ContentSeoError as exc:
            print(f"CẢNH BÁO: chấm điểm lỗi vòng {round_i} ({exc}).", file=sys.stderr)
            history.append({"round": round_i, "stage": "judge", "error": str(exc)})
            continue

        history.append({"round": round_i, "candidates": candidates, "verdict": verdict})
        winner = verdict.get("winner")
        print(f"Vòng {round_i}/{max_rounds}: fact_check={verdict.get('fact_check')} winner={winner} hook_score={verdict.get('hook_score')}", flush=True)

        if winner and winner != "NONE" and verdict.get("winner_script"):
            score = float(verdict.get("hook_score", 0))  # đã qua _validate_verdict() coerce được về số, ép kiểu tường minh để so sánh an toàn
            if best_score is None or score > best_score:
                best_script, best_score, best_feedback = verdict["winner_script"], score, verdict.get("feedback")
            if score >= hook_pass_threshold:
                return {"script": verdict["winner_script"], "passed": True, "hook_score": score,
                        "iterations_used": round_i, "history": history, "needs_human_review": False}
        else:
            # Toàn bộ phương án đều fail fact-check -- không có gì để giữ lại
            # làm "best" vòng này, thử lại vòng sau với toàn bộ feedback.
            best_feedback = json.dumps(verdict.get("fact_check", {}), ensure_ascii=False)

    if best_script is None:
        print(f"CẢNH BÁO: sau {max_rounds} vòng KHÔNG có phương án nào qua được fact-check -- DỪNG HẲN, không đăng.", file=sys.stderr)
        return {"script": None, "passed": False, "hook_score": None, "iterations_used": max_rounds, "history": history, "needs_human_review": True}

    print(f"CẢNH BÁO: sau {max_rounds} vòng chưa đạt ngưỡng hook {hook_pass_threshold}/10 -- dùng bản tốt nhất ({best_score}/10), cần người xem lại.", file=sys.stderr)
    return {"script": best_script, "passed": False, "hook_score": best_score, "iterations_used": max_rounds, "history": history, "needs_human_review": True}
