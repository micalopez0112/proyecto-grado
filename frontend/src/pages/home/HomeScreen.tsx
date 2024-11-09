import React from "react";
import { useNavigate } from "react-router-dom";
import "./HomeScreen.css";

const HomeScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <button
        className="mappings-button"
        onClick={() => navigate("/MappingsScreen")}
      >
        Mappings
      </button>
      <button
        className="quality-button"
        onClick={() => navigate("/DatasetsScreen")}
      >
        Data Quality
      </button>
    </div>
  );
};

export default HomeScreen;
