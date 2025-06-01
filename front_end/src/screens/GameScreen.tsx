import type { Socket } from "socket.io-client";
import Map from "../components/Map";
import { useLocation, useParams } from "react-router-dom";
import { useEffect } from "react";
import HomeButton from "../components/HomeButton";
import PlayerCard from "../components/PlayerCard";

const GameScreen = ({ socket }: { socket: Socket }) => {
  const { roomID } = useParams();
  const location = useLocation();

  const username = location.state?.username || null;

  useEffect(() => {
    socket.emit("join-room", { roomID, username });

    return () => {
      socket.off("room-users");
    };
  }, []);

  return (
    <>
      <div
        style={{
          justifyContent: "left",
          height: "0px",
        }}
      >
        <HomeButton />
        <h2>Room {roomID}</h2>
      </div>
      <div style={{ position: "absolute", left: 0, top: "50%" }}>
        <ul>
          <PlayerCard socket={socket} />
        </ul>
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Map socket={socket} />
      </div>
    </>
  );
};

export default GameScreen;
