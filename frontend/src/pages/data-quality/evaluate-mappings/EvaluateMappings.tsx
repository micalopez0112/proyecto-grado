import React, { useState } from "react";
import Modal from "react-modal";
import { useLocation } from "react-router-dom";
import { StyledSpinnerImage } from "../../../components/Spinner/Spinner.tsx";
import { fetchDetailedEvaluationResults } from "../../../services/mapsApi.ts";
import "./EvaluateMappings.css";
import { FaAngleLeft, FaAngleRight, FaEye } from "react-icons/fa";
import InfoModal from "../../../components/InfoModal/InfoModal.tsx";

const PAGE_SIZE = 10;

const EvaluateMappings = () => {
  const location = useLocation();
  const { mappingId, dqModelId } = location.state;
  const initialResults = location.state?.validationResults || [];

  const [detailedResults, setDetailedResults] = useState<any[]>([]);
  const [selectedMapping, setSelectedMapping] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [modalIsOpen, setModalIsOpen] = useState<boolean>(false);

  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);

  const handleFetchDetailedResults = async (mappingName: string, page = 1) => {
    if (!mappingId) {
      setError("Mapping process ID is not available.");
      return;
    }

    setLoading(true);
    setSelectedMapping(mappingName);
    const offset = (page - 1) * PAGE_SIZE;

    try {
      const data = await fetchDetailedEvaluationResults(
        mappingId,
        mappingName,
        dqModelId,
        PAGE_SIZE,
        offset
      );
      setDetailedResults(data.results);
      setTotalResults(data.total || 0);
      setCurrentPage(page);
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
    setCurrentPage(1);
  };

  const totalPages = Math.ceil(totalResults / PAGE_SIZE);

  return (
    <div className="container">
      <div className="title-info">
        <h1 className="title-section">Evaluation results</h1>
        <InfoModal
          text={
            "This page shows the evaluation results for each attribute at Field level. Click on the eye icon to see the evaluation results for each document."
          }
        />
      </div>
      {error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="validation-results-container">
          {initialResults.length > 0 ? (
            <ul className="validation-results-list">
              {initialResults.map((result, index) => (
                <li
                  key={index}
                  className="validation-result-item card no-hover"
                >
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
        <h2>Evaluation results for: {selectedMapping}</h2>
        {loading ? (
          <div className="spinner-wrapper">
            <StyledSpinnerImage />
          </div>
        ) : detailedResults.length > 0 ? (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Document ID</th>
                  <th>Date</th>
                  <th>Measure</th>
                </tr>
              </thead>
              <tbody>
                {detailedResults.map((detail, idx) => (
                  <tr key={idx}>
                    <td>{detail.id_document}</td>
                    <td>{detail.date}</td>
                    <td>{detail.measure}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="pagination">
              <button
                disabled={currentPage === 1}
                onClick={() =>
                  handleFetchDetailedResults(selectedMapping!, currentPage - 1)
                }
                className="pages-button"
              >
                <FaAngleLeft size={20} />
              </button>
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <button
                disabled={currentPage === totalPages || totalResults === 0}
                onClick={() =>
                  handleFetchDetailedResults(selectedMapping!, currentPage + 1)
                }
                className="pages-button"
              >
                <FaAngleRight size={20} />
              </button>
            </div>
          </div>
        ) : (
          <p>No evaluation results available.</p>
        )}
        <button className="button" onClick={closeModal}>
          Close
        </button>
      </Modal>
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
    width: "800px",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "space-around",
    height: "700px",
  },
  modalContent: {
    width: "100%",
    height: "100%",
    overflow: "auto",
  },
};

export default EvaluateMappings;
