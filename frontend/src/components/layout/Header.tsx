import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../common';

interface HeaderProps {
  showNewTimeline?: boolean;
  onNewTimeline?: () => void;
}

export default function Header({ showNewTimeline = false, onNewTimeline }: HeaderProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="bg-slate-800 text-white px-6 py-3 flex justify-between items-center">
      <Link to="/dashboard" className="flex items-center gap-2">
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

      <div className="flex items-center gap-3">
        <Link to="/dashboard">
          <Button variant="secondary" size="sm">
            My Timelines
          </Button>
        </Link>
        {showNewTimeline && (
          <Button size="sm" onClick={onNewTimeline}>
            + New Timeline
          </Button>
        )}
        <button
          onClick={handleLogout}
          className="text-slate-400 hover:text-white text-sm ml-2"
        >
          Sign Out
        </button>
      </div>
    </header>
  );
}
