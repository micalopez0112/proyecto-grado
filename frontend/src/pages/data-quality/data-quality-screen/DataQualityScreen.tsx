import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchMappings, getMapping } from "../../../services/mapsApi.ts";
import MappingCard from "../../../components/MappingCard.tsx";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import "./DataQualityScreen.css";

const DataQualityScreen = () => {
  const navigate = useNavigate();
  const [mappings, setMappings] = useState<Array<{ id: string; name: string }>>(
    []
  );
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

  useEffect(() => {
    const retrieveMappings = async () => {
      setLoading(true);
      const mappings = await fetchMappings(true);
      console.log("Mappings: ", mappings);
      if (mappings) setMappings(mappings.data);
      setLoading(false);
    };
    retrieveMappings();

    setDataQualityRules([{ id: "1", name: "Accuracy" }]);
  }, []);

  const onClickMappingCard = (id: string) => {
    setSelectedMappingId(id);
  };

  const onClickRule = (id: string) => {
    setSelectedRuleId(id);
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
                <h2 className="sub-title">Mappings</h2>
                <div className="quality-list-container">
                  {mappings.map((mapping) => (
                    <MappingCard
                      key={mapping.id}
                      id={mapping.id}
                      name={mapping.name}
                      style={{
                        ...styles.mappingCard,
                        backgroundColor:
                          selectedMappingId === mapping.id ? "#f39c12" : "#fff",
                      }}
                      onClickCallback={() => onClickMappingCard(mapping.id)}
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
                          selectedRuleId === rule.id ? "#f39c12" : "#fff",
                      }}
                    >
                      {rule.name}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <button
            className="select-button"
            onClick={() =>
              navigate("/SelectMappingsValidate", {
                state: { mappingId: selectedMappingId, ruleId: selectedRuleId },
              })
            }
            disabled={!selectedMappingId || !selectedRuleId}
          >
            Seleccionar
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
    display: "grid",
    gridTemplateColumns: "1fr 2fr",
    padding: 10,
    cursor: "pointer",
    borderRadius: 5,
  },
};

export default DataQualityScreen;
