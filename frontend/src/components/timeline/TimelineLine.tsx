interface TimelineLineProps {
  gradient: string;
}

export default function TimelineLine({ gradient }: TimelineLineProps) {
  return (
    <div
      className="absolute bottom-0 left-0 right-0 h-1 rounded-full"
      style={{ background: gradient }}
    ></div>
  );
}
