import client from './client';
import { Timeline, TimelineCreate, TimelineUpdate, TimelineEventCreate } from '../types';

export async function getTimelines(): Promise<Timeline[]> {
  const response = await client.get<Timeline[]>('/timelines');
  return response.data;
}

export async function getTimeline(id: string): Promise<Timeline> {
  const response = await client.get<Timeline>(`/timelines/${id}`);
  return response.data;
}

export async function createTimeline(data: TimelineCreate): Promise<Timeline> {
  const response = await client.post<Timeline>('/timelines', data);
  return response.data;
}

export async function updateTimeline(id: string, data: TimelineUpdate): Promise<Timeline> {
  const response = await client.put<Timeline>(`/timelines/${id}`, data);
  return response.data;
}

export async function deleteTimeline(id: string): Promise<void> {
  await client.delete(`/timelines/${id}`);
}

export async function addEventToTimeline(
  timelineId: string,
  data: TimelineEventCreate
): Promise<Timeline> {
  const response = await client.post<Timeline>(`/timelines/${timelineId}/events`, data);
  return response.data;
}

export async function removeEventFromTimeline(
  timelineId: string,
  position: number
): Promise<Timeline> {
  const response = await client.delete<Timeline>(`/timelines/${timelineId}/events/${position}`);
  return response.data;
}

export async function reorderTimelineEvents(
  timelineId: string,
  positions: string[]
): Promise<Timeline> {
  const response = await client.put<Timeline>(`/timelines/${timelineId}/events/reorder`, {
    positions,
  });
  return response.data;
}

export async function exportTimelinePdf(timelineId: string): Promise<Blob> {
  const response = await client.post(`/timelines/${timelineId}/export/pdf`, null, {
    responseType: 'blob',
  });
  return response.data;
}
