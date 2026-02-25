import { useEffect } from 'react';
import { TimelineEvent } from '../../types';

interface EventDetailModalProps {
  event: TimelineEvent;
  onClose: () => void;
}

export default function EventDetailModal({ event, onClose }: EventDetailModalProps) {
  const title = event.custom_title || event.event?.title || 'Custom Event';
  const dateDisplay = event.custom_date_display || event.event?.date_display || '';
  const description = event.custom_description || event.event?.description || null;
  const imageUrl = event.event?.image_url || null;
  const location = event.event?.location || null;
  const tags = event.event?.tags || [];

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {imageUrl && (
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-64 object-cover"
          />
        )}
        <div className="p-6">
          <div className="flex items-start justify-between gap-4 mb-1">
            <h2 className="text-xl font-bold text-slate-800 leading-tight">{title}</h2>
            <button
              onClick={onClose}
              className="shrink-0 text-slate-400 hover:text-slate-600 transition-colors text-xl leading-none"
              aria-label="Close"
            >
              ×
            </button>
          </div>

          <div className="text-sm font-medium text-primary-500 mb-1">{dateDisplay}</div>

          {location && (
            <div className="text-sm text-slate-500 mb-3">{location}</div>
          )}

          {description && (
            <p className="text-sm text-slate-700 leading-relaxed mb-4">{description}</p>
          )}

          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {tags.map((tag) => (
                <span
                  key={tag.id}
                  className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-full"
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
