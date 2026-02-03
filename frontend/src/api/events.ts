import client from './client';
import { EventListItem, Event, Topic, Tag } from '../types';

interface EventSearchParams {
  topic?: string;
  q?: string;
  standard?: string;
  tag?: string;
  grade?: string;
}

export async function searchEvents(params: EventSearchParams = {}): Promise<EventListItem[]> {
  const response = await client.get<EventListItem[]>('/events', { params });
  return response.data;
}

export async function getEvent(eventId: string): Promise<Event> {
  const response = await client.get<Event>(`/events/${eventId}`);
  return response.data;
}

export async function getTopics(): Promise<Topic[]> {
  const response = await client.get<Topic[]>('/topics');
  return response.data;
}

export async function getTags(category?: string): Promise<Tag[]> {
  const response = await client.get<Tag[]>('/tags', { params: { category } });
  return response.data;
}
