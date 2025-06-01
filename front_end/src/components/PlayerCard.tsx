import { useEffect, useState } from "react";
import type { Socket } from "socket.io-client";
import { type User } from "../types/User";
import "../styles/PlayerCard.scss";

const PlayerCard = ({ socket }: { socket: Socket }) => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    socket.on("player_data", (data) => {
      console.log(data);
      setUsers(data);
    });

    return () => {
      socket.off("player_data");
    };
  }, [socket]);

  return (
    <div>
      {users.map((user) => (
        <div key={user.username} className="player-card">
          <div className="player-name">{user.username} </div>
          <div className="player-points">{user.points}</div>
        </div>
      ))}
    </div>
  );
};

export default PlayerCard;
