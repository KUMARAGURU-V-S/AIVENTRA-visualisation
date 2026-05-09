import { useState, useMemo } from 'react';
import EvidenceBoard from './components/EvidenceBoard';
import ChronoScrubber from './components/ChronoScrubber';
import DossierPanel from './components/DossierPanel';
import { mockData } from './mockData';
import './App.css';

function App() {
  const [currentTime, setCurrentTime] = useState<number>(
    new Date('2026-10-24T20:00:00Z').getTime()
  );
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedConnectionId, setSelectedConnectionId] = useState<string | null>(null);

  const startTime = useMemo(() => new Date('2026-10-24T20:00:00Z').getTime(), []);
  const endTime = useMemo(() => new Date('2026-10-25T04:00:00Z').getTime(), []);

  const filteredEntities = useMemo(() => {
    return mockData.entities.filter(
      (e) => new Date(e.timestamp).getTime() <= currentTime
    );
  }, [currentTime]);

  const filteredConnections = useMemo(() => {
    return mockData.connections.filter(
      (c) => new Date(c.timestamp).getTime() <= currentTime
    );
  }, [currentTime]);

  const selectedEntity = useMemo(() => {
    return mockData.entities.find((e) => e.id === selectedEntityId) || null;
  }, [selectedEntityId]);

  const selectedConnection = useMemo(() => {
    return mockData.connections.find((c) => c.id === selectedConnectionId) || null;
  }, [selectedConnectionId]);

  const changeTimestamps = useMemo(() => {
    const entityTimes = mockData.entities.map((e) => new Date(e.timestamp).getTime());
    const connectionTimes = mockData.connections.map((c) => new Date(c.timestamp).getTime());
    return Array.from(new Set([...entityTimes, ...connectionTimes])).sort((a, b) => a - b);
  }, []);

  const formatTime = (time: number) => {
    return new Date(time).toLocaleString();
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>4D Chronograph</h1>
        <div className="badge">Active Investigation: Midnight Shadow</div>
      </header>

      <main className="main-content">
        <div className="board-section">
          <EvidenceBoard
            entities={filteredEntities}
            connections={filteredConnections}
            onSelectNode={setSelectedEntityId}
            onSelectEdge={setSelectedConnectionId}
          />
        </div>
        <aside className="side-panel">
          <DossierPanel
            selectedEntity={selectedEntity}
            selectedConnection={selectedConnection}
          />
        </aside>
      </main>

      <footer className="app-footer">
        <ChronoScrubber
          min={startTime}
          max={endTime}
          value={currentTime}
          onChange={setCurrentTime}
          formatTime={formatTime}
          marks={changeTimestamps}
        />
      </footer>
    </div>
  );
}

export default App;
