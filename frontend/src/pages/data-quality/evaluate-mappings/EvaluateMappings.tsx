import React, { useEffect, useState } from "react";
import Modal from "react-modal";
import { useLocation, useNavigate } from "react-router-dom";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { fetchDetailedEvaluationResults } from "../../../services/mapsApi.ts";
import "./EvaluateMappings.css";
import { FaEye } from "react-icons/fa";

const EvaluateMappings = () => {
  const location = useLocation();
  const navigate = useNavigate();
  // const { mappingProcessId } = useDataContext();
  const { mappingId, dqModelId } = location.state;
  const initialResults = location.state?.validationResults || {};

  const [detailedResults, setDetailedResults] = useState<any[]>([]);
  const [selectedMapping, setSelectedMapping] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [modalIsOpen, setModalIsOpen] = useState<boolean>(false);

  const handleFetchDetailedResults = async (mappingName: string) => {
    if (!mappingId) {
      setError("Mapping process ID is not available.");
      return;
    }

    setLoading(true);
    setSelectedMapping(mappingName);
    try {
      const data = await fetchDetailedEvaluationResults(
        mappingId,
        mappingName,
        dqModelId
      );
      setDetailedResults(data);
      setModalIsOpen(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setSelectedMapping(null);
    setDetailedResults([]);
  };

  console.log("Initial results: ", initialResults);

  return (
    <div className="container">
      <h1 className="title-section">Validation Results</h1>

      {loading ? (
        <Spinner />
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="validation-results-container">
          {initialResults.length > 0 ? (
            <ul className="validation-results-list">
              {initialResults.map((result, index) => (
                <li key={index} className="validation-result-item">
                  <div className="result-mapping">
                    <strong>Mapping:</strong> {result.mappingName}
                  </div>
                  <div className="result-score">
                    <strong>Score:</strong> {result.score}
                  </div>
                  <button
                    className="info-button"
                    onClick={() =>
                      handleFetchDetailedResults(result.mappingName)
                    }
                  >
                    <FaEye size={20} />
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div>No validation results found.</div>
          )}
        </div>
      )}

      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={modalStyles}
        ariaHideApp={false}
      >
        <div style={modalStyles.modalContent}>
          <h2>Detailed Results for: {selectedMapping}</h2>
          {loading && <Spinner />}
          {!loading && detailedResults.length > 0 ? (
            <ul>
              {detailedResults.map((detail, idx) => (
                <li key={idx}>
                  <strong>Detail:</strong> {JSON.stringify(detail)}
                </li>
              ))}
            </ul>
          ) : (
            <p>No detailed results available.</p>
          )}
          <button className="button" onClick={closeModal}>
            Close
          </button>
        </div>
      </Modal>

      <button className="back-button" onClick={() => navigate(-1)}>
        Back to Selection
      </button>
    </div>
  );
};

const modalStyles: { [key: string]: React.CSSProperties } = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    transform: "translate(-50%, -50%)",
    width: "600px",
    height: "400px",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  },
  modalContent: {
    width: "100%",
    height: "100%",
    overflow: "auto",
  },
};

export default EvaluateMappings;
