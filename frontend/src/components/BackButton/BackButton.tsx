import React from "react";
import "./BackButton.css";
import { useNavigate } from "react-router-dom";
import { FaAngleLeft } from "react-icons/fa";

const BackButton = () => {
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <button className="back-button" onClick={handleGoBack}>
      <FaAngleLeft size={20} /> Back
    </button>
  );
};

export default BackButton;
