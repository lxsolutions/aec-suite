

/**
 * Shared TypeScript types for AEC Suite
 */

export interface Project {
  id: string;
  name: string;
  description?: string;
  clientId: string;
  startDate: string;
  endDate?: string;
  budget?: number;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
  orgId: string;
}

export interface Rfp {
  id: string;
  projectId: string;
  filename: string;
  originalFilename: string;
  fileSize: number;
  mimeType: string;
  status: RfpStatus;
  parsedData?: Record<string, any>;
  errorMessage?: string;
  createdAt: string;
  updatedAt: string;
  orgId: string;
}

export interface EstimateItem {
  id: string;
  description: string;
  quantity: number;
  unit: string;
  unitCost: number;
  totalCost: number;
  category: string;
  notes?: string;
}

export interface Estimate {
  id: string;
  projectId: string;
  rfpId: string;
  version: number;
  status: EstimateStatus;
  totalAmount: number;
  items: EstimateItem[];
  notes?: string;
  createdAt: string;
  updatedAt: string;
  orgId: string;
}

export interface Schedule {
  id: string;
  projectId: string;
  estimateId: string;
  startDate: string;
  endDate: string;
  status: ScheduleStatus;
  milestones: Record<string, any>[];
  createdAt: string;
  updatedAt: string;
  orgId: string;
}

export interface AECError {
  traceId?: string;
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Enums
export enum ProjectStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

export enum RfpStatus {
  RECEIVED = 'received',
  PARSING = 'parsing',
  PARSED = 'parsed',
  ERROR = 'error'
}

export enum EstimateStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  READY = 'ready',
  APPROVED = 'approved',
  SYNCED = 'synced'
}

export enum ScheduleStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed'
}

// Event types
export interface ProjectCreatedEvent {
  project: Project;
}

export interface RfpParsedEvent {
  rfp: Rfp;
  parsedItems: Record<string, any>[];
}

export interface EstimateReadyEvent {
  estimate: Estimate;
  schedule?: Schedule;
}

export interface ScheduleUpdatedEvent {
  schedule: Schedule;
}

export interface ERPSyncCompletedEvent {
  estimateId: string;
  erpId: string;
  syncTimestamp: string;
}

