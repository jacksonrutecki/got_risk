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

  const [canExecuteMove, setCanExecuteMove] = useState(false);

  const username = location.state?.username || null;

  const handleExecuteMove = () => {
    socket.emit("execute_move");
  };

  const handleNextMove = () => {
    socket.emit("next_move");
  };

  useEffect(() => {
    socket.emit("join-room", { roomID, username });
    socket.emit("start-game");
  }, []);

  useEffect(() => {
    socket.emit("get_current_turn");
    socket.emit("get_current_phase");

    const handlePhase = (data: string) => setCurPhase(data);
    socket.on("current_phase", handlePhase);

    const handleTurn = (data: string) => setCurTurn(data);
    socket.on("current_turn", handleTurn);

    const handleCanExecuteMove = (data: boolean) => setCanExecuteMove(data);
    socket.on("can_execute_move", handleCanExecuteMove);

    return () => {
      socket.off("current_phase", handlePhase);
      socket.off("current_turn", handleTurn);
      socket.off("can_execute_move", handleCanExecuteMove);
    };
  }, [socket]);

  return (
    <div style={{ display: "flex", width: "100%" }}>
      {/* First column */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-start",
          height: "100%",
        }}
      >
        {/* Home button */}
        <div style={{ paddingLeft: "10px", marginBottom: "20px" }}>
          <HomeButton />
        </div>

        {/* Room Info */}
        <div style={{ paddingLeft: "20px", marginBottom: "20px" }}>
          <h2>Room {roomID}</h2>
          {curPhase}
          <br />
          {curTurn}
        </div>

        {/* Player Cards */}
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
          }}
        >
          <PlayerCard socket={socket} />
        </div>
      </div>

      {/* Second column */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Map socket={socket} />
      </div>

      {/* Third column */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            flex: 1,
            display: "flex",
            justifyContent: "center",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <button
            disabled={!canExecuteMove}
            className="base-button"
            onClick={handleExecuteMove}
          >
            Execute Move
          </button>
          <button className="base-button" onClick={handleNextMove}>
            Next Move
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameScreen;
