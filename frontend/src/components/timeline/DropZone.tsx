import { useDroppable } from '@dnd-kit/core';

interface DropZoneProps {
  isOver?: boolean;
}

export default function DropZone({ isOver }: DropZoneProps) {
  const { setNodeRef } = useDroppable({
    id: 'timeline-drop-zone',
  });

  return (
    <div
      ref={setNodeRef}
      className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${
        isOver
          ? 'border-primary-400 bg-primary-50'
          : 'border-slate-300 text-slate-400'
      }`}
    >
      <div className="text-3xl mb-2">
        <svg className="w-8 h-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </div>
      <div className="text-sm">Drag events here to add them to your timeline</div>
    </div>
  );
}
