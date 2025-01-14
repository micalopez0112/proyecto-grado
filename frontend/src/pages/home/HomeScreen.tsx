import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./HomeScreen.css";

const HomeScreen = () => {
  const navigate = useNavigate();

  useEffect(() => {
    console.log("HomeScreen loaded");
    console.log("Check if external user is in")
    //check if external user is in
    //if so, navigate to RedirectScreen
    //else, do nothing
  }, []);

  return (
    <div className="home-container">
      <button
        className="mappings-button"
        onClick={() => {
          navigate("/MappingsScreen");
        }}
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
