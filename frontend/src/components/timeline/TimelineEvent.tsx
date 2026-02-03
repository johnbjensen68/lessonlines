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
  index,
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
  const isAbove = index % 2 === 0;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex flex-col items-center w-40 ${isDragging ? 'opacity-50' : ''}`}
    >
      {isAbove ? (
        <>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center max-w-[160px] relative group">
            <button
              onClick={onRemove}
              className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity"
            >
              x
            </button>
            <div className="text-xs font-semibold mb-1" style={{ color: colorPrimary }}>
              {dateDisplay}
            </div>
            <div className="text-xs font-medium text-slate-800 leading-tight">{title}</div>
          </div>
          <div className="w-0.5 h-10 bg-slate-200"></div>
          <div
            {...attributes}
            {...listeners}
            className="w-4 h-4 rounded-full border-[3px] border-white shadow-md cursor-grab active:cursor-grabbing z-10"
            style={{ backgroundColor: colorPrimary }}
          ></div>
        </>
      ) : (
        <>
          <div
            {...attributes}
            {...listeners}
            className="w-4 h-4 rounded-full border-[3px] border-white shadow-md cursor-grab active:cursor-grabbing z-10"
            style={{ backgroundColor: colorPrimary }}
          ></div>
          <div className="w-0.5 h-10 bg-slate-200"></div>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center max-w-[160px] relative group">
            <button
              onClick={onRemove}
              className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity"
            >
              x
            </button>
            <div className="text-xs font-semibold mb-1" style={{ color: colorPrimary }}>
              {dateDisplay}
            </div>
            <div className="text-xs font-medium text-slate-800 leading-tight">{title}</div>
          </div>
        </>
      )}
    </div>
  );
}
