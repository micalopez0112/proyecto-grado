import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchMappings } from "../../../services/mapsApi.ts";
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

  useEffect(() => {
    const retrieveMappings = async () => {
      setLoading(true);
      const mappings = await fetchMappings();
      console.log("Mappings: ", mappings);
      //setMappings(mappings);
      if (mappings) setMappings(mappings.data);
      setLoading(false);
    };
    retrieveMappings();

    setDataQualityRules([
      { id: "1", name: "Accuracy" },
      { id: "2", name: "Accuracy 2" },
    ]);
  }, []);

  const onClickMappingCard = (id: string) => {};

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <h1 className="title-section">Data Quality</h1>

          <div className="quality-container">
            {mappings && (
              <div className="container">
                <div className="data-quality-container">
                  <h2 className="sub-title">Mappings</h2>
                  {mappings.map((mapping) => (
                    <MappingCard
                      style={styles.mappingCard}
                      key={mapping.id}
                      id={mapping.id}
                      name={mapping.name}
                      onClickCallback={onClickMappingCard}
                    />
                  ))}
                </div>
              </div>
            )}

            {mappings && (
              <div className="container">
                <div className="data-quality-container">
                  <h2 className="sub-title">Data Quality Rules</h2>
                  {dataQualityRules.map((rule) => (
                    <div>{rule.name}</div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <button
            className="select-button"
            onClick={() =>
              navigate("/SelectMappings", {
                state: { mappingId: selectedMappingId, ruleId: selectedRuleId },
              })
            }
          >
            Seleccionar
          </button>
        </div>
      )}
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  mappingCard: {
    display: "grid",
    gridTemplateColumns: "1fr 2fr",
    padding: "20px",
    backgroundColor: "#f0f0f0",
  },
};

export default DataQualityScreen;
