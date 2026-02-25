import { useState } from 'react';
import { TimelineEvent } from '../../types';
import EventDetailModal from './EventDetailModal';

interface PublicTimelineEventMobileProps {
  event: TimelineEvent;
  index: number;
  colorPrimary: string;
  colorSecondary: string;
}

export default function PublicTimelineEventMobile({
  event,
  index,
  colorPrimary,
  colorSecondary,
}: PublicTimelineEventMobileProps) {
  const [modalOpen, setModalOpen] = useState(false);

  const title = event.custom_title || event.event?.title || 'Custom Event';
  const dateDisplay = event.custom_date_display || event.event?.date_display || '';
  const imageUrl = event.event?.image_url || null;
  const description = event.event?.description || null;

  const cardColor = index % 2 === 0 ? colorPrimary : colorSecondary;

  return (
    <div className="relative flex items-start gap-3">
      {/* Dot on the vertical line */}
      <div
        className="absolute -left-5 top-3 w-3.5 h-3.5 rounded-full border-2 shrink-0 z-10"
        style={{ backgroundColor: cardColor, borderColor: cardColor }}
      />

      {/* Card */}
      <div
        className="flex-1 rounded-lg px-4 py-3 cursor-pointer shadow-md"
        style={{ backgroundColor: cardColor }}
        onClick={() => setModalOpen(true)}
      >
        {imageUrl && (
          <img src={imageUrl} alt={title} className="w-full h-32 object-cover rounded-sm mb-2" />
        )}
        <div className="text-sm font-bold text-white leading-tight">{title}</div>
        <div className="text-xs mt-1 text-white/80">{dateDisplay}</div>
        {description && (
          <div className="text-xs mt-1.5 text-white/70 leading-snug line-clamp-4">{description}</div>
        )}
      </div>

      {modalOpen && <EventDetailModal event={event} onClose={() => setModalOpen(false)} />}
    </div>
  );
}
