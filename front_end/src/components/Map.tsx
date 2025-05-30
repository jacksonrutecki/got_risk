import { useEffect, useState } from "react";

const Map = () => {
  // using the list of files, get the layer paths inside of them
  const [paths, setPaths] = useState<{ id: string; d: string }[]>([]);

  useEffect(() => {
    fetch("http://localhost:5000/list-files?directory=back_end/paths")
      .then((response) => response.json())
      .then((data) => {
        setPaths(data);
      });
  }, []);

  // when a layer is clicked, print out its name to the console (temporary function)
  const handleGroupClick = (event: React.MouseEvent) => {
    console.log(event.currentTarget.id.replace(".txt", ""));
  };

  // the image width and height as denoted by the .svg itself -
  // there might be a better way to abstract this out, leaving it hardcoded for now
  const IMG_WIDTH = "720";
  const IMG_HEIGHT = "1071";

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={`0 0 ${IMG_WIDTH} ${IMG_HEIGHT}`}
      width={IMG_WIDTH}
      height={IMG_HEIGHT}
    >
      <image
        href="test.svg"
        x="0"
        y="0"
        width={IMG_WIDTH}
        height={IMG_HEIGHT}
      />

      {paths.map(({ id, d }) => (
        <g key={id} id={id} onClick={handleGroupClick}>
          <path
            d={d}
            style={{
              fillOpacity: 0,
            }}
          />
        </g>
      ))}
    </svg>
  );
};

export default Map;
