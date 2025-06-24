import { useEffect, useState } from "react";
import type { Socket } from "socket.io-client";
import { type User } from "../types/User";
import "../styles/PlayerCard.scss";

const PlayerCard = ({ socket }: { socket: Socket }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [currentPlayer, setCurrentPlayer] = useState(String);

  useEffect(() => {
    socket.emit("get_current_turn");

    socket.on("current_turn", (data) => {
      setCurrentPlayer(data);
    });

    socket.on("player_data", (data) => {
      setUsers(data);
    });

    return () => {
      socket.off("player_data");
    };
  }, [socket]);

  return (
    <div>
      {users.map((user) => (
        <div
          style={{
            background: user.color,
            opacity: currentPlayer == user.username ? 1 : 0.25,
          }}
          key={user.username}
          className="player-card"
        >
          <div className="player-name">{user.username} </div>
          <div className="player-points">{user.points}</div>
        </div>
      ))}
    </div>
  );
};

export default PlayerCard;
