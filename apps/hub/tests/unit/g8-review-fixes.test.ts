import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

// @ts-expect-error — module JS thuần, dùng chung với `attempt_table.mjs`.
import { artifactIndexGateOk, BATCH_CONTRACT_COLUMNS, mixedAcrossBatch } from '../../attempt_accounting.mjs'

import { parseStoredCompositePayload } from '@/lib/cursor/composite'
import {
  buildArtifactFile,
  buildIndexJson,
  missingIdentityFields,
  runIdentity,
  shouldWriteArtifact,
} from '@/lib/cursor/identity'
import { checkProvenanceCoverage, PROVENANCE_MATRIX } from '@/lib/cursor/provenance'
import { CONTRACT_PROVENANCE } from '@/lib/cursor/run'
import {
  COMPOSITE_VALIDATOR_VERSION,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  OBLIGATION_GENERATOR_VERSION,
} from '@/lib/cursor/schema'
import type { RunCursorAnalysisResult } from '@/lib/cursor/run'

/**
 * HỒI QUY cho các khiếm khuyết do rà soát đối kháng G8 tìm ra.
 *
 * Mỗi ca ở đây tương ứng một khiếm khuyết THẬT đã đi lọt qua toàn bộ cổng trước
 * đó. Giữ chúng lại vì cả bốn đều thuộc loại hỏng IM LẶNG: không có ngoại lệ,
 * không có log, chỉ có một con số sai hoặc một trường biến mất.
 */

const BODY = {
  schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
  analysisSummary: {
    overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
    confidence: 'MEDIUM',
    confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ trong cửa sổ quan sát này.',
    primaryConstraint: 'Cỡ mẫu còn nhỏ nên kết luận xu hướng cần thận trọng.',
  },
  keyFindings: [
    {
      id: 'F-001',
      statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
      findingType: 'OBSERVATION',
      confidence: 'MEDIUM',
      evidenceIds: ['OBS-001'],
      supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
      contradictingEvidenceIds: [],
      limitations: [],
    },
  ],
  hypotheses: [],
  recommendations: [],
  experiments: [],
  manualReviewTargets: [],
  dataRequests: [],
  explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
  metricClaims: [],
  selfCheck: {
    usedOnlyProvidedEvidence: true,
    recomputedMetrics: false,
    madeCausalClaims: false,
    madeCtrOrImpressionClaims: false,
    allFindingEvidenceResolved: true,
  },
}

const META = {
  analysisExecutionId: 'a-1',
  declarationExecutionId: 'd-1',
  analysisPayloadHash: 'a'.repeat(64),
  obligationSetHash: 'b'.repeat(64),
  obligationCount: 3,
  obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION,
  compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
}

describe('G8/B2 — `_meta` mang phiên bản GIẢ phải bị chặn', () => {
  it('phiên bản bộ sinh nghĩa vụ khác mã đang chạy -> chặn', () => {
    const r = parseStoredCompositePayload({
      ...BODY,
      _meta: { ...META, obligationGeneratorVersion: 'bịa-đặt' },
    })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_meta_version_drift')
  })

  it('phiên bản bộ kiểm hợp nhất khác mã đang chạy -> chặn', () => {
    const r = parseStoredCompositePayload({
      ...BODY,
      _meta: { ...META, compositeValidatorVersion: '0.9' },
    })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_meta_version_drift')
  })

  it('phiên bản ĐÚNG -> cho qua', () => {
    const r = parseStoredCompositePayload({ ...BODY, _meta: META })
    expect(r.ok, JSON.stringify(r.issues)).toBe(true)
  })
})

describe('G8/C3 — giá trị SENTINEL không được coi là nguồn gốc hợp lệ', () => {
  it('`unavailable` bị tính là THIẾU, không phải là giá trị', () => {
    const full: Record<string, unknown> = {}
    for (const f of PROVENANCE_MATRIX.resultRow.required) full[f] = `x-${f}`
    const r = checkProvenanceCoverage(
      { resultRow: { ...full, payloadHash: 'unavailable' } },
      ['resultRow'],
    )
    expect(r.ok).toBe(false)
    expect(r.missing).toContainEqual({ surface: 'resultRow', field: 'payloadHash' })
  })

  it('chuỗi rỗng cũng bị tính là THIẾU', () => {
    const full: Record<string, unknown> = {}
    for (const f of PROVENANCE_MATRIX.resultRow.required) full[f] = `x-${f}`
    const r = checkProvenanceCoverage({ resultRow: { ...full, payloadHash: '' } }, ['resultRow'])
    expect(r.ok).toBe(false)
  })

  it('bản ghi nguồn gốc THẬT không chứa sentinel nào', () => {
    // Nếu ca này đỏ thì môi trường build đang thiếu git/lockfile/tệp nguồn, và
    // mọi lô đo chạy trong môi trường ấy KHÔNG có nguồn gốc dùng được.
    for (const [k, v] of Object.entries(CONTRACT_PROVENANCE)) {
      if (typeof v !== 'string') continue
      expect(v, `\`CONTRACT_PROVENANCE.${k}\` là sentinel "${v}"`).not.toBe('unavailable')
      expect(v, `\`CONTRACT_PROVENANCE.${k}\` rỗng`).not.toBe('')
    }
  })
})

/** Kết quả chạy TỐI THIỂU, đủ để `runIdentity` làm việc. */
const RUN = {
  requestId: 'req-1',
  channelLabel: 'hinh_su',
  packageHash: 'p'.repeat(64),
  promptHash: 'q'.repeat(64),
  promptBytes: 100,
  attempts: [],
  finalAttempt: 1,
  output: BODY as never,
  report: null,
  status: 'SUCCEEDED',
  analysisAttempts: [{}] as never,
  declarationAttempts: [{}, {}] as never,
  analysisExecutionId: 'exec-a',
  obligationCount: 3,
  obligationSetHash: 'b'.repeat(64),
  analysisPayloadHash: 'a'.repeat(64),
  declarations: null,
  declarationPromptBytes: 10,
  declarationExecutionId: 'exec-d',
  compositeValidationId: 'val-c',
  resultId: 'res-1',
  compositePayloadHash: 'c'.repeat(64),
  analysisRunId: 'run-1',
  channelId: 'ch-1',
} as unknown as RunCursorAnalysisResult

describe('G8/C1 — `_meta` của artifact KHÔNG được bị payload ghi đè', () => {
  it('giữ nguyên các trường chỉ có lúc GHI TỆP', () => {
    // Bản trước viết `{ _meta: buildArtifactMeta(...), ...r.output }`. Vì
    // `r.output` mang `_meta` riêng, spread ghi đè ngược lại và tệp mất sạch
    // `resultId`, `compositeValidationId`, số lần thử, `writtenAt`.
    const file = buildArtifactFile(
      { ...BODY, _meta: { analysisExecutionId: 'exec-a', obligationCount: 3 } },
      RUN,
      CONTRACT_PROVENANCE,
      {
        channelLabel: 'hinh_su',
        durationMs: 5,
        writtenAt: '2026-08-06T00:00:00Z',
        outputSchemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      },
    )
    const meta = file._meta as Record<string, unknown>
    expect(meta.resultId).toBe('res-1')
    expect(meta.compositeValidationId).toBe('val-c')
    expect(meta.declarationExecutionId).toBe('exec-d')
    expect(meta.writtenAt).toBe('2026-08-06T00:00:00Z')
    expect(meta.analysisAttempts).toBe(1)
    expect(meta.declarationAttempts).toBe(2)
    expect(meta.gitCommit).toBe(CONTRACT_PROVENANCE.gitCommit)
  })

  it('thân payload vẫn nguyên vẹn và KHÔNG còn `_meta` lồng', () => {
    const file = buildArtifactFile({ ...BODY, _meta: { x: 1 } }, RUN, CONTRACT_PROVENANCE, {
      channelLabel: 'hinh_su', durationMs: 5, writtenAt: 'z', outputSchemaVersion: '3.0',
    })
    expect(file.keyFindings).toEqual(BODY.keyFindings)
    expect((file as Record<string, unknown>).x).toBeUndefined()
  })

  it('`_meta` của artifact qua được MA TRẬN PHỦ', () => {
    const file = buildArtifactFile({ ...BODY, _meta: {} }, RUN, CONTRACT_PROVENANCE, {
      channelLabel: 'hinh_su', durationMs: 5, writtenAt: 'z', outputSchemaVersion: '3.0',
    })
    const r = checkProvenanceCoverage(
      { artifactMeta: file._meta as Record<string, unknown> },
      ['artifactMeta'],
    )
    expect(r.missing, JSON.stringify(r.missing)).toEqual([])
  })
})

describe('G8/C2 — `INDEX.json` phải mang tally VÀ danh tính', () => {
  const idx = () =>
    buildIndexJson({
      contract: CONTRACT_PROVENANCE,
      generatedAt: '2026-08-06T00:00:00Z',
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      mode: 'successes=3',
      tally: { hinh_su: { attempts: 4, successes: 3, timeouts: 0, validationFails: 1, other: 0 } },
      identities: { hinh_su: [runIdentity(RUN)] },
      filesFor: () => ['hinh_su.cursor.s1.json'],
    })

  it('mang đủ tally, gồm cả cột THẤT BẠI', () => {
    const ch = (idx().channels as Record<string, Record<string, unknown>>).hinh_su!
    expect(ch.attempts).toBe(4)
    expect(ch.successes).toBe(3)
    // Lần thất bại phải hiện diện: mẫu số của lô là 4, không phải 3.
    expect(ch.validationFails).toBe(1)
  })

  it('mang DANH TÍNH đủ để lần ngược về database', () => {
    const ch = (idx().channels as Record<string, Record<string, unknown>>).hinh_su!
    const id = (ch.identities as Array<Record<string, unknown>>)[0]!
    for (const k of [
      'requestId', 'analysisRunId', 'channelId', 'analysisExecutionId',
      'declarationExecutionId', 'compositeValidationId', 'resultId',
    ]) {
      expect(id[k], `INDEX.json thiếu danh tính "${k}"`).toBeTruthy()
    }
  })

  it('mang nguồn gốc hợp đồng và qua được MA TRẬN PHỦ', () => {
    const r = checkProvenanceCoverage({ indexJson: idx() }, ['indexJson'])
    expect(r.missing, JSON.stringify(r.missing)).toEqual([])
  })
})

describe('G-R4 — lỗ hổng nguồn gốc do rà soát subagent tìm ra', () => {
  it('C-1: `sensitive.ts` được băm như một HỢP ĐỒNG', () => {
    // Tệp này định nghĩa "ô nào phải khai báo" và được import bởi CẢ bộ sinh
    // nghĩa vụ lẫn bộ kiểm định. Trước đây không băm nào phủ nó, và vì tệp chưa
    // được git theo dõi nên `gitDirtyDiffHash` cũng mù — sửa một regex là đổi
    // ngữ nghĩa U3/S1 với nguồn gốc giống hệt từng byte.
    const c = CONTRACT_PROVENANCE as unknown as Record<string, string>
    expect(c.sensitiveLexiconHash, 'thiếu băm từ điển ô nhạy cảm').toMatch(/^[0-9a-f]{64}$/)
    expect(c.identitySourceHash).toMatch(/^[0-9a-f]{64}$/)
    expect(c.provenanceSourceHash).toMatch(/^[0-9a-f]{64}$/)
    // Và nó phải khác các băm khác — nếu trùng thì ai đó băm nhầm tệp.
    expect(c.sensitiveLexiconHash).not.toBe(c.obligationGeneratorHash)
    expect(c.sensitiveLexiconHash).not.toBe(c.validatorHash)
  })

  it('C-1: MỌI tệp quyết định ngữ nghĩa đều có băm riêng trong ma trận', () => {
    for (const f of ['sensitiveLexiconHash', 'identitySourceHash', 'provenanceSourceHash']) {
      expect(
        PROVENANCE_MATRIX.storedMeta.required.includes(f),
        `"${f}" không nằm trong trường BẮT BUỘC của storedMeta`,
      ).toBe(true)
    }
  })

  it('C-2: `_meta` artifact mang `llmExecutionId` — khoá mà bộ kiểm tra cứu', () => {
    const file = buildArtifactFile({ ...BODY, _meta: {} }, RUN, CONTRACT_PROVENANCE, {
      channelLabel: 'hinh_su', durationMs: 5, writtenAt: 'z', outputSchemaVersion: '3.0',
    })
    const meta = file._meta as Record<string, unknown>
    expect(meta.llmExecutionId, '`attempt_table.mjs` tra đúng khoá này').toBe('exec-d')
    expect(meta.llmExecutionId).toBe(meta.declarationExecutionId)
  })

  it('C-2: lần chạy ĐẠT không được thiếu `llmExecutionId`', () => {
    expect(missingIdentityFields(runIdentity(RUN))).toEqual([])
    const noExec = { ...RUN, declarationExecutionId: null, analysisExecutionId: null } as never
    expect(missingIdentityFields(runIdentity(noExec))).toContain('llmExecutionId')
  })

  it('C-3: thiếu INDEX.json phải làm HỎNG cổng — kiểm bằng CHẠY', () => {
    /*
     * Bản trước `grep` một đoạn 260 ký tự quanh chữ "thiếu INDEX.json" tìm chuỗi
     * `gateOk = false`. Xoá hẳn lệnh gán THẬT mà để lại chuỗi ấy trong một chú
     * thích lân cận thì test vẫn xanh — đúng khuôn mẫu không-thể-sai mà chính
     * tệp này cảnh báo ngay bên dưới. Nay gọi hàm thật.
     */
    expect(artifactIndexGateOk({ indexExists: false }), 'thiếu INDEX mà cổng vẫn ĐẠT').toBe(false)
    expect(artifactIndexGateOk({ indexExists: true, declaredFilesMissing: 1 })).toBe(false)
    expect(artifactIndexGateOk({ indexExists: true, declaredFilesMissing: 0 })).toBe(true)
    // Và `attempt_table.mjs` phải THẬT SỰ dùng hàm này, không tự quyết định lại.
    const src = readFileSync(new URL('../../attempt_table.mjs', import.meta.url), 'utf8')
    expect(src).toContain('artifactIndexGateOk({ indexExists: false })')
  })

  /*
   * C-4 / M-4 — phép kiểm này từng KHÔNG THỂ SAI.
   *
   * Bản trước `grep` mã nguồn `attempt_table.mjs` tìm chuỗi `'schema_hash'` giữa
   * hai mốc. Reviewer chứng minh bằng mutation: xoá hẳn dòng so THẬT, test vẫn
   * xanh — vì tên cột còn nằm trong câu SELECT ngay phía trên. Nay bộ test CHẠY
   * chính hàm mà `attempt_table.mjs` gọi và khẳng định trên GIÁ TRỊ TRẢ VỀ.
   */
  describe('C-4/M-4: băm mã nguồn được so ở mức LÔ — kiểm bằng CHẠY', () => {
    const row = (over: Record<string, unknown> = {}) => ({
      obligation_generator_version: '1.0',
      declaration_prompt_version: '1.0.0',
      declaration_prompt_source_hash: 'd'.repeat(64),
      composite_validator_version: '1.0',
      schema_hash: 's'.repeat(64),
      prompt_source_hash: 'p'.repeat(64),
      obligation_generator_hash: 'o'.repeat(64),
      composite_source_hash: 'c'.repeat(64),
      sensitive_lexicon_hash: 'x'.repeat(64),
      identity_source_hash: 'i'.repeat(64),
      provenance_source_hash: 'v'.repeat(64),
      ...over,
    })

    it('lô đồng nhất -> KHÔNG báo động', () => {
      expect(mixedAcrossBatch([row(), row(), row()])).toEqual([])
    })

    it('mỗi cột hợp đồng: đổi giá trị giữa chừng -> BỊ BẮT', () => {
      // Từng cột một. Một cột rơi khỏi danh sách sẽ làm đỏ đúng cột đó.
      for (const col of BATCH_CONTRACT_COLUMNS) {
        const mixed = mixedAcrossBatch([row(), row({ [col]: 'KHÁC' })])
        expect(mixed.map((m: { column: string }) => m.column), `"${col}" không được so ở mức lô`)
          .toContain(col)
      }
    })

    it('M-3: sửa `sensitive.ts` giữa hai kênh của một lô -> BỊ BẮT', () => {
      // Đây là ca cụ thể mà M-3 nêu: đổi ĐỊNH NGHĨA "ô nào phải khai báo" giữa
      // chừng. Trước 0035 không có cột nào để so, nên lô trộn hai định nghĩa vẫn
      // in "sạch".
      const mixed = mixedAcrossBatch([
        row({ sensitive_lexicon_hash: 'a'.repeat(64) }),
        row({ sensitive_lexicon_hash: 'b'.repeat(64) }),
      ])
      expect(mixed.map((m: { column: string }) => m.column)).toContain('sensitive_lexicon_hash')
    })

    it('hàng NULL (một lượt / trước 0035) KHÔNG tạo báo động giả', () => {
      // "không ghi" khác hẳn "ghi khác". Nếu NULL bị tính là một giá trị thì mọi
      // lô có lẫn dữ liệu cũ đều đỏ, và một cổng luôn đỏ thì bị bỏ qua.
      const mixed = mixedAcrossBatch([row(), row({ sensitive_lexicon_hash: null })])
      expect(mixed).toEqual([])
    })

    it('`attempt_table.mjs` dùng ĐÚNG hàm này, không tự viết lại', () => {
      const src = readFileSync(new URL('../../attempt_table.mjs', import.meta.url), 'utf8')
      expect(src).toContain('mixedAcrossBatch(r.rows)')
    })
  })
})

describe('G-R6 — artifact CHỈ được ghi khi lần chạy ĐƯỢC CẤP PHÉP', () => {
  it('lần chạy ĐẠT có kết quả chính thức -> ghi', () => {
    expect(shouldWriteArtifact(RUN)).toBe(true)
  })

  it('cạn ngân sách khai báo: có `output` nhưng KHÔNG đạt -> KHÔNG ghi', () => {
    // Nhánh này gán `output = văn xuôi phân tích` để giữ bằng chứng. Ghi nó ra
    // sẽ ĐÈ LÊN ô `.s{n}` của mẫu đạt gần nhất, vì `successes` chưa tăng.
    const failed = { ...RUN, status: 'REJECTED_SCHEMA', resultId: null } as never
    expect(shouldWriteArtifact(failed)).toBe(false)
  })

  it('hỏng bộ sinh nghĩa vụ: FAILED kèm `output` -> KHÔNG ghi', () => {
    const sysFail = { ...RUN, status: 'FAILED', resultId: null } as never
    expect(shouldWriteArtifact(sysFail)).toBe(false)
  })

  it('ĐẠT nhưng THIẾU id kết quả -> KHÔNG ghi (không có đường tắt nào khác)', () => {
    const noResult = { ...RUN, status: 'SUCCEEDED', resultId: null } as never
    expect(shouldWriteArtifact(noResult)).toBe(false)
  })
})
