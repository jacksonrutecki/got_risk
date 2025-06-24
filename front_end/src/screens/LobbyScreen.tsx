import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import type { Socket } from "socket.io-client";
import type { User } from "../types/User";
import "../styles/LobbyScreen.scss";
import HomeButton from "../components/HomeButton";

const LobbyScreen = ({ socket }: { socket: Socket }) => {
  const { roomID } = useParams();
  const promptedRef = useRef(false); // flag to prevent double prompting in strict mode
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState(location.state?.username || null);
  const [users, setUsers] = useState<User[]>([]);

  // if a user opens the link directly, prompt the user for their username
  useEffect(() => {
    if (!promptedRef.current && username == null) {
      promptedRef.current = true;
      const enteredUsername = prompt("Please enter your username");
      if (enteredUsername && enteredUsername.trim() != "") {
        setUsername(enteredUsername.trim());
        navigate(`/room/${roomID}`, {
          state: { username: enteredUsername.trim() },
        });
      }
    }
  }, [username, navigate, roomID]);

  // update the list of users
  useEffect(() => {
    if (!username) return;

    socket.emit("join-room", { roomID, username });

    socket.on("player_data", (users) => setUsers(users));
    socket.on("game_started", () =>
      navigate(`/room/${roomID}/game`, { state: { username } })
    );

    return () => {
      socket.off("player_data");
      socket.off("game_started");
    };
  }, [roomID, username]);

  // handle copying the link to the keyboard of the user
  const handleCopyLink = () => {
    const lobbyURL = window.location.href;
    navigator.clipboard
      .writeText(lobbyURL)
      .then(() => {
        alert("Lobby link copied to keyboard!");
      })
      .catch((err) => {
        console.error("Failed to copy: ", err);
      });
  };

  const handleStartGame = () => {
    socket.emit("start-game");
  };

  return (
    <>
      <HomeButton />
      <div style={{ textAlign: "center", marginTop: "100px" }}>
        <h1>Lobby</h1>
        <div className="lobby-grid">
          {Array.from({ length: 8 }).map((_, index) => {
            const user = users[index];
            return (
              <div
                key={index}
                className={`lobby-box ${user ? "filled" : "empty"}`}
                style={{ background: user ? user.color : "lightgray" }}
              >
                {user ? user.username : "Waiting...."}
              </div>
            );
          })}
        </div>
        <button onClick={handleCopyLink} className="base-button">
          Copy Lobby Link
        </button>
        <button onClick={handleStartGame} className="base-button">
          Start Game
        </button>
      </div>
    </>
  );
};

export default LobbyScreen;
