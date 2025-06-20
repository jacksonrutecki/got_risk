import type { Socket } from "socket.io-client";
import Map from "../components/Map";
import { useLocation, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import HomeButton from "../components/HomeButton";
import PlayerCard from "../components/PlayerCard";

const GameScreen = ({ socket }: { socket: Socket }) => {
  const { roomID } = useParams();
  const location = useLocation();

  const [curPhase, setCurPhase] = useState("");
  const [curTurn, setCurTurn] = useState("");

  const username = location.state?.username || null;

  useEffect(() => {
    socket.emit("join-room", { roomID, username });
    socket.emit("start-game");
    socket.emit("get_current_phase");
    socket.emit("get_current_turn");

    const handlePhase = (data: string) => setCurPhase(data);
    socket.on("current_phase", handlePhase);

    const handleTurn = (data: string) => setCurTurn(data);
    socket.on("current_turn", handleTurn);

    return () => {
      socket.off("current_phase", handlePhase);
      socket.off("current_turn", handleTurn);
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
        {curPhase}
        <br />
        {curTurn}
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
