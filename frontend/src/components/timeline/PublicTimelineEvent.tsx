import { useState } from 'react';
import { TimelineEvent } from '../../types';
import EventDetailModal from './EventDetailModal';

interface PublicTimelineEventProps {
  event: TimelineEvent;
  index: number;
  colorPrimary: string;
  colorSecondary: string;
  axisColor: string;
}

export default function PublicTimelineEvent({
  event,
  index,
  colorPrimary,
  colorSecondary,
  axisColor,
}: PublicTimelineEventProps) {
  const [modalOpen, setModalOpen] = useState(false);

  const title = event.custom_title || event.event?.title || 'Custom Event';
  const dateDisplay = event.custom_date_display || event.event?.date_display || '';
  const imageUrl = event.event?.image_url || null;
  const description = event.event?.description || null;

  const cardColor = index % 2 === 0 ? colorPrimary : colorSecondary;
  const level = index % 3;
  const connectorHeight = level === 0 ? 'h-24' : level === 1 ? 'h-12' : 'h-40';

  return (
    <div className="flex flex-col items-center shrink-0">
      <div
        className="rounded w-[170px] px-3 py-2.5 relative cursor-pointer shadow-lg"
        style={{ backgroundColor: cardColor }}
        onClick={() => setModalOpen(true)}
      >
        {imageUrl && (
          <img src={imageUrl} alt={title} className="w-full h-20 object-cover rounded-sm mb-1.5" />
        )}
        <div className="text-sm font-bold text-white leading-tight">{title}</div>
        <div className="text-xs mt-1 text-white/80">{dateDisplay}</div>
        {description && (
          <div className="text-xs mt-1.5 text-white/70 leading-snug line-clamp-3">{description}</div>
        )}
      </div>

      <div className={`w-0.5 ${connectorHeight}`} style={{ backgroundColor: cardColor }} />
      <div
        className="w-3.5 h-3.5 rounded-full z-10 shrink-0 border-2"
        style={{ backgroundColor: axisColor, borderColor: axisColor }}
      />
      <div className="w-px h-2" style={{ backgroundColor: axisColor }} />
      <div className="mt-0.5 text-center w-[170px]">
        <span className="text-[11px] font-medium text-slate-300">{dateDisplay}</span>
      </div>

      {modalOpen && <EventDetailModal event={event} onClose={() => setModalOpen(false)} />}
    </div>
  );
}
