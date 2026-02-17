import EventCard from './EventCard';
import { EventListItem } from '../../types';

interface EventListProps {
  events: EventListItem[];
  isLoading: boolean;
  onAddEvent?: (event: EventListItem) => void;
}

export default function EventList({ events, isLoading, onAddEvent }: EventListProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 text-sm">
        No events found. Try a different search or topic.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {events.map((event) => (
        <EventCard
          key={event.id}
          event={event}
          onAdd={onAddEvent ? () => onAddEvent(event) : undefined}
        />
      ))}
    </div>
  );
}
