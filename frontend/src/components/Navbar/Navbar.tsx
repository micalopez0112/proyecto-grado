// components/Navbar.tsx
import React from "react";
import { Link } from "react-router-dom";
import { useDataContext } from "../../context/context.tsx";
import "./Navbar.css"; // You will style the navbar in this file

const Navbar = () => {
  const {externalFlow,setExternalFlow} = useDataContext();
  console.log("Valor de externalFlow en Navbar: ", externalFlow);
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
            <Link to="/">Exit</Link>
          </li>
        </ul>
      </nav>
      }
    </>
  );
};

export default Navbar;
