import React, { useEffect } from "react";
import {toast} from "react-toastify";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate } from "react-router-dom";
import "./HomeScreen.css";

const HomeScreen = () => {
  const navigate = useNavigate();
  const {outOfExternalFlow,externalFlow,setExternalFlow,externalDatasetId,setExternalDatasetId} = useDataContext();
  useEffect(() => {
    console.log("HomeScreen loaded");
    console.log("Check if external user is in")
    if(externalFlow){
      console.log("External user is in")
      outOfExternalFlow();
      toast.success("The internal flow has been restored");
      //navigate("/RedirectScreen");
    }
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
