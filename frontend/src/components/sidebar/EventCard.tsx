import { EventListItem } from '../../types';

interface EventCardProps {
  event: EventListItem;
  onAdd?: () => void;
}

export default function EventCard({ event, onAdd }: EventCardProps) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 transition-all hover:border-primary-300 hover:shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold text-primary-500 mb-1">{event.date_display}</div>
          <div className="text-sm font-medium text-slate-800 mb-1">{event.title}</div>
          <div className="text-xs text-slate-500 line-clamp-2">{event.description}</div>
        </div>
        {onAdd && (
          <button
            onClick={onAdd}
            className="shrink-0 w-7 h-7 flex items-center justify-center rounded-full bg-primary-500 text-white hover:bg-primary-600 transition-colors"
            title="Add to timeline"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
