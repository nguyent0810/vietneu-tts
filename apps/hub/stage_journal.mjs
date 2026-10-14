/**
 * Bày journal để áp ĐÚNG N migration mới đầu tiên.
 *
 * Drizzle áp mọi migration đang chờ trong MỘT transaction. Tiện cho an toàn,
 * nhưng khiến "áp từng cái rồi kiểm từng cái" là bất khả — và chính vì không làm
 * được điều đó mà 0026 đi tới TEST trước khi ai kịp biết nó hỏng trên MAIN.
 */
import { readFileSync, writeFileSync } from 'node:fs'
const full = JSON.parse(readFileSync('/tmp/_journal_full.json', 'utf8'))
const n = Number(process.argv[2])
const base = full.entries.filter((e) => e.idx < 23)
if (base.length !== 23) throw new Error(`nền có ${base.length} mục, mong đợi 23`)
const staged = full.entries.filter((e) => e.idx >= 23).slice(0, n)
writeFileSync('drizzle/meta/_journal.json',
  JSON.stringify({ ...full, entries: [...base, ...staged] }, null, 2) + '\n')
console.log(`journal: ${base.length + staged.length} mục` +
  (staged.length ? ` (mới: ${staged.map((e) => e.tag).join(', ')})` : ' (chỉ nền)'))
