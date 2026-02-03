interface TimelineLineProps {
  gradient: string;
}

export default function TimelineLine({ gradient }: TimelineLineProps) {
  const isGradient = gradient.includes('linear-gradient');

  return (
    <div
      className="absolute top-1/2 left-0 right-0 h-1 rounded-full -translate-y-1/2"
      style={{
        background: isGradient ? gradient : gradient,
      }}
    ></div>
  );
}
