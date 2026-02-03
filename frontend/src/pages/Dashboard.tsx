import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AppLayout } from '../components/layout';
import { Button } from '../components/common';
import { getTimelines, createTimeline, deleteTimeline } from '../api/timelines';
import { Timeline } from '../types';

export default function Dashboard() {
  const [timelines, setTimelines] = useState<Timeline[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadTimelines();
  }, []);

  const loadTimelines = async () => {
    try {
      const data = await getTimelines();
      setTimelines(data);
    } catch {
      setError('Failed to load timelines');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewTimeline = async () => {
    try {
      const timeline = await createTimeline({ title: 'Untitled Timeline' });
      navigate(`/timeline/${timeline.id}`);
    } catch {
      setError('Failed to create timeline');
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this timeline?')) return;

    try {
      await deleteTimeline(id);
      setTimelines(timelines.filter((t) => t.id !== id));
    } catch {
      setError('Failed to delete timeline');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <AppLayout showNewTimeline onNewTimeline={handleNewTimeline}>
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-slate-800">My Timelines</h1>
          <Button onClick={handleNewTimeline}>+ New Timeline</Button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          </div>
        ) : timelines.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-slate-800 mb-2">No timelines yet</h3>
            <p className="text-slate-500 mb-6">Create your first timeline to get started</p>
            <Button onClick={handleNewTimeline}>Create Timeline</Button>
          </div>
        ) : (
          <div className="grid gap-4">
            {timelines.map((timeline) => (
              <Link
                key={timeline.id}
                to={`/timeline/${timeline.id}`}
                className="block bg-white rounded-xl border border-slate-200 p-5 hover:border-primary-300 hover:shadow-sm transition-all"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-slate-800 mb-1">{timeline.title}</h3>
                    {timeline.subtitle && (
                      <p className="text-sm text-slate-500 mb-2">{timeline.subtitle}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-slate-400">
                      <span>{timeline.events.length} events</span>
                      <span>Updated {formatDate(timeline.updated_at)}</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDelete(timeline.id, e)}
                    className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
