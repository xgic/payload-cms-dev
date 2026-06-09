/**
 * XGIC Payload CMS Dev Container Configuration
 *
 * This file defines the strongly-typed shape of the devcontainer configuration.
 * It is the single source of truth for both runtime validation and
 * editor IntelliSense.
 *
 * @see https://payloadcms.com/docs/getting-started/installation
 */

import { z } from 'zod';

/**
 * Supported Payload starter templates.
 */
export const TemplateSchema = z.enum([
  'blank',
  'website',
  'ecommerce',
  'plugin',
  'payload-demo',
  'payload-website',
]);

export type Template = z.infer<typeof TemplateSchema>;

/**
 * Supported database adapters.
 */
export const DbAdapterSchema = z.enum([
  'postgres',
  'mongodb',
  'sqlite',
  'd1-sqlite',
  'vercel-postgres',
]);

export type DbAdapter = z.infer<typeof DbAdapterSchema>;

/**
 * Coding agent skill to install (or none).
 */
export const AgentSchema = z.enum(['claude', 'codex', 'cursor', 'none']);

export type Agent = z.infer<typeof AgentSchema>;

/**
 * Full configuration schema for create-payload-config.
 *
 * This schema powers:
 * - Runtime validation (in setup scripts)
 * - JSON Schema generation for .json files
 * - Excellent VS Code IntelliSense when using the .ts config approach
 */
export const CreatePayloadConfigSchema = z.object({
  /** The name of the generated Payload project folder (e.g. "website",
   * "my-app") */
  projectName: z
    .string()
    .min(1)
    .regex(/^[a-z0-9-]+$/, 'Must be lowercase, numbers, and hyphens only')
    .describe('The folder name for the generated Payload project'),

  /** Which official Payload starter template to use */
  template: TemplateSchema.default('website'),

  /** Optional: Use a specific Payload example instead of a template */
  example: z.string().nullable().optional(),

  /**
   * Coding agent integration.
   *
   * Use "none" (recommended) when running inside a dev container or CI.
   * This prevents the generated project from having Claude Code / Cursor /
   * Codex skills installed.
   */
  agent: AgentSchema.default('none'),

  /** Database adapter to configure */
  dbAdapter: DbAdapterSchema.default('postgres'),

  /** Logical database name (used for Postgres/Mongo) */
  dbName: z.string().default('payload_db'),

  /** Database user (used for Postgres/Mongo) */
  dbUser: z.string().default('payload'),

  /**
   * Full database connection string.
   *
   * IMPORTANT: In the devcontainer flow, this value is usually overridden at
   * runtime from the live .devcontainer/.env (which contains the real
   * random password).
   * You may leave a placeholder here — it will be replaced during creation.
   */
  dbUri: z
    .string()
    .optional()
    .describe(
      'Database connection URI. Secrets are injected from the live '
      + 'environment at creation time.'
    ),

  /** Default admin email for the first user */
  adminEmail: z.string().email().default('admin@example.com'),

  /** Whether to enable Payload telemetry */
  telemetry: z.boolean().default(false),
});

export type CreatePayloadConfig = z.infer<typeof CreatePayloadConfigSchema>;

/**
 * Helper to validate a config object at runtime (used by Python + TS tooling).
 */
export function validateCreatePayloadConfig(
  input: unknown
): CreatePayloadConfig {
  return CreatePayloadConfigSchema.parse(input);
}

/**
 * Safe parse (returns result instead of throwing).
 */
export function safeParseCreatePayloadConfig(input: unknown) {
  return CreatePayloadConfigSchema.safeParse(input);
}
