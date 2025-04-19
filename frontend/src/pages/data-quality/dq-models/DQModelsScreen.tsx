import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "react-toastify";
import { evaluateMapping, getDQModels } from "../../../services/mapsApi.ts";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import "./DQModelsScreen.css";
import { useDataContext } from "../../../context/context.tsx";

import { SYNTCTATIC_ACCURACY, AGG_AVERAGE } from "../../../types/constants.ts";
import DQModelCard from "../../../components/DQModelCard/DQModelCard.tsx";
import InfoModal from "../../../components/InfoModal/InfoModal.tsx";
import BackButton from "../../../components/BackButton/BackButton.tsx";

const DQModelsScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [dqModels, setDQModels] = useState<Record<string, string>>({});
  const [selectedDQModelId, setSelectedDQModelId] = useState("");
  const [loading, setLoading] = useState<boolean>(false);
  const { mappingProcessId } = useDataContext();
  const { mappingId, rule } = location.state;

  useEffect(() => {
    const fetchDQModels = async () => {
      if (!mappingId) {
        console.error("Mapping process ID is missing!");
        return;
      }
      setLoading(true);
      try {
        const response = await getDQModels(mappingId, rule.ruleId);
        setDQModels(response.data);
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
    navigate("/SelectMappingsValidate", {
      state: { mappingId: mappingProcessId, rule: rule },
    });
  };

  const onSelectModel = (id: string) => {
    if (selectedDQModelId === id) {
      setSelectedDQModelId("");
    } else {
      setSelectedDQModelId(id);
    }
  };

  const handleEvaluateClick = async () => {
    try {
      setLoading(true);
      const response = await evaluateMapping(
        SYNTCTATIC_ACCURACY,
        AGG_AVERAGE,
        selectedDQModelId,
        {}
      );
      if (response) {
        const validationResults = Object.entries(response.data).map(
          ([mappingName, score]) => ({
            mappingName,
            score,
          })
        );
        navigate("/EvaluateMappings", {
          state: {
            mappingId: mappingId,
            ruleId: rule.ruleId,
            validationResults: validationResults,
            dqModelId: selectedDQModelId,
          },
        });
        if (validationResults.length > 0) {
          toast.success("Successful evaluation");
        } else {
          toast.error("Error evaluating");
        }
      }
    } catch (error) {
      console.error("Error evaluating mappings:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <div className="title-info">
            <BackButton />
            <h1 className="title-section">Available DQ Model’s</h1>
            <InfoModal
              text={
                'You can select a defined Data Quality Model or create a new one clicking on "New DQ Model". The DQ Model is defined based on the mapped attributes  of the previously selected dataset.Click on "Evaluate" to run the evaluation of the selected DQ Model.'
              }
            />
          </div>
          <div className="dq-models-container">
            {Object.entries(dqModels).length > 0 ? (
              Object.entries(dqModels).map(([id, name]) => (
                <DQModelCard
                  key={id}
                  id={id}
                  name={name}
                  style={{
                    backgroundColor:
                      selectedDQModelId === id ? "#ffdc92" : "#efefef",
                  }}
                  onClickCallback={() => onSelectModel(id)}
                />
              ))
            ) : (
              <p className="no-elements-message">
                No DQ Models available for selected Metric
              </p>
            )}
          </div>
          <div className="dq-models-buttons">
            <button className="select-button" onClick={handleSelectClick}>
              New DQ Model
            </button>
            <button
              className="select-button"
              onClick={handleEvaluateClick}
              disabled={!selectedDQModelId}
              style={{
                backgroundColor: selectedDQModelId ? "#41a339" : "#ccc",
                cursor: selectedDQModelId ? "pointer" : "not-allowed",
              }}
            >
              Evaluate
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default DQModelsScreen;
