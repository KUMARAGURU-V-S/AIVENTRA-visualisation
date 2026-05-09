import { Suspense, useState, useEffect, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Html, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

interface Mark {
  id: string;
  type: string;
  location?: string; // e.g., "Skull", "Left_Femur"
  coordinates?: { x: number; y: number; z: number };
  color: string;
  description: string;
}

interface AutopsyData {
  patient_id: string;
  report_date: string;
  marks: Mark[];
}

const ANATOMY_MAP: Record<string, string> = {
  'skull': 'frontal',
  'head': 'frontal',
  'chest': 'sternum',
  'spine': 'vertebrae',
  'back': 'vertebrae',
  'neck': 'cervical',
  'rib': 'rib',
  'leg': 'femur',
  'arm': 'humerus',
  'hand': 'metacarpal',
  'foot': 'metatarsal'
};

function HumanBody({ marks, onSelect }: { marks: Mark[], onSelect: (mark: Mark) => void }) {
  const { scene } = useGLTF('/skeleton.glb');
  
  // Create a mirrored version for the left side
  const mirroredScene = useMemo(() => {
    const clone = scene.clone();
    clone.scale.set(-1, 1, 1);
    return clone;
  }, [scene]);

  const [resolvedMarks, setResolvedMarks] = useState<(Mark & { worldPos: THREE.Vector3 })[]>([]);
  
  useEffect(() => {
    const newResolved: (Mark & { worldPos: THREE.Vector3 })[] = [];
    
    marks.forEach(mark => {
      if (mark.coordinates) {
        newResolved.push({ ...mark, worldPos: new THREE.Vector3(mark.coordinates.x, mark.coordinates.y, mark.coordinates.z) });
      } else if (mark.location) {
        let targetNode: THREE.Object3D | null = null;
        const searchLoc = mark.location.toLowerCase();
        
        // Try direct match then map match
        const anatomicalTerm = ANATOMY_MAP[searchLoc] || searchLoc;
        
        scene.traverse(node => {
          if (node.name.toLowerCase().includes(anatomicalTerm)) {
            targetNode = node;
          }
        });

        if (targetNode) {
          const node = targetNode as THREE.Object3D;
          // Force world matrix update to get accurate bounding box
          node.updateWorldMatrix(true, true);
          
          const box = new THREE.Box3().setFromObject(node);
          const worldPos = new THREE.Vector3();
          box.getCenter(worldPos);
          
          // If the location specifies "left", we use the mirrored position
          // Assuming the source model is the right side
          if (searchLoc.includes('left')) {
            worldPos.x = -worldPos.x;
          }
          
          newResolved.push({ ...mark, worldPos });
        } else {
          console.warn(`Anatomy location not found in model: ${mark.location} (tried term: ${anatomicalTerm})`);
        }
      }
    });

    setResolvedMarks(newResolved);
  }, [scene, marks]);

  return (
    <group>
      <primitive object={scene} />
      <primitive object={mirroredScene} />
      {resolvedMarks.map((mark) => (
        <Marker key={mark.id} mark={mark} position={mark.worldPos} onSelect={onSelect} />
      ))}
    </group>
  );
}

function Marker({ mark, position, onSelect }: { mark: Mark; position: THREE.Vector3; onSelect: (mark: Mark) => void }) {
  const [hovered, setHovered] = useState(false);

  return (
    <mesh
      position={position}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(mark);
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
    >
      <sphereGeometry args={[0.04, 16, 16]} />
      <meshStandardMaterial 
        color={mark.color} 
        emissive={mark.color} 
        emissiveIntensity={hovered ? 3 : 1} 
        depthTest={false}
        transparent
        opacity={0.9}
      />
      {hovered && (
        <Html distanceFactor={10}>
          <div className="bg-black/80 text-white p-2 rounded text-xs whitespace-nowrap border border-white backdrop-blur-sm shadow-xl">
            <strong>{mark.location || 'Point'}:</strong> {mark.description}
          </div>
        </Html>
      )}
    </mesh>
  );
}

export default function Viewer3D() {
  const [data, setData] = useState<AutopsyData | null>(null);
  const [selectedMark, setSelectedMark] = useState<Mark | null>(null);

  useEffect(() => {
    fetch('/autopsy.json')
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  if (!data) return <div className="flex items-center justify-center h-full text-white">Loading autopsy data...</div>;

  return (
    <div className="relative w-full h-full flex flex-col md:flex-row bg-gray-950">
      <div className="flex-1 relative">
        <Canvas camera={{ position: [0, 2, 5], fov: 45 }} shadows>
          <ambientLight intensity={0.7} />
          <directionalLight position={[5, 5, 5]} intensity={1} castShadow />
          <pointLight position={[-5, 5, -5]} intensity={0.5} />
          
          <Suspense fallback={<Html center className="text-white">Loading Skeleton Model...</Html>}>
            <HumanBody marks={data.marks} onSelect={setSelectedMark} />
          </Suspense>

          <OrbitControls target={[0, 1, 0]} makeDefault />
          <gridHelper args={[20, 20, 0x444444, 0x222222]} />
          <PerspectiveCamera makeDefault position={[0, 2, 5]} />
        </Canvas>

        <div className="absolute top-4 left-4 bg-black/60 text-white p-4 rounded-lg backdrop-blur-md border border-white/20 pointer-events-none">
          <h2 className="text-xl font-bold">Autopsy Report: {data.patient_id}</h2>
          <p className="text-sm opacity-80">Date: {data.report_date}</p>
        </div>
      </div>

      <div className="w-full md:w-80 bg-gray-800 text-white p-6 overflow-y-auto border-l border-gray-700">
        <h3 className="text-lg font-semibold mb-4 border-b border-gray-600 pb-2">Evidence & Marks</h3>
        <div className="space-y-4">
          {data.marks.map((mark) => (
            <div 
              key={mark.id}
              onClick={() => setSelectedMark(mark)}
              className={`p-3 rounded-md cursor-pointer transition-colors ${
                selectedMark?.id === mark.id ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: mark.color }}
                ></span>
                <span className="font-medium uppercase text-xs">{mark.type}</span>
              </div>
              <p className="text-sm">{mark.description}</p>
              <div className="mt-2 text-[10px] text-gray-400">
                {mark.location ? (
                  <span className="bg-gray-600 px-1 rounded text-white">Anatomy: {mark.location}</span>
                ) : (
                  <span>Coords: {mark.coordinates?.x}, {mark.coordinates?.y}, {mark.coordinates?.z}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {selectedMark && (
          <div className="mt-8 p-4 bg-blue-900/40 rounded-lg border border-blue-500/30">
            <h4 className="font-bold text-blue-300 mb-1">Detailed Inspection</h4>
            <p className="text-sm">{selectedMark.description}</p>
          </div>
        )}
      </div>
    </div>
  );
}
