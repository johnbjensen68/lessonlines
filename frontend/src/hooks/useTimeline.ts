import { useState, useEffect, useCallback, useRef } from 'react';
import {
  getTimeline,
  updateTimeline,
  addEventToTimeline,
  removeEventFromTimeline,
  reorderTimelineEvents,
} from '../api/timelines';
import { Timeline, TimelineUpdate, TimelineEventCreate } from '../types';

const AUTOSAVE_DELAY = 1000;

export function useTimeline(timelineId: string) {
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const pendingChangesRef = useRef<TimelineUpdate | null>(null);

  useEffect(() => {
    loadTimeline();
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [timelineId]);

  const loadTimeline = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTimeline(timelineId);
      setTimeline(data);
    } catch {
      setError('Failed to load timeline');
    } finally {
      setIsLoading(false);
    }
  };

  const saveChanges = useCallback(async (changes: TimelineUpdate) => {
    if (!timeline) return;

    setIsSaving(true);
    try {
      const updated = await updateTimeline(timeline.id, changes);
      setTimeline(updated);
      pendingChangesRef.current = null;
    } catch {
      setError('Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  }, [timeline]);

  const debouncedSave = useCallback((changes: TimelineUpdate) => {
    pendingChangesRef.current = {
      ...pendingChangesRef.current,
      ...changes,
    };

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(() => {
      if (pendingChangesRef.current) {
        saveChanges(pendingChangesRef.current);
      }
    }, AUTOSAVE_DELAY);
  }, [saveChanges]);

  const update = useCallback((changes: TimelineUpdate) => {
    if (!timeline) return;

    setTimeline({
      ...timeline,
      ...changes,
    });

    debouncedSave(changes);
  }, [timeline, debouncedSave]);

  const addEvent = useCallback(async (data: TimelineEventCreate) => {
    if (!timeline) return;

    setIsSaving(true);
    try {
      const updated = await addEventToTimeline(timeline.id, data);
      setTimeline(updated);
    } catch {
      setError('Failed to add event');
    } finally {
      setIsSaving(false);
    }
  }, [timeline]);

  const removeEvent = useCallback(async (position: number) => {
    if (!timeline) return;

    setIsSaving(true);
    try {
      const updated = await removeEventFromTimeline(timeline.id, position);
      setTimeline(updated);
    } catch {
      setError('Failed to remove event');
    } finally {
      setIsSaving(false);
    }
  }, [timeline]);

  const reorderEvents = useCallback(async (eventIds: string[]) => {
    if (!timeline) return;

    setIsSaving(true);
    try {
      const updated = await reorderTimelineEvents(timeline.id, eventIds);
      setTimeline(updated);
    } catch {
      setError('Failed to reorder events');
    } finally {
      setIsSaving(false);
    }
  }, [timeline]);

  return {
    timeline,
    isLoading,
    isSaving,
    error,
    update,
    addEvent,
    removeEvent,
    reorderEvents,
    refresh: loadTimeline,
  };
}
