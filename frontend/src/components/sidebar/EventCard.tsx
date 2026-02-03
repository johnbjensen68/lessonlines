import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { EventListItem } from '../../types';

interface EventCardProps {
  event: EventListItem;
  isDragging?: boolean;
}

export default function EventCard({ event, isDragging }: EventCardProps) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: `event-${event.id}`,
    data: { event },
  });

  const style = transform
    ? {
        transform: CSS.Translate.toString(transform),
      }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`bg-slate-50 border border-slate-200 rounded-lg p-3 cursor-grab active:cursor-grabbing transition-all ${
        isDragging ? 'opacity-50 border-dashed border-primary-400' : 'hover:border-primary-300 hover:shadow-sm'
      }`}
    >
      <div className="text-xs font-semibold text-primary-500 mb-1">{event.date_display}</div>
      <div className="text-sm font-medium text-slate-800 mb-1">{event.title}</div>
      <div className="text-xs text-slate-500 line-clamp-2">{event.description}</div>
      <div className="flex items-center gap-1 mt-2 text-xs text-slate-400">
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        <span>Drag to timeline</span>
      </div>
    </div>
  );
}
