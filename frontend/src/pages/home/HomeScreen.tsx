import React from "react";
import { useNavigate } from "react-router-dom";
import "./HomeScreen.css";

const HomeScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <button className="button" onClick={() => navigate("/MappingsScreen")}>
        Mappings
      </button>
      <button className="button" onClick={() => navigate("/DataQualityScreen")}>
        Data Quality
      </button>
    </div>
  );
};

export default HomeScreen;
