import React from "react";
import { useNavigate } from "react-router-dom";
import { useDataContext } from "../../context/context.tsx";
import "./Unauthorized.css";

const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();
  const { collectionPath, externalDatasetId } = useDataContext();
  console.log("Unautorized: Collection path: ", collectionPath);
  console.log("Unauthorized: External dataset id: ", externalDatasetId);
  return (
    <div className="unauthorized-container">
      <div className="unauthorized-box">
        <h1 className="unauthorized-title">Unhautorized Access</h1>
        <p className="unauthorized-text">
          You are not allowed to access this route.
        </p>
        <button
          className="unauthorized-button"
          onClick={() =>
            navigate(
              `/MappingsScreen?connection_string=neo4j%2Bs%3A%2F%2F5312230f.databases.neo4j.io%24neo4j%24NmQmFeKBVkBrYdEQqq8YC6XJuN6J6kGFIGO62KY8bU4&collection_path=${collectionPath}&id_dataset=${externalDatasetId}`
            )
          } // Ajusta esta ruta según el flujo de tu app
        >
          Back to Mappings List
        </button>
      </div>
    </div>
  );
};

export default UnauthorizedPage;
