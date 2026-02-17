import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { TimelineEvent as TimelineEventType } from '../../types';

interface TimelineEventProps {
  event: TimelineEventType;
  index: number;
  colorPrimary: string;
  onRemove: () => void;
}

export default function TimelineEvent({
  event,
  colorPrimary,
  onRemove,
}: TimelineEventProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: event.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const title = event.custom_title || event.event?.title || 'Custom Event';
  const dateDisplay = event.custom_date_display || event.event?.date_display || '';

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex flex-col items-center shrink-0 ${isDragging ? 'opacity-50' : ''}`}
    >
      {/* Event card */}
      <div
        className="bg-white rounded-lg shadow-md w-[180px] p-3 relative group cursor-grab active:cursor-grabbing"
        style={{ borderTop: `3px solid ${colorPrimary}` }}
        {...attributes}
        {...listeners}
      >
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
        >
          x
        </button>
        <div className="text-sm font-semibold text-slate-800 leading-tight">{title}</div>
        <div className="text-xs mt-1" style={{ color: colorPrimary }}>{dateDisplay}</div>
      </div>

      {/* Connector line */}
      <div className="w-px h-8 bg-slate-300"></div>

      {/* Dot on axis */}
      <div
        className="w-3 h-3 rounded-full border-2 border-white shadow-sm z-10 shrink-0"
        style={{ backgroundColor: colorPrimary }}
      ></div>
    </div>
  );
}
