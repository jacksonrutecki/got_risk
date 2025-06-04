import { useEffect, useState } from "react";
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
              d={d}
              style={{
                fillOpacity: 0,
                cursor: "pointer",
              }}
            />
          </g>
        ))}
      </svg>
    </ReactSVGPanZoom>
  );
};

export default Map;
