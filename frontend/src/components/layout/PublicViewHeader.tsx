import { Link } from 'react-router-dom';

export default function PublicViewHeader() {
  return (
    <header className="bg-slate-800 text-white px-6 py-3 flex justify-between items-center shrink-0">
      <Link to="/" className="flex items-center gap-2">
        <div className="w-7 h-7 bg-primary-500 rounded-md flex items-center justify-center">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12" />
            <circle cx="6" cy="12" r="2" />
            <circle cx="12" cy="12" r="2" />
            <circle cx="18" cy="12" r="2" />
          </svg>
        </div>
        <span className="text-lg font-semibold">LessonLines</span>
      </Link>
      <span className="text-sm text-slate-400 italic">View only</span>
    </header>
  );
}
