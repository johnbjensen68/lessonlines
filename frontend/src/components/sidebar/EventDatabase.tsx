import { useEvents } from '../../hooks/useEvents';
import SearchInput from './SearchInput';
import TopicTabs from './TopicTabs';
import EventList from './EventList';
import { EventListItem } from '../../types';

interface EventDatabaseProps {
  onAddEvent?: (event: EventListItem) => void;
}

export default function EventDatabase({ onAddEvent }: EventDatabaseProps) {
  const {
    events,
    topics,
    selectedTopic,
    searchQuery,
    isLoading,
    selectTopic,
    search,
  } = useEvents();

  return (
    <aside className="w-80 bg-white border-r border-slate-200 flex flex-col h-full">
      <div className="p-4 border-b border-slate-200">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
          Event Database
        </h2>
        <SearchInput value={searchQuery} onChange={search} />
        <div className="mt-3">
          <TopicTabs
            topics={topics}
            selectedTopic={selectedTopic}
            onSelect={selectTopic}
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3">
        <EventList events={events} isLoading={isLoading} onAddEvent={onAddEvent} />
      </div>
    </aside>
  );
}
