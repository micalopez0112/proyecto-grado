// components/Navbar.tsx
import React from "react";
import { Link } from "react-router-dom";
import { useDataContext } from "../../context/context.tsx";
import {connectNeo4jDB} from "../../services/mapsApi.ts";
import {toast} from "react-toastify";
import "./Navbar.css"; // You will style the navbar in this file
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const {externalFlow,setExternalFlow,outOfExternalFlow} = useDataContext();
  console.log("Valor de externalFlow en Navbar: ", externalFlow);
  const navigate = useNavigate();
  const handleExit = async () =>{
    try{
      const response = await connectNeo4jDB("","","");
      
      if( response && response.status === 200){
        outOfExternalFlow();
        toast.success("The internal flow has been restored");
      }
      else
        toast.error("Error while restoring internal flow");
      navigate("/");
    }
    catch(error){
      console.error("Error in exiting externalFlow: ", error);
    }
  }

  return (
    <>
      {!externalFlow ?
      <nav className="navbar">
        <ul className="navbar-list">
          <li className="navbar-elem">
            <Link to="/">Home</Link>
          </li>
          <li className="navbar-elem">
            <Link to="/MappingsScreen">Mappings</Link>
          </li>
          <li className="navbar-elem">
            <Link to="/DatasetsScreen">Data Quality</Link>
          </li>
        </ul>
      </nav>
      :
      <nav className="navbar" style={{backgroundColor:"#ee7b3f", justifyContent:"flex-end"}}>
        <ul className="navbar-list" style={{paddingRight:"2%"}}>
          <li className="navbar-elem">
            <button onClick={handleExit} className="navbar-button">
              Exit
            </button>
          </li>
        </ul>
      </nav>
      }
    </>
  );
};

export default Navbar;
