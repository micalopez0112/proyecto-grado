import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
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
  const [selectedMetric, setSelectedMetric] = useState<null | {
    method_id: string;
    agg_method_id: string;
  }>(null);

  const [dataQualityRules, setDataQualityRules] = useState<
    Array<{
      dimension: string;
      factors: Array<{
        name: string;
        metrics: Array<{
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
    if (selectedMappingId === id) {
      setSelectedMappingId("");
    } else {
      setSelectedMappingId(id);
    }
  };

  const onClickDimension = (dimension: string) => {
    if (dimension === selectedDimension) {
      setSelectedDimension(null);
      setSelectedFactor(null);
      setSelectedMetric(null);
    } else {
      setSelectedDimension(dimension);
      setSelectedFactor(null);
      setSelectedMetric(null);
    }
  };

  const onClickFactor = (factor: string) => {
    if (factor === selectedFactor) {
      setSelectedFactor(null);
      setSelectedMetric(null);
    } else {
      setSelectedFactor(factor);
      setSelectedMetric(null);
    }
  };

  const onClickMetric = (metric: any) => {
    if (metric === selectedMetric) {
      setSelectedMetric(null);
    } else {
      setSelectedMetric(metric);
    }
  };

  const handleSelectClick = () => {
    if (!selectedMappingId || !selectedMetric) {
      toast.error(
        "Please select a mapping, a dimension, a factor, and a metric."
      );
      return;
    }
    setMappingProcessId(selectedMappingId);
    navigate("/DQModelsScreen", {
      state: {
        mappingId: selectedMappingId,
        rule: {
          ruleId: selectedMetric.method_id,
          aggRuleId: selectedMetric.agg_method_id,
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
                <h2 className="sub-title">List of Mappings</h2>
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
                      {dataQualityRules.length === 0 ? (
                        <p className="no-elements-message">
                          No dimensions available.
                        </p>
                      ) : (
                        dataQualityRules.map((dim) => (
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
                            className="dimension-card"
                          >
                            {dim.dimension}
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {selectedDimension && (
                    <div>
                      <h2 className="sub-title">Select Factor</h2>
                      <div className="quality-list-container">
                        {dataQualityRules.find(
                          (dim) => dim.dimension === selectedDimension
                        )?.factors.length === 0 ? (
                          <p className="no-elements-message">
                            No factors available.
                          </p>
                        ) : (
                          dataQualityRules
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
                                className="factor-card"
                              >
                                {factor.name}
                              </div>
                            ))
                        )}
                      </div>
                    </div>
                  )}

                  {selectedFactor && (
                    <div>
                      <h2 className="sub-title">Select Metric</h2>
                      <div className="quality-list-container">
                        {dataQualityRules
                          .find((dim) => dim.dimension === selectedDimension)
                          ?.factors.find((fact) => fact.name === selectedFactor)
                          ?.metrics.length === 0 ? (
                          <p className="no-elements-message">
                            No metrics available.
                          </p>
                        ) : (
                          dataQualityRules
                            .find((dim) => dim.dimension === selectedDimension)
                            ?.factors.find(
                              (fact) => fact.name === selectedFactor
                            )
                            ?.metrics.map((metric) => (
                              <div
                                key={metric.method_id}
                                onClick={() => onClickMetric(metric)}
                                style={{
                                  ...styles.mappingCard,
                                  backgroundColor:
                                    selectedMetric?.method_id ===
                                    metric.method_id
                                      ? "#ffdc92"
                                      : "#fff",
                                }}
                                className="metric-card"
                              >
                                {metric.name}
                              </div>
                            ))
                        )}
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
