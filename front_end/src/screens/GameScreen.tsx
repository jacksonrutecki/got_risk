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
  const [canNextMove, setCanNextMove] = useState(false);

  const username = location.state?.username || null;

  const handleClearBoard = () => {
    socket.emit("clear_board");
  };

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

    const handleCanNextMove = (data: boolean) => setCanNextMove(data);
    socket.on("can_next_move", handleCanNextMove);

    return () => {
      socket.off("current_phase", handlePhase);
      socket.off("current_turn", handleTurn);
      socket.off("can_execute_move", handleCanExecuteMove);
      socket.off("can_next_move", handleCanNextMove);
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
          position: "relative",
        }}
      >
        <Map socket={socket} />

        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <div
            style={{
              backgroundColor: "white",
              padding: "20px",
              borderRadius: "8px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              flex: 0.35,
            }}
          >
            <label style={{ marginBottom: "10px" }}>
              Number of armies to move:
              <input
                type="number"
                style={{ marginLeft: "10px", width: "60px" }}
              />
            </label>
          </div>
        </div>
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
            onClick={handleClearBoard}
          >
            Clear Board
          </button>
          <button
            disabled={!canExecuteMove}
            className="base-button"
            onClick={handleExecuteMove}
          >
            Execute Move
          </button>
          <button
            disabled={!canNextMove}
            className="base-button"
            onClick={handleNextMove}
          >
            Next Move
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameScreen;
