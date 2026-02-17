import { useParams, useNavigate } from 'react-router-dom';
import {
  DndContext,
  DragEndEvent,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { arrayMove } from '@dnd-kit/sortable';
import { Header } from '../components/layout';
import { Toolbar } from '../components/toolbar';
import { EventDatabase } from '../components/sidebar';
import { TimelineCanvas } from '../components/timeline';
import { useTimeline } from '../hooks/useTimeline';
import { useAuth } from '../context/AuthContext';
import { exportTimelinePdf } from '../api/timelines';
import { EventListItem } from '../types';

export default function Editor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const {
    timeline,
    isLoading,
    isSaving,
    error,
    update,
    addEvent,
    removeEvent,
    reorderEvents,
  } = useTimeline(id!);

  const handleExport = async (): Promise<string | null> => {
    if (!timeline) return null;
    try {
      const blob = await exportTimelinePdf(timeline.id);
      const url = URL.createObjectURL(blob);
      return url;
    } catch (err) {
      console.error('Export failed:', err);
      return null;
    }
  };

  const handleAddEvent = async (event: EventListItem) => {
    await addEvent({ event_id: event.id });
  };

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || !timeline) return;

    const oldIndex = timeline.events.findIndex((e) => e.id === active.id);
    const newIndex = timeline.events.findIndex((e) => e.id === over.id);

    if (oldIndex !== -1 && newIndex !== -1 && oldIndex !== newIndex) {
      const reorderedEvents = arrayMove(timeline.events, oldIndex, newIndex);
      await reorderEvents(reorderedEvents.map((e) => e.id));
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error || !timeline) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || 'Timeline not found'}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-primary-500 hover:underline"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-100">
      <Header />
      <Toolbar
        colorScheme={timeline.color_scheme}
        layout={timeline.layout}
        isPro={user?.is_pro || false}
        onColorChange={(color_scheme) => update({ color_scheme })}
        onLayoutChange={(layout) => update({ layout })}
        onExport={handleExport}
      />
      <div className="flex items-center gap-2 px-4 py-1 bg-slate-50 border-b border-slate-200">
        {isSaving && (
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
            Saving...
          </span>
        )}
        {!isSaving && (
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <span className="w-2 h-2 bg-green-400 rounded-full"></span>
            Saved
          </span>
        )}
      </div>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <div className="flex flex-1 overflow-hidden">
          <EventDatabase onAddEvent={handleAddEvent} />
          <TimelineCanvas
            timeline={timeline}
            onTitleChange={(title) => update({ title })}
            onSubtitleChange={(subtitle) => update({ subtitle })}
            onRemoveEvent={removeEvent}
          />
        </div>
      </DndContext>
    </div>
  );
}
