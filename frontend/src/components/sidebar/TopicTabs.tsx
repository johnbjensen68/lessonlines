import { Topic } from '../../types';

interface TopicTabsProps {
  topics: Topic[];
  selectedTopic: string | null;
  onSelect: (topicSlug: string | null) => void;
}

export default function TopicTabs({ topics, selectedTopic, onSelect }: TopicTabsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {topics.map((topic) => (
        <button
          key={topic.id}
          onClick={() => onSelect(topic.slug === selectedTopic ? null : topic.slug)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
            topic.slug === selectedTopic
              ? 'bg-primary-500 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          {topic.name}
        </button>
      ))}
    </div>
  );
}
