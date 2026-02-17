import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { TimelineEvent as TimelineEventType } from '../../types';

interface TimelineEventProps {
  event: TimelineEventType;
  index: number;
  colorPrimary: string;
  colorSecondary: string;
  axisColor: string;
  onRemove: () => void;
}

export default function TimelineEvent({
  event,
  index,
  colorPrimary,
  colorSecondary,
  axisColor,
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

  // Alternate between primary and secondary colors like the reference
  const cardColor = index % 2 === 0 ? colorPrimary : colorSecondary;

  // Stagger heights: cycle through 3 levels to create the layered look
  const level = index % 3;
  const connectorHeight = level === 0 ? 'h-24' : level === 1 ? 'h-12' : 'h-40';

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex flex-col items-center shrink-0 ${isDragging ? 'opacity-50' : ''}`}
    >
      {/* Event card */}
      <div
        className="rounded w-[170px] px-3 py-2.5 relative group cursor-grab active:cursor-grabbing shadow-lg"
        style={{ backgroundColor: cardColor }}
        {...attributes}
        {...listeners}
      >
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center shadow"
        >
          x
        </button>
        <div className="text-sm font-bold text-white leading-tight">{title}</div>
        <div className="text-xs mt-1 text-white/80">{dateDisplay}</div>
      </div>

      {/* Connector line */}
      <div
        className={`w-0.5 ${connectorHeight}`}
        style={{ backgroundColor: cardColor }}
      ></div>

      {/* Dot on axis */}
      <div
        className="w-3.5 h-3.5 rounded-full z-10 shrink-0 border-2"
        style={{ backgroundColor: axisColor, borderColor: axisColor }}
      ></div>

      {/* Tick mark below dot */}
      <div className="w-px h-2" style={{ backgroundColor: axisColor }}></div>

      {/* Date label on axis */}
      <div className="mt-0.5 text-center w-[170px]">
        <span className="text-[11px] font-medium text-slate-300">{dateDisplay}</span>
      </div>
    </div>
  );
}
