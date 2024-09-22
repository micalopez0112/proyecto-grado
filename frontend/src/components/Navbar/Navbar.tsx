// components/Navbar.tsx
import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css"; // You will style the navbar in this file

const Navbar = () => {
  return (
    <nav className="navbar">
      <ul className="navbar-list">
        <li className="navbar-elem">
          <Link to="/">Home</Link>
        </li>
        <li className="navbar-elem">
          <Link to="/MappingsScreen">Mappings</Link>
        </li>
        <li className="navbar-elem">
          <Link to="/DataQualityScreen">Data Quality</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
