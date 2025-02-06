import React, { useEffect,useRef } from "react";
import {toast} from "react-toastify";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate } from "react-router-dom";
import {connectNeo4jDB} from "../../services/mapsApi.ts";
import "./HomeScreen.css";


const HomeScreen = () => {
  const navigate = useNavigate();
  const effectRun = useRef(false);
  
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
