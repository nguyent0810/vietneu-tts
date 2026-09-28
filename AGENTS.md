# AGENTS.md

File hướng dẫn chung cho mọi coding agent làm việc trên repo này. Codex CLI đọc `AGENTS.md`; Claude Code cũng tự đọc `AGENTS.md` khi không có `CLAUDE.md`. Vì vậy repo chỉ giữ một file: **không tạo `CLAUDE.md` song song**. Nếu sau này buộc phải có `CLAUDE.md`, file đó chỉ chứa dòng `@AGENTS.md`.

## Agent skills

### Issue tracker

Spec và ticket nằm local trong `.scratch/<feature>/`, chưa đưa lên GitHub khi chưa được duyệt. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` ở gốc repo. See `docs/agents/domain.md`.
