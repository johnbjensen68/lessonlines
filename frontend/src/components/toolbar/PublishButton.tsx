import { useState, useEffect, useRef } from 'react';

interface PublishButtonProps {
  isPublic: boolean;
  timelineId: string;
  onToggle: () => void;
  isToggling: boolean;
}

export default function PublishButton({ isPublic, timelineId, onToggle, isToggling }: PublishButtonProps) {
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const publicUrl = `${window.location.origin}/t/${timelineId}`;

  useEffect(() => {
    if (!popoverOpen) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setPopoverOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [popoverOpen]);

  const handleCopy = () => {
    const succeed = () => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    };

    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(publicUrl).then(succeed).catch(() => fallbackCopy());
    } else {
      fallbackCopy();
    }
  };

  const fallbackCopy = () => {
    const el = document.createElement('textarea');
    el.value = publicUrl;
    el.style.position = 'fixed';
    el.style.opacity = '0';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleButtonClick = () => {
    if (isPublic) {
      setPopoverOpen((o) => !o);
    } else {
      onToggle();
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={handleButtonClick}
        disabled={isToggling}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50 ${
          isPublic
            ? 'bg-green-500 hover:bg-green-600 text-white'
            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
        }`}
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <circle cx="12" cy="12" r="10" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20" />
        </svg>
        {isPublic ? 'Published' : 'Publish'}
      </button>

      {isPublic && popoverOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 p-4 z-50">
          <p className="text-sm font-medium text-slate-700 mb-2">Share this timeline</p>
          <div className="flex items-center gap-2 bg-slate-50 rounded-lg px-3 py-2 mb-3">
            <span className="text-xs text-slate-600 truncate flex-1">{publicUrl}</span>
            <button
              onClick={handleCopy}
              className="text-xs text-primary-500 font-medium shrink-0 hover:text-primary-600 transition-colors"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <button
            onClick={() => { onToggle(); setPopoverOpen(false); }}
            className="text-xs text-slate-400 hover:text-red-500 transition-colors"
          >
            Unpublish
          </button>
        </div>
      )}
    </div>
  );
}
