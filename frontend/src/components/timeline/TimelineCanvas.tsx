import { SortableContext, horizontalListSortingStrategy } from '@dnd-kit/sortable';
import TimelineEvent from './TimelineEvent';
import TimelineLine from './TimelineLine';
import { Timeline } from '../../types';
import { COLOR_SCHEMES } from '../../utils/constants';

interface TimelineCanvasProps {
  timeline: Timeline;
  onTitleChange: (title: string) => void;
  onSubtitleChange: (subtitle: string) => void;
  onRemoveEvent: (position: number) => void;
}

export default function TimelineCanvas({
  timeline,
  onTitleChange,
  onSubtitleChange,
  onRemoveEvent,
}: TimelineCanvasProps) {
  const colorScheme = COLOR_SCHEMES[timeline.color_scheme as keyof typeof COLOR_SCHEMES] || COLOR_SCHEMES.blue_green;
  const sortedEvents = [...timeline.events].sort((a, b) => a.position - b.position);

  return (
    <div className="flex-1 p-6 overflow-auto">
      <input
        type="text"
        value={timeline.title}
        onChange={(e) => onTitleChange(e.target.value)}
        className="text-3xl font-semibold text-slate-800 bg-transparent border-none outline-none w-full mb-2"
        placeholder="Timeline Title"
      />
      <input
        type="text"
        value={timeline.subtitle || ''}
        onChange={(e) => onSubtitleChange(e.target.value)}
        className="text-sm text-slate-500 bg-transparent border-none outline-none w-full mb-8"
        placeholder="Add a subtitle..."
      />

      <div className="bg-slate-800 rounded-xl shadow-sm min-h-[400px] overflow-hidden">
        {sortedEvents.length > 0 ? (
          <div className="overflow-x-auto p-6">
            <div className="relative">
              <TimelineLine gradient={colorScheme.gradient} />
              <SortableContext
                items={sortedEvents.map((e) => e.id)}
                strategy={horizontalListSortingStrategy}
              >
                <div className="flex gap-3 items-end px-2">
                  {sortedEvents.map((event, index) => (
                    <TimelineEvent
                      key={event.id}
                      event={event}
                      index={index}
                      colorPrimary={colorScheme.primary}
                      colorSecondary={colorScheme.secondary}
                      axisColor={colorScheme.secondary}
                      onRemove={() => onRemoveEvent(event.position)}
                    />
                  ))}
                </div>
              </SortableContext>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-48 text-slate-400 text-sm">
            Add events from the sidebar to get started
          </div>
        )}
      </div>
    </div>
  );
}
