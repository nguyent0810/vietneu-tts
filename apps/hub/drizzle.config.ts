import { config } from 'dotenv'
import { defineConfig } from 'drizzle-kit'

// drizzle-kit chạy ngoài Next.js nên không tự nạp .env.local.
config({ path: '.env.local' })
config({ path: '.env' })

export default defineConfig({
  schema: './src/db/schema/index.ts',
  out: './drizzle',
  dialect: 'postgresql',
  casing: 'snake_case',
  dbCredentials: {
    url: process.env.DATABASE_URL ?? '',
  },
  strict: true,
  verbose: true,
})
