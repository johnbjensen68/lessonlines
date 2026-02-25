import { Timeline } from '../../types';
import { COLOR_SCHEMES } from '../../utils/constants';
import TimelineLine from './TimelineLine';
import PublicTimelineEvent from './PublicTimelineEvent';
import PublicTimelineEventMobile from './PublicTimelineEventMobile';

interface PublicTimelineCanvasProps {
  timeline: Timeline;
}

export default function PublicTimelineCanvas({ timeline }: PublicTimelineCanvasProps) {
  const colorScheme = COLOR_SCHEMES[timeline.color_scheme as keyof typeof COLOR_SCHEMES] || COLOR_SCHEMES.blue_green;

  const sortedEvents = [...timeline.events].sort((a, b) => {
    const dateA = a.custom_date_start ?? a.event?.date_start ?? '';
    const dateB = b.custom_date_start ?? b.event?.date_start ?? '';
    return dateA < dateB ? -1 : dateA > dateB ? 1 : a.position - b.position;
  });

  return (
    <div className="flex-1 p-4 md:p-6 overflow-auto">
      <h1 className="text-2xl md:text-3xl font-semibold text-slate-800 mb-1">{timeline.title}</h1>
      {timeline.subtitle && (
        <p className="text-sm text-slate-500 mb-6 md:mb-8">{timeline.subtitle}</p>
      )}

      <div className="bg-slate-800 rounded-xl shadow-sm overflow-hidden">
        {sortedEvents.length === 0 ? (
          <div className="flex items-center justify-center h-48 text-slate-400 text-sm">
            No events on this timeline yet.
          </div>
        ) : (
          <>
            {/* Desktop: horizontal scrolling layout */}
            <div className="hidden md:block overflow-x-auto p-6">
              <div className="relative">
                <TimelineLine gradient={colorScheme.gradient} />
                <div className="flex gap-3 items-end px-2">
                  {sortedEvents.map((event, index) => (
                    <PublicTimelineEvent
                      key={event.id}
                      event={event}
                      index={index}
                      colorPrimary={colorScheme.primary}
                      colorSecondary={colorScheme.secondary}
                      axisColor={colorScheme.secondary}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Mobile: vertical stacked layout */}
            <div className="md:hidden p-4 pb-6">
              <div className="relative pl-8">
                {/* Vertical gradient line */}
                <div
                  className="absolute left-3 top-0 bottom-0 w-0.5"
                  style={{ background: colorScheme.gradient }}
                />
                <div className="flex flex-col gap-4">
                  {sortedEvents.map((event, index) => (
                    <PublicTimelineEventMobile
                      key={event.id}
                      event={event}
                      index={index}
                      colorPrimary={colorScheme.primary}
                      colorSecondary={colorScheme.secondary}
                    />
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
