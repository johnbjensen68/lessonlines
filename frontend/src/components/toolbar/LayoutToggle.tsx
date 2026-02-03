interface LayoutToggleProps {
  value: string;
  onChange: (layout: string) => void;
}

export default function LayoutToggle({ value, onChange }: LayoutToggleProps) {
  return (
    <div className="flex items-center bg-slate-100 rounded-md p-0.5">
      <button
        onClick={() => onChange('horizontal')}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded transition-colors ${
          value === 'horizontal'
            ? 'bg-white text-slate-800 shadow-sm'
            : 'text-slate-500 hover:text-slate-700'
        }`}
        title="Horizontal layout"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 12h16M8 8l-4 4 4 4M16 8l4 4-4 4"
          />
        </svg>
        <span className="hidden sm:inline">Horizontal</span>
      </button>
      <button
        onClick={() => onChange('vertical')}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded transition-colors ${
          value === 'vertical'
            ? 'bg-white text-slate-800 shadow-sm'
            : 'text-slate-500 hover:text-slate-700'
        }`}
        title="Vertical layout"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 4v16M8 8l4-4 4 4M8 16l4 4 4-4"
          />
        </svg>
        <span className="hidden sm:inline">Vertical</span>
      </button>
    </div>
  );
}
