export type TicketStateStatus = 'unprocessed' | 'processing' | 'classified' | 'draft-ready' | 'approved' | 'rejected';

export interface TicketState {
  status: TicketStateStatus;
  classification_artifact: string | null;
  draft_artifact: string | null;
  steps_completed: string[];
  current_step: string | null;
  errors: string[];
}

export interface GlobalStats {
  total_processed: number;
  pending_review: number;
}

export interface PipelineState {
  pipeline_version: string;
  last_updated: string;
  tickets: Record<string, TicketState>;
  global: GlobalStats;
}
