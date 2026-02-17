interface TimelineLineProps {
  gradient: string;
}

export default function TimelineLine({ gradient }: TimelineLineProps) {
  return (
    <div
      className="absolute left-0 right-0 h-0.5"
      style={{
        background: gradient,
        bottom: '37px',
      }}
    ></div>
  );
}
