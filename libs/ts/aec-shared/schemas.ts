


/**
 * Zod schemas for AEC Suite types
 */

import { z } from 'zod';

// Enums
export const ProjectStatusSchema = z.enum(['draft', 'active', 'completed', 'archived']);
export const RfpStatusSchema = z.enum(['received', 'parsing', 'parsed', 'error']);
export const EstimateStatusSchema = z.enum(['draft', 'pending', 'ready', 'approved', 'synced']);
export const ScheduleStatusSchema = z.enum(['draft', 'in_progress', 'completed']);

// Base schemas
export const EstimateItemSchema = z.object({
  id: z.string().uuid(),
  description: z.string(),
  quantity: z.number().positive(),
  unit: z.string(),
  unitCost: z.number().positive(),
  totalCost: z.number().positive(),
  category: z.string(),
  notes: z.string().optional(),
});

export const ProjectSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  description: z.string().optional(),
  clientId: z.string(),
  startDate: z.string().datetime(),
  endDate: z.string().datetime().optional(),
  budget: z.number().positive().optional(),
  status: ProjectStatusSchema,
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  orgId: z.string(),
});

export const RfpSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  filename: z.string(),
  originalFilename: z.string(),
  fileSize: z.number().positive(),
  mimeType: z.string(),
  status: RfpStatusSchema,
  parsedData: z.record(z.any()).optional(),
  errorMessage: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  orgId: z.string(),
});

export const EstimateSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  rfpId: z.string().uuid(),
  version: z.number().int().positive(),
  status: EstimateStatusSchema,
  totalAmount: z.number().nonnegative(),
  items: z.array(EstimateItemSchema),
  notes: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  orgId: z.string(),
});

export const ScheduleSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  estimateId: z.string().uuid(),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  status: ScheduleStatusSchema,
  milestones: z.array(z.record(z.any())),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  orgId: z.string(),
});

// Error schema
export const AECErrorSchema = z.object({
  traceId: z.string().uuid().optional(),
  code: z.string(),
  message: z.string(),
  details: z.record(z.any()).optional(),
});

// Event schemas
export const ProjectCreatedEventSchema = z.object({
  project: ProjectSchema,
});

export const RfpParsedEventSchema = z.object({
  rfp: RfpSchema,
  parsedItems: z.array(z.record(z.any())),
});

export const EstimateReadyEventSchema = z.object({
  estimate: EstimateSchema,
  schedule: ScheduleSchema.optional(),
});

export const ScheduleUpdatedEventSchema = z.object({
  schedule: ScheduleSchema,
});

export const ERPSyncCompletedEventSchema = z.object({
  estimateId: z.string().uuid(),
  erpId: z.string(),
  syncTimestamp: z.string().datetime(),
});

// Type inference
export type Project = z.infer<typeof ProjectSchema>;
export type Rfp = z.infer<typeof RfpSchema>;
export type EstimateItem = z.infer<typeof EstimateItemSchema>;
export type Estimate = z.infer<typeof EstimateSchema>;
export type Schedule = z.infer<typeof ScheduleSchema>;
export type AECError = z.infer<typeof AECErrorSchema>;
export type ProjectCreatedEvent = z.infer<typeof ProjectCreatedEventSchema>;
export type RfpParsedEvent = z.infer<typeof RfpParsedEventSchema>;
export type EstimateReadyEvent = z.infer<typeof EstimateReadyEventSchema>;
export type ScheduleUpdatedEvent = z.infer<typeof ScheduleUpdatedEventSchema>;
export type ERPSyncCompletedEvent = z.infer<typeof ERPSyncCompletedEventSchema>;


