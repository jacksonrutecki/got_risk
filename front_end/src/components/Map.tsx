import { useEffect, useRef, useState } from "react";
import { POSITION_NONE, ReactSVGPanZoom, TOOL_AUTO } from "react-svg-pan-zoom";
import type { Value, Tool } from "react-svg-pan-zoom";
import { Socket } from "socket.io-client";
import "../styles/Map.scss";

const Map = ({ socket }: { socket: Socket }) => {
  // using the list of files, get the layer paths inside of them
  const [paths, setPaths] = useState<{ id: string; d: string }[]>([]);
  const [tool, setTool] = useState<Tool>(TOOL_AUTO);
  const [value, setValue] = useState<Value | null>(null);
  const [viewerHeight, setViewerHeight] = useState(window.innerHeight);

  const [armyPositions, setArmyPositions] = useState<
    Record<string, { x: number; y: number }>
  >({});
  const [armyCounts, setArmyCounts] = useState<Record<string, number>>({});

  const pathRefs = useRef<Record<string, SVGPathElement | null>>({});

  // load all paths corresponding to each region of the map
  useEffect(() => {
    fetch("http://localhost:5000/app/list-files?directory=back_end/data/paths")
      .then((response) => response.json())
      .then((data) => {
        setPaths(data);
      });
  }, []);

  // automatically resize the image zoom space to the height of the current window
  useEffect(() => {
    const handleResize = () => setViewerHeight(window.innerHeight);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  });

  const getArmies = (territory: string): Promise<number> => {
    return new Promise((resolve) => {
      socket.emit("get_armies", { territory: territory });

      socket.once("num_armies", (count: number) => {
        console.log(count);
        resolve(count);
      });
    });
  };

  useEffect(() => {
    const updatePositionsAndCounts = async () => {
      const newPositions: Record<string, { x: number; y: number }> = {};
      const newCounts: Record<string, number> = {};

      for (const { id } of paths) {
        const pathEl = pathRefs.current[id];
        if (pathEl) {
          const bbox = pathEl.getBBox();
          const centerX = bbox.x + bbox.width / 2;
          const centerY = bbox.y + bbox.height / 2;
          newPositions[id] = { x: centerX, y: centerY };

          const count = await getArmies(id.replace(".txt", ""));
          newCounts[id] = count;
        }
      }

      setArmyPositions(newPositions);
      setArmyCounts(newCounts);
    };

    updatePositionsAndCounts();
  }, [paths]);

  // when a layer is clicked, print out its name to the console (temporary function)
  const handleGroupClick = (event: React.MouseEvent) => {
    console.log(event.currentTarget.id.replace(".txt", ""));
    socket.emit("button_click", {
      territory: event.currentTarget.id.replace(".txt", ""),
    });
  };

  // the image width and height as denoted by the .svg itself -
  // there might be a better way to abstract this out, leaving it hardcoded for now
  const IMG_WIDTH = "720";
  const IMG_HEIGHT = "1071";

  return (
    <ReactSVGPanZoom
      height={viewerHeight}
      width={1000}
      modifierKeys={["Alt", "Shift", "Control"]}
      onChangeTool={setTool}
      onChangeValue={setValue}
      tool={tool}
      value={value}
      detectAutoPan={false}
      toolbarProps={{ position: POSITION_NONE }}
      miniatureProps={{ position: "none", background: "", width: 0, height: 0 }}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox={`0 0 ${IMG_WIDTH} ${IMG_HEIGHT}`}
        width={IMG_WIDTH}
        height={IMG_HEIGHT}
      >
        <image
          href="/test.svg"
          x="0"
          y="0"
          width={IMG_WIDTH}
          height={IMG_HEIGHT}
        />

        {paths.map(({ id, d }) => (
          <g key={id} id={id} onClick={handleGroupClick} className="test">
            <path
              ref={(el) => {
                pathRefs.current[id] = el;
              }}
              d={d}
              style={{
                fillOpacity: 0,
                cursor: "pointer",
              }}
            />
          </g>
        ))}

        {Object.entries(armyPositions).map(([id, pos]) => (
          <g key={`army-${id}`}>
            <circle
              cx={pos.x}
              cy={pos.y}
              r={6}
              fill="red"
              stroke="black"
              strokeWidth={1}
            />
            <text
              x={pos.x}
              y={pos.y}
              textAnchor="middle"
              alignmentBaseline="middle"
              fontSize="10"
              fill="white"
            >
              {armyCounts[id] ?? 0}
            </text>
          </g>
        ))}
      </svg>
    </ReactSVGPanZoom>
  );
};

export default Map;
