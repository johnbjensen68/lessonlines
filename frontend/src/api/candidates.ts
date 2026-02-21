import client from './client';
import { CandidateEvent, CandidateEventDetail, Event, HarvestBatch } from '../types';

interface CandidateListParams {
  status?: string;
  topic?: string;
  q?: string;
  has_existing_event?: boolean;
  harvest_batch_id?: string;
  limit?: number;
  offset?: number;
}

export async function getHarvestBatches(): Promise<HarvestBatch[]> {
  const response = await client.get<HarvestBatch[]>('/admin/harvest-batches');
  return response.data;
}

export async function getCandidates(params: CandidateListParams = {}): Promise<CandidateEvent[]> {
  const response = await client.get<CandidateEvent[]>('/admin/candidates', { params });
  return response.data;
}

export async function getCandidate(id: string): Promise<CandidateEventDetail> {
  const response = await client.get<CandidateEventDetail>(`/admin/candidates/${id}`);
  return response.data;
}

export async function promoteCandidate(id: string): Promise<Event> {
  const response = await client.post<Event>(`/admin/candidates/${id}/promote`);
  return response.data;
}

export async function rejectCandidate(id: string, reviewNotes?: string): Promise<CandidateEvent> {
  const response = await client.patch<CandidateEvent>(`/admin/candidates/${id}`, {
    status: 'rejected',
    review_notes: reviewNotes || null,
  });
  return response.data;
}
