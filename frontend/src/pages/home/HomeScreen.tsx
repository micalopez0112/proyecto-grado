import React, { useEffect } from "react";
import {toast} from "react-toastify";
import { useDataContext } from "../../context/context.tsx";
import { useNavigate } from "react-router-dom";
import {connectNeo4jDB} from "../../services/mapsApi.ts";
import "./HomeScreen.css";

const HomeScreen = () => {
  const navigate = useNavigate();
  const {outOfExternalFlow,externalFlow,setExternalFlow,externalDatasetId,setExternalDatasetId} = useDataContext();
  useEffect(() => {
    const checkExternalFlow = async () => {;
      console.log("HomeScreen loaded");
      console.log("Check if external user is in")
      if(externalFlow){
        console.log("External user is in")
        outOfExternalFlow();
        //call to backend to restore local Neo4j connection
        const response = await connectNeo4jDB("","","");
        if( response && response.status === 200)
          toast.success("The internal flow has been restored");
        else{
          toast.error("Error while restoring internal flow");
          //navigate to MappingsScreen con los parametros de la URL
        }
        //navigate("/RedirectScreen");
      }
    }
    checkExternalFlow();
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
