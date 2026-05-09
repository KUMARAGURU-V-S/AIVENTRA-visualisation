import React from 'react';
import { Clock } from 'lucide-react';

interface ChronoScrubberProps {
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
  formatTime: (value: number) => string;
}

const ChronoScrubber: React.FC<ChronoScrubberProps> = ({ min, max, value, onChange, formatTime }) => {
  return (
    <div className="chrono-scrubber">
      <div className="scrubber-header">
        <Clock size={16} />
        <span>Chronological Investigation Timeline</span>
        <span className="current-time">{formatTime(value)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="timeline-slider"
      />
      <div className="scrubber-labels">
        <span>{formatTime(min)}</span>
        <span>{formatTime(max)}</span>
      </div>
    </div>
  );
};

export default ChronoScrubber;
