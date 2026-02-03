import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common';

export default function Landing() {
  const { token } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900">
      <header className="px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-500 rounded-md flex items-center justify-center">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <line x1="3" y1="12" x2="21" y2="12" />
              <circle cx="6" cy="12" r="2" />
              <circle cx="12" cy="12" r="2" />
              <circle cx="18" cy="12" r="2" />
            </svg>
          </div>
          <span className="text-xl font-semibold text-white">LessonLines</span>
        </div>
        <div className="flex gap-3">
          {token ? (
            <Link to="/dashboard">
              <Button>Go to Dashboard</Button>
            </Link>
          ) : (
            <>
              <Link to="/login">
                <Button variant="secondary">Sign In</Button>
              </Link>
              <Link to="/register">
                <Button>Get Started</Button>
              </Link>
            </>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl font-bold text-white mb-6">
          Create Historical Timelines
          <br />
          <span className="text-primary-400">For Your Classroom</span>
        </h1>
        <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
          LessonLines helps K-12 teachers build engaging historical timelines aligned with
          curriculum standards. Drag and drop from our curated event database.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/register">
            <Button size="lg">Start Building Free</Button>
          </Link>
        </div>

        <div className="mt-20 grid grid-cols-3 gap-8 text-left">
          <div className="bg-slate-800/50 p-6 rounded-xl">
            <div className="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Curated Events</h3>
            <p className="text-slate-400">
              Browse hundreds of historical events aligned to Common Core, AP, and state standards.
            </p>
          </div>
          <div className="bg-slate-800/50 p-6 rounded-xl">
            <div className="w-12 h-12 bg-secondary-500/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Drag & Drop</h3>
            <p className="text-slate-400">
              Simply drag events onto your timeline. Reorder and customize with ease.
            </p>
          </div>
          <div className="bg-slate-800/50 p-6 rounded-xl">
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Export to PDF</h3>
            <p className="text-slate-400">
              Download beautiful PDF handouts for your students with one click.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
