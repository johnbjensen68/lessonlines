import { Topic } from '../../types';

interface TopicTabsProps {
  topics: Topic[];
  selectedTopic: string | null;
  onSelect: (topicSlug: string | null) => void;
}

export default function TopicTabs({ topics, selectedTopic, onSelect }: TopicTabsProps) {
  return (
    <select
      value={selectedTopic ?? ''}
      onChange={(e) => onSelect(e.target.value || null)}
      className="w-full px-3 py-1.5 rounded border border-slate-200 text-xs text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
    >
      <option value="">All Topics</option>
      {topics.map((topic) => (
        <option key={topic.id} value={topic.slug}>
          {topic.name}
        </option>
      ))}
    </select>
  );
}
