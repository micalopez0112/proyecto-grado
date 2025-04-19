// Spinner.tsx
import React from "react";
import "./Spinner.css";
import spinnerImage from "./../../assets/spinner.svg";

interface SpinnerProps {
  small?: boolean;
}

export const StyledSpinnerImage: React.FC<SpinnerProps> = ({ small }) => {
  return (
    <img
      className={`spinner-image ${small ? "small" : ""}`}
      src={spinnerImage}
      alt="Loading spinner"
    />
  );
};

export const Spinner: React.FC = () => {
  return (
    <div className="spinner-container">
      <StyledSpinnerImage />
    </div>
  );
};
