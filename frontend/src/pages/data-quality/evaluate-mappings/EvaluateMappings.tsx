import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";

const EvaluateMappings = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Get selected mappings and ruleId from location.state
  const selectedMappings = location.state?.selectedMappings || [];
  const ruleId = location.state?.ruleId || "";

  const [validationResults, setValidationResults] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  // Validate selected mappings when component mounts
  useEffect(() => {
    const validateSelectedMappings = async () => {
      setLoading(true);
      setError("");

      try {
        // const response = await validateMappings(selectedMappings, ruleId);
        // setValidationResults(response.data);
      } catch (err) {
        console.error("Error validating mappings:", err);
        setError("An error occurred while validating the mappings.");
      } finally {
        setLoading(false);
      }
    };

    if (selectedMappings.length > 0) {
      validateSelectedMappings();
    } else {
      setError("No mappings selected for validation.");
      setLoading(false);
    }
  }, [selectedMappings, ruleId]);

  return (
    <div className="container">
      <h1 className="title-section">Validation Results</h1>

      {loading ? (
        <Spinner />
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="validation-results-container">
          {validationResults.length > 0 ? (
            <ul className="validation-results-list">
              {validationResults.map((result, index) => (
                <li key={index} className="validation-result-item">
                  <div className="result-mapping">
                    <strong>Mapping:</strong> {result.mappingName}
                  </div>
                  <div className="result-status">
                    <strong>Status:</strong>{" "}
                    {result.isValid ? "Valid" : "Invalid"}
                  </div>
                  {result.errorMessage && (
                    <div className="result-error">
                      <strong>Error:</strong> {result.errorMessage}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <div>No validation results found.</div>
          )}
        </div>
      )}

      <button className="back-button" onClick={() => navigate(-1)}>
        Back to Selection
      </button>
    </div>
  );
};

export default EvaluateMappings;
