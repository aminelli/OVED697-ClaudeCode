export type Priority = 'critical' | 'high' | 'medium' | 'low';
export type Category = 'billing' | 'technical' | 'account' | 'complaint' | 'feature-request' | 'general';
export type Sentiment = 'frustrated' | 'neutral' | 'satisfied';
export type TicketStatus = 'unprocessed' | 'processing' | 'classified' | 'draft-ready' | 'approved' | 'rejected';

export interface Classification {
  'artifact:category': Category;
  'artifact:priority': Priority;
  'artifact:sentiment': Sentiment;
  'artifact:tags': string[];
  'artifact:summary': string;
}

export interface Draft {
  'artifact:status': TicketStatus;
  'artifact:tone': string;
  'artifact:subject': string;
  'artifact:placeholders-count': number;
  body: string;
}

export interface Ticket {
  id: string;
  content: string;
  classification: Classification | null;
  draft: Draft | null;
  status: TicketStatus;
}
