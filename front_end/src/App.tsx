import { useEffect } from "react";
import { io } from "socket.io-client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import LoginScreen from "./screens/LoginScreen";
import GameScreen from "./screens/GameScreen";
import LobbyScreen from "./screens/LobbyScreen";

const socket = io("http://localhost:5000");

function App() {
  useEffect(() => {
    socket.on("connect", () => {
      console.log("socket connected with ID", socket.id);
    });

    socket.on("server_response", (data) => {
      console.log("server says", data);
    });

    return () => {
      socket.off("connect");
      socket.off("server_response");
      console.log("socket disconnected");
    };
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginScreen />} />
        <Route path="/room/:roomID" element={<LobbyScreen socket={socket} />} />
        <Route
          path="/room/:roomID/game"
          element={<GameScreen socket={socket} />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
