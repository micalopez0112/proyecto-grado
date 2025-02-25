import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import {
  getDataQualityRules,
  getDatasetMappings,
} from "../../../services/mapsApi.ts";
import MappingCard from "../../../components/MappingCard.tsx";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import "./DataQualityScreen.css";
import { useDataContext } from "../../../context/context.tsx";

const DataQualityScreen = () => {
  const navigate = useNavigate();
  const { setMappingProcessId } = useDataContext();
  const { idDataset } = useParams<{ idDataset: string }>();
  const [mappings, setMappings] = useState<
    Array<{ idMapping: string; name: string }>
  >([]);
  const [selectedMappingId, setSelectedMappingId] = useState("");
  const [loading, setLoading] = useState<boolean>(false);
  const [mappingDetails, setMappingDetails] = useState<null | {
    mapping_name: string;
    mapping: string;
    schema: string;
    ontology: string;
  }>(null);

  const [selectedDimension, setSelectedDimension] = useState<string | null>(
    null
  );
  const [selectedFactor, setSelectedFactor] = useState<string | null>(null);
  const [selectedMeasure, setSelectedMeasure] = useState<null | {
    method_id: string;
    agg_method_id: string;
  }>(null);

  const [dataQualityRules, setDataQualityRules] = useState<
    Array<{
      dimension: string;
      factors: Array<{
        name: string;
        measures: Array<{
          method_id: string;
          agg_method_id: string;
          name: string;
        }>;
      }>;
    }>
  >([]);

  useEffect(() => {
    const fetchDataQualityRules = async () => {
      setLoading(true);
      const response = await getDataQualityRules();
      setDataQualityRules(response);
      setLoading(false);
    };

    fetchDataQualityRules();
  }, []);

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
    }
  }, [idDataset, mappings.length]);

  const onClickMappingCard = (id: string) => {
    setSelectedMappingId(id);
  };

  const onClickDimension = (dimension: string) => {
    setSelectedDimension(dimension);
    setSelectedFactor(null);
    setSelectedMeasure(null);
  };

  const onClickFactor = (factor: string) => {
    setSelectedFactor(factor);
    setSelectedMeasure(null);
  };

  const onClickMeasure = (measure: any) => {
    setSelectedMeasure(measure);
  };

  const handleSelectClick = () => {
    if (!selectedMappingId || !selectedMeasure) {
      toast.error(
        "Please select a mapping, a dimension, a factor, and a measure."
      );
      return;
    }
    setMappingProcessId(selectedMappingId);
    navigate("/DQModelsScreen", {
      state: {
        mappingId: selectedMappingId,
        rule: {
          ruleId: selectedMeasure.method_id,
          aggRuleId: selectedMeasure.agg_method_id,
        },
      },
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
                <div className="quality-list-container">
                  <div>
                    <h2 className="sub-title">Select Dimension</h2>
                    <div className="quality-list-container">
                      {dataQualityRules.map((dim) => (
                        <div
                          key={dim.dimension}
                          onClick={() => onClickDimension(dim.dimension)}
                          style={{
                            ...styles.mappingCard,
                            backgroundColor:
                              selectedDimension === dim.dimension
                                ? "#ffdc92"
                                : "#fff",
                          }}
                        >
                          {dim.dimension}
                        </div>
                      ))}
                    </div>
                  </div>

                  {selectedDimension && (
                    <div>
                      <h2 className="sub-title">Select Factor</h2>
                      <div className="quality-list-container">
                        {dataQualityRules
                          .find((dim) => dim.dimension === selectedDimension)
                          ?.factors.map((factor) => (
                            <div
                              key={factor.name}
                              onClick={() => onClickFactor(factor.name)}
                              style={{
                                ...styles.mappingCard,
                                backgroundColor:
                                  selectedFactor === factor.name
                                    ? "#ffdc92"
                                    : "#fff",
                              }}
                            >
                              {factor.name}
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  {selectedFactor && (
                    <div>
                      <h2 className="sub-title">Select Measure</h2>
                      <div className="quality-list-container">
                        {dataQualityRules
                          .find((dim) => dim.dimension === selectedDimension)
                          ?.factors.find((fact) => fact.name === selectedFactor)
                          ?.measures.map((measure) => (
                            <div
                              key={measure.method_id}
                              onClick={() => onClickMeasure(measure)}
                              style={{
                                ...styles.mappingCard,
                                backgroundColor:
                                  selectedMeasure?.method_id ===
                                  measure.method_id
                                    ? "#ffdc92"
                                    : "#fff",
                              }}
                            >
                              {measure.name}
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
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
          <ToastContainer />
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
