import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { getDatasetMappings } from "../../../services/mapsApi.ts";
import MappingCard from "../../../components/MappingCard.tsx";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import "./DataQualityScreen.css";
import { useDataContext } from "../../../context/context.tsx";

const DataQualityScreen = () => {
  const navigate = useNavigate();
  const { idDataset } = useParams<{ idDataset: string }>();
  const [mappings, setMappings] = useState<
    Array<{ idMapping: string; name: string }>
  >([]);
  const [selectedMappingId, setSelectedMappingId] = useState("");
  const [selectedRuleId, setSelectedRuleId] = useState("");
  const [dataQualityRules, setDataQualityRules] = useState<
    Array<{ id: string; name: string }>
  >([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [mappingDetails, setMappingDetails] = useState<null | {
    mapping_name: string;
    mapping: string;
    schema: string;
    ontology: string;
  }>(null);

  const { setMappingProcessId } = useDataContext();

  useEffect(() => {
    if (idDataset && mappings.length === 0) {
      const retrieveMappings = async () => {
        setLoading(true);
        const mappings = await getDatasetMappings(idDataset);
        console.log(`Mappings for schema ID ${idDataset}: `, mappings);
        if (mappings) setMappings(mappings.data);
        setLoading(false);
      };
      retrieveMappings();

      setDataQualityRules([{ id: "1", name: "Accuracy" }]);
    }
  }, [idDataset, mappings.length]);

  const onClickMappingCard = (id: string) => {
    setSelectedMappingId(id);
  };

  const onClickRule = (id: string) => {
    setSelectedRuleId(id);
  };

  const handleSelectClick = () => {
    if (!selectedMappingId || !selectedRuleId) {
      toast.error("Please select a set of mappings and a quality rule.");
      return;
    }
    setMappingProcessId(selectedMappingId);
    navigate("/DQModelsScreen", {
      state: { mappingId: selectedMappingId, ruleId: selectedRuleId },
    });
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <h1 className="title-section">Data Quality</h1>

          <div className="quality-container">
            <div className="container">
              <div className="data-quality-container">
                <h2 className="sub-title">Set of Mappings</h2>
                <div className="quality-list-container">
                  {mappings.map((mapping) => (
                    <MappingCard
                      key={mapping.idMapping}
                      id={mapping.idMapping}
                      name={mapping.name}
                      style={{
                        ...styles.mappingCard,
                        backgroundColor:
                          selectedMappingId === mapping.idMapping
                            ? "#ffdc92"
                            : "#fff",
                      }}
                      onClickCallback={() =>
                        onClickMappingCard(mapping.idMapping)
                      }
                      includeMappingInfo={true}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div className="container">
              <div className="data-quality-container">
                <h2 className="sub-title">Data Quality Rules</h2>
                <div className="quality-list-container">
                  {dataQualityRules.map((rule) => (
                    <div
                      key={rule.id}
                      onClick={() => onClickRule(rule.id)}
                      style={{
                        ...styles.mappingCard,
                        backgroundColor:
                          selectedRuleId === rule.id ? "#ffdc92" : "#fff",
                      }}
                    >
                      {rule.name}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <button className="select-button" onClick={handleSelectClick}>
            Select
          </button>

          {mappingDetails && (
            <div className="mapping-details-modal">
              <h3>Mapping Details</h3>
              <p>
                <strong>Name:</strong> {mappingDetails.mapping_name}
              </p>
              <p>
                <strong>Mapping:</strong> {mappingDetails.mapping}
              </p>
              <p>
                <strong>Schema:</strong> {mappingDetails.schema}
              </p>
              <p>
                <strong>Ontology:</strong> {mappingDetails.ontology}
              </p>
              <button onClick={() => setMappingDetails(null)}>Close</button>
            </div>
          )}
        </div>
      )}
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

export default DataQualityScreen;
