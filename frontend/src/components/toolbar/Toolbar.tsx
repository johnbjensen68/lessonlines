import ColorPicker from './ColorPicker';
import LayoutToggle from './LayoutToggle';
import ExportButton from './ExportButton';

interface ToolbarProps {
  colorScheme: string;
  layout: string;
  isPro: boolean;
  onColorChange: (colorScheme: string) => void;
  onLayoutChange: (layout: string) => void;
  onExport: () => Promise<string | null>;
}

export default function Toolbar({
  colorScheme,
  layout,
  isPro,
  onColorChange,
  onLayoutChange,
  onExport,
}: ToolbarProps) {
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-slate-200">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-500 uppercase">Color</span>
          <ColorPicker value={colorScheme} onChange={onColorChange} />
        </div>
        <div className="w-px h-6 bg-slate-200" />
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-500 uppercase">Layout</span>
          <LayoutToggle value={layout} onChange={onLayoutChange} />
        </div>
      </div>
      <div className="flex items-center gap-3">
        <ExportButton isPro={isPro} onExport={onExport} />
      </div>
    </div>
  );
}
