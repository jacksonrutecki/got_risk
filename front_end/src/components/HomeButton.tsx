import { useNavigate } from "react-router-dom";
import "../styles/main_styles.scss";

const HomeButton = () => {
  const navigate = useNavigate();

  return (
    <button onClick={() => navigate("/")} className="base-button">
      Home
    </button>
  );
};

export default HomeButton;
