import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/main_styles.scss";

const LoginScreen = () => {
  const [username, setUsername] = useState("");
  const navigate = useNavigate();

  const handleJoinRoom = () => {
    const roomID = prompt("Enter Room ID");
    if (roomID) {
      navigate(`/room/${roomID}`, { state: { username } });
    }
  };

  const handleCreateRoom = async () => {
    const roomID = Math.random().toString(36).substring(2, 8);
    navigate(`/room/${roomID}`, { state: { username } });
  };

  return (
    <div style={{ textAlign: "center", marginTop: "200px" }}>
      <h1>Login</h1>
      <input
        type="text"
        placeholder="Enter your username..."
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <br />
      <button onClick={handleJoinRoom} className="base-button">
        Join Existing Room
      </button>
      <br />
      <button onClick={handleCreateRoom} className="base-button">
        Create Private Room
      </button>
    </div>
  );
};

export default LoginScreen;
