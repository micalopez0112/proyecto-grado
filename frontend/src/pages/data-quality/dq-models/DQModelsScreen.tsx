import React, { useEffect, useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { getDQModels } from "../../../services/mapsApi.ts";
import MappingCard from "../../../components/MappingCard.tsx";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import "./DQModelsScreen.css";
import { useDataContext } from "../../../context/context.tsx";

const DQModelsScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [dqModels, setDQModels] = useState<Record<string, string>>({});

  const [selectedDQModel, setSelectedDQModel] = useState("");
  const [loading, setLoading] = useState<boolean>(false);

  const { mappingProcessId } = useDataContext();

  useEffect(() => {
    const fetchDQModels = async () => {
      if (!mappingProcessId) {
        console.error("Mapping process ID is missing!");
        return;
      }
      setLoading(true);
      try {
        const response = await getDQModels(mappingProcessId, "D1F1M1MD1");
        console.log("API Response: ", response.data);
        setDQModels(response.data); // Assuming response.data is an array
      } catch (error) {
        toast.error("Failed to fetch Data Quality models");
        console.error("Error fetching DQ models:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDQModels();
  }, [location.state, mappingProcessId]);

  const handleSelectClick = () => {
    navigate("/EvaluateMappings", {
      state: {
        state: { mappingId: selectedDQModel, ruleId: "D1F1M1MD1" },
      },
    });
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <h1 className="title-section">Instances of selected Metric</h1>
          <div className="dq-models-container">
            {Object.entries(dqModels).length > 0 ? (
              Object.entries(dqModels).map(([id, name]) => (
                <MappingCard
                  key={id}
                  id={id}
                  name={name}
                  style={{
                    ...styles.mappingCard,
                    backgroundColor:
                      selectedDQModel === id ? "#ffdc92" : "#fff",
                  }}
                  onClickCallback={() => setSelectedDQModel(id)}
                  includeMappingInfo={true}
                />
              ))
            ) : (
              <>No Instances of selected Metric</>
            )}
          </div>
          <div className="dq-models-buttons">
            <button className="select-button" onClick={handleSelectClick}>
              New Metric Instance
            </button>
            <button
              className="select-button"
              onClick={handleSelectClick}
              disabled={!selectedDQModel}
              style={{
                backgroundColor: selectedDQModel ? "#007bff" : "#ccc",
                cursor: selectedDQModel ? "pointer" : "not-allowed",
              }}
            >
              Evaluate
            </button>
          </div>
        </div>
      )}
      <ToastContainer />
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  mappingCard: {
    display: "flex",
    padding: 10,
    cursor: "pointer",
    borderRadius: 5,
    alignItems: "center",
    justifyContent: "space-between",
  },
};

export default DQModelsScreen;
