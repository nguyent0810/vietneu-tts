/**
 * CUỘN LẠI 0023–0026 trên MỘT database.
 *
 * Dùng khi hai database phân kỳ. Không đoán định nghĩa cũ: hàm trigger được KHÔI
 * PHỤC TỪ CHÍNH TỆP MIGRATION 0020/0022, không gõ lại bằng tay.
 */
import { readFileSync } from 'node:fs'
import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import ws from 'ws'
neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

const target = process.argv[2]
const url = target === 'MAIN' ? process.env.DATABASE_URL
          : target === 'TEST' ? process.env.TEST_DATABASE_URL : null
if (!url) { console.error('Dùng: node rollback_g3.mjs MAIN|TEST'); process.exit(2) }

/** Lấy khối CREATE OR REPLACE FUNCTION ... $$ LANGUAGE plpgsql; từ tệp migration. */
function fnFrom(file, name) {
  const sql = readFileSync(`drizzle/${file}`, 'utf8')
  const start = sql.indexOf(`CREATE OR REPLACE FUNCTION ${name}()`)
  if (start === -1) throw new Error(`không thấy hàm ${name} trong ${file}`)
  const end = sql.indexOf('$$ LANGUAGE plpgsql;', start)
  if (end === -1) throw new Error(`không thấy kết thúc hàm ${name} trong ${file}`)
  return sql.slice(start, end + '$$ LANGUAGE plpgsql;'.length)
}

const restoreLineage = fnFrom('0022_result_requires_validation.sql', 'cursor_result_semantic_lineage')
const restoreRepair = fnFrom('0020_repair_same_request.sql', 'cursor_repair_version_immutable')

const c = new Client({ connectionString: url })
await c.connect()
console.log(`Cuộn lại trên ${target} @ ${new URL(url).host}`)
try {
  await c.query('BEGIN')
  const before = (await c.query('SELECT count(*)::int n FROM drizzle.__drizzle_migrations')).rows[0].n
  const res = (await c.query('SELECT count(*)::int n FROM cursor_analysis_result')).rows[0].n
  if (res > 0) throw new Error(`ĐỪNG: ${target} có ${res} dòng kết quả — không cuộn lại database có dữ liệu`)

  await c.query(restoreLineage)
  await c.query(restoreRepair)

  await c.query('DROP TABLE IF EXISTS cursor_claim_obligation')
  await c.query('DROP FUNCTION IF EXISTS cursor_obligation_immutable()')

  await c.query('DROP INDEX IF EXISTS analysis_validation_execution_stage_key')
  await c.query('ALTER TABLE analysis_validation DROP COLUMN IF EXISTS stage')
  await c.query('CREATE UNIQUE INDEX IF NOT EXISTS analysis_validation_execution_key ON analysis_validation USING btree (llm_execution_id)')
  await c.query('DROP TYPE IF EXISTS validation_stage')

  await c.query('ALTER TABLE cursor_analysis_result DROP CONSTRAINT IF EXISTS cursor_result_composite_requires_lineage')
  await c.query('ALTER TABLE cursor_analysis_result DROP CONSTRAINT IF EXISTS cursor_result_lineage_hash_format')
  for (const col of ['result_role','analysis_payload_hash','obligation_set_hash'])
    await c.query(`ALTER TABLE cursor_analysis_result DROP COLUMN IF EXISTS ${col}`)
  await c.query('DROP TYPE IF EXISTS cursor_result_role')

  await c.query('ALTER TABLE cursor_execution_manifest DROP CONSTRAINT IF EXISTS cursor_manifest_role_lineage')
  await c.query('ALTER TABLE cursor_execution_manifest DROP CONSTRAINT IF EXISTS cursor_manifest_declaration_hash_format')
  await c.query('ALTER TABLE cursor_execution_manifest DROP CONSTRAINT IF EXISTS cursor_manifest_analysis_execution_run_fk')
  for (const col of ['execution_role','analysis_execution_id','obligation_generator_version',
                     'declaration_prompt_version','declaration_prompt_source_hash',
                     'composite_validator_version','analysis_payload_hash','obligation_set_hash'])
    await c.query(`ALTER TABLE cursor_execution_manifest DROP COLUMN IF EXISTS ${col}`)
  await c.query('DROP TYPE IF EXISTS cursor_execution_role')

  await c.query(`DELETE FROM drizzle.__drizzle_migrations WHERE created_at IN (
    SELECT created_at FROM drizzle.__drizzle_migrations ORDER BY created_at DESC LIMIT 4)`)

  const after = (await c.query('SELECT count(*)::int n FROM drizzle.__drizzle_migrations')).rows[0].n
  if (after !== before - 4) throw new Error(`số migration sau khi cuộn: ${after}, mong đợi ${before - 4}`)
  await c.query('COMMIT')
  console.log(`${target}: đã cuộn lại ${before} -> ${after} migration`)
} catch (e) {
  await c.query('ROLLBACK')
  console.error(`${target}: CUỘN LẠI THẤT BẠI, đã ROLLBACK:`, e.message)
  process.exitCode = 1
} finally { await c.end() }
