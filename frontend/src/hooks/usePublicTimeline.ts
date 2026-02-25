import { useState, useEffect } from 'react';
import { getPublicTimeline } from '../api/timelines';
import { Timeline } from '../types';

export function usePublicTimeline(timelineId: string) {
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    getPublicTimeline(timelineId)
      .then((data) => { if (!cancelled) setTimeline(data); })
      .catch(() => { if (!cancelled) setError('Timeline not found or not available'); })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [timelineId]);

  return { timeline, isLoading, error };
}
