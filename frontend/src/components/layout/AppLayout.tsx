import { ReactNode } from 'react';
import Header from './Header';

interface AppLayoutProps {
  children: ReactNode;
  showNewTimeline?: boolean;
  onNewTimeline?: () => void;
}

export default function AppLayout({ children, showNewTimeline, onNewTimeline }: AppLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header showNewTimeline={showNewTimeline} onNewTimeline={onNewTimeline} />
      <main className="flex-1">{children}</main>
    </div>
  );
}
