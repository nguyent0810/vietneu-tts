import { fileURLToPath } from 'node:url'

import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    globals: false,
    // Integration test chạy trên Neon THẬT qua mạng, chậm hơn hẳn unit test.
    testTimeout: 60_000,
    hookTimeout: 60_000,
    setupFiles: ['./tests/setup.ts'],
    // Chạy tuần tự: các test integration dùng chung một database và có
    // TRUNCATE giữa các test, chạy song song sẽ xoá dữ liệu của nhau.
    fileParallelism: false,
    sequence: { concurrent: false },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
