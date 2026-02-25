import { useParams } from 'react-router-dom';
import PublicViewHeader from '../components/layout/PublicViewHeader';
import PublicTimelineCanvas from '../components/timeline/PublicTimelineCanvas';
import { usePublicTimeline } from '../hooks/usePublicTimeline';

export default function PublicTimeline() {
  const { id } = useParams<{ id: string }>();
  const { timeline, isLoading, error } = usePublicTimeline(id!);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error || !timeline) {
    return (
      <div className="min-h-screen flex flex-col bg-slate-100">
        <PublicViewHeader />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center px-4">
            <p className="text-slate-500 mb-4">
              This timeline is not available. It may have been unpublished or the link is invalid.
            </p>
            <a href="/" className="text-primary-500 hover:underline text-sm">
              Go to LessonLines
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-100">
      <PublicViewHeader />
      <PublicTimelineCanvas timeline={timeline} />
    </div>
  );
}
