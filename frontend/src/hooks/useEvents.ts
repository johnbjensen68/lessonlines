import { useState, useEffect, useCallback } from 'react';
import { searchEvents, getTopics } from '../api/events';
import { EventListItem, Topic } from '../types';

interface UseEventsOptions {
  initialTopic?: string;
}

export function useEvents(options: UseEventsOptions = {}) {
  const [events, setEvents] = useState<EventListItem[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(options.initialTopic || null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTopics();
  }, []);

  useEffect(() => {
    loadEvents();
  }, [selectedTopic, searchQuery]);

  const loadTopics = async () => {
    try {
      const data = await getTopics();
      setTopics(data);
      if (data.length > 0 && !selectedTopic) {
        setSelectedTopic(data[0].slug);
      }
    } catch {
      setError('Failed to load topics');
    }
  };

  const loadEvents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: { topic?: string; q?: string } = {};
      if (selectedTopic) params.topic = selectedTopic;
      if (searchQuery) params.q = searchQuery;
      const data = await searchEvents(params);
      setEvents(data);
    } catch {
      setError('Failed to load events');
    } finally {
      setIsLoading(false);
    }
  }, [selectedTopic, searchQuery]);

  const selectTopic = (topicSlug: string | null) => {
    setSelectedTopic(topicSlug);
  };

  const search = (query: string) => {
    setSearchQuery(query);
  };

  return {
    events,
    topics,
    selectedTopic,
    searchQuery,
    isLoading,
    error,
    selectTopic,
    search,
    refresh: loadEvents,
  };
}
