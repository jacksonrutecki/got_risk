import { useEffect, useRef, useState } from "react";
import { POSITION_NONE, ReactSVGPanZoom, TOOL_AUTO } from "react-svg-pan-zoom";
import type { Value, Tool } from "react-svg-pan-zoom";
import { Socket } from "socket.io-client";
import "../styles/Map.scss";
import type { TerrInfo } from "../types/TerrInfo";

const Map = ({ socket }: { socket: Socket }) => {
  // using the list of files, get the layer paths inside of them
  const [paths, setPaths] = useState<{ id: string; d: string }[]>([]);
  const [tool, setTool] = useState<Tool>(TOOL_AUTO);
  const [value, setValue] = useState<Value | null>(null);
  const [viewerHeight, setViewerHeight] = useState(window.innerHeight);

  const [armyPositions, setArmyPositions] = useState<
    Record<string, { x: number; y: number }>
  >({});
  const [armyCounts, setArmyCounts] = useState<Record<string, TerrInfo>>({});
  const [armyUpdateTrigger, setArmyUpdateTrigger] = useState(0);

  const refreshArmies = () => {
    setArmyUpdateTrigger((prev) => prev + 1);
  };

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

  useEffect(() => {
    const handleUpdate = () => {
      refreshArmies();
    };

    socket.on("armies_updated", handleUpdate);

    return () => {
      socket.off("armies_updated", handleUpdate);
    };
  });

  const getArmies = (territory: string): Promise<TerrInfo> => {
    return new Promise((resolve) => {
      socket.emit("get_armies", { territory: territory });

      socket.once("num_armies", (data: TerrInfo) => {
        resolve(data);
      });
    });
  };

  useEffect(() => {
    const updatePositionsAndCounts = async () => {
      const newPositions: Record<string, { x: number; y: number }> = {};
      const newInfo: Record<string, TerrInfo> = {};

      for (const { id } of paths) {
        const pathEl = pathRefs.current[id];
        if (pathEl) {
          const bbox = pathEl.getBBox();
          const centerX = bbox.x + bbox.width / 2;
          const centerY = bbox.y + bbox.height / 2;
          newPositions[id] = { x: centerX, y: centerY };

          const ti = await getArmies(id.replace(".txt", ""));
          newInfo[id] = ti;
        }
      }

      setArmyPositions(newPositions);
      setArmyCounts(newInfo);
    };

    updatePositionsAndCounts();
  }, [paths, armyUpdateTrigger]);

  // when a layer is clicked, print out its name to the console (temporary function)
  const handleGroupClick = (event: React.MouseEvent) => {
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
                fillOpacity: armyCounts[id]
                  ? armyCounts[id].is_ter_from || armyCounts[id].is_ter_to
                    ? 0.25
                    : 0
                  : 0,
                fill: armyCounts[id] ? armyCounts[id].color : "transparent",
                strokeOpacity: "0",
                cursor: "pointer",
                stroke: armyCounts[id] ? armyCounts[id].color : "transparent",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.strokeOpacity = "1";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.strokeOpacity = "0";
              }}
            />
          </g>
        ))}

        {Object.entries(armyPositions).map(([id, pos]) => (
          <g key={`army-${id}`}>
            <circle
              cx={pos.x}
              cy={pos.y}
              r={12}
              fillOpacity={0.25}
              fill={armyCounts[id].color}
              stroke="black"
              strokeWidth={1}
            />
            <text
              x={pos.x}
              y={pos.y}
              textAnchor="middle"
              alignmentBaseline="middle"
              fontSize="12"
              fill="white"
            >
              {armyCounts[id].num_armies ?? 0}
            </text>
          </g>
        ))}
      </svg>
    </ReactSVGPanZoom>
  );
};

export default Map;
