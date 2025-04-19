import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  createDQModel,
  evaluateMapping,
  getMapping,
} from "../../../services/mapsApi.ts";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { useDataContext } from "../../../context/context.tsx";
import { FaArrowRightLong } from "react-icons/fa6";
import "./SelectMappingsEvaluate.css";
import { JsonSchemaProperty } from "../../../types/JsonSchema.ts";
import { toast } from "react-toastify";
import { AGG_AVERAGE, SYNTCTATIC_ACCURACY } from "../../../types/constants.ts";
import InfoModal from "../../../components/InfoModal/InfoModal.tsx";
import BackButton from "../../../components/BackButton/BackButton.tsx";

const SelectMappingsEvaluate = () => {
  const navigate = useNavigate();
  const {
    mappings,
    setcurrentOntologyId,
    setontologyDataContext,
    setMappings,
    setJsonSchemaContext,
    jsonSchemaContext,
    mappingProcessId,
  } = useDataContext();

  const location = useLocation();
  const { mappingId, rule } = location.state;
  const [evaluateAndCreate, setEvaluateAndCreate] = useState(false);
  const [dqModelName, setdqModelName] = useState<string>("");
  const [selectedMappings, setSelectedMappings] = useState<Record<string, any>>(
    {}
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [allSelected, setAllSelected] = useState<boolean>(false);
  // const [dqAggregatedMethodId, setDQAggregatedMethodId] = useState<string>("");
  // const [dqMethodId, setDQMethodId] = useState<string>("");

  const getSimpleMappings = () => {
    return Object.keys(mappings).filter(
      (key) =>
        key.endsWith("#string") ||
        key.endsWith("#number") ||
        key.endsWith("#integer") ||
        key.endsWith("#boolean")
    );
  };

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingProcessId) {
        setLoading(true);
        try {
          const response = await getMapping(mappingProcessId);
          if (response) {
            const { mapping, schema, ontology } = response.data;
            setMappings(mapping);
            setJsonSchemaContext(schema);
            setcurrentOntologyId(ontology.ontology_id);
            setontologyDataContext(ontology);
          }
        } catch (error) {
          console.error("Error in getMappingData", error);
        }
        setLoading(false);
      }
    };
    getMappingData();
  }, [mappingId]);

  useEffect(() => {
    const simpleMappings = getSimpleMappings();
    const allSimpleSelected = simpleMappings.every((key) =>
      selectedMappings.hasOwnProperty(key)
    );
    setAllSelected(allSimpleSelected);
  }, [selectedMappings, mappings]);

  const handleToggleMapping = (
    key: string,
    mappingElement: any,
    e: React.MouseEvent<HTMLDivElement>
  ) => {
    e.stopPropagation();
    setSelectedMappings((prev) => {
      const updated = { ...prev };
      if (updated[key]) {
        delete updated[key];
      } else {
        updated[key] = mappingElement;
      }
      return updated;
    });
  };

  const handleSelectAllMappings = () => {
    if (!allSelected) {
      const simpleMappings = getSimpleMappings();
      const allMappings: Record<string, any> = {};
      simpleMappings.forEach((key) => {
        allMappings[key] = mappings[key];
      });
      setSelectedMappings(allMappings);
    } else {
      setSelectedMappings({});
    }
  };

  const handleCreateDQModel = async () => {
    if (Object.keys(selectedMappings).length === 0) {
      toast.error("Please select at least one mapping to evaluate.");
      return;
    }

    setLoading(true);

    try {
      console.log("Rule just before create DQModel: ", rule);
      const response = await createDQModel(
        mappingProcessId,
        dqModelName,
        rule.aggRuleId,
        rule.ruleId,
        selectedMappings
      );
      if (response.status === 200) {
        if (response.data.name) {
          console.log("##DQ MODEL ALREADY EXISTS##: ", response.data.name);
          alert(
            "A DQ Model with the same attributes already exists. Its name is: '" +
              response.data.name +
              "'."
          );
          navigate("/DQModelsScreen", {
            state: { mappingId: mappingProcessId, rule: rule },
          });
          return;
        }
        if (evaluateAndCreate) {
          console.log("Response de createDQModel: ", response);
          console.error("Response.data: ", response.data);
          const evaluationResponse = await evaluateMapping(
            SYNTCTATIC_ACCURACY,
            AGG_AVERAGE,
            response.data,
            {}
          );
          if (evaluationResponse) {
            const validationResults = Object.entries(
              evaluationResponse.data
            ).map(([mappingName, score]) => ({
              mappingName,
              score,
            }));
            console.log("Validation results: ", validationResults);
            navigate("/EvaluateMappings", {
              state: {
                mappingId: mappingProcessId,
                ruleId: rule.ruleId,
                validationResults: validationResults,
                dqModelId: response.data,
              },
            });
            if (validationResults.length > 0) {
              toast.success("Successful evaluation");
            } else {
              toast.error("Error evaluating");
            }
          }
        } else {
          navigate("/DQModelsScreen", {
            state: { mappingId: mappingProcessId, rule: rule },
          });
        }
      } else {
        toast.error("Failed to create DQ Model. Please try again.");
      }
    } catch (error) {
      console.error("Error creating DQ Model:", error);
      toast.error("An error occurred. Please check the console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEvaluateAndCreate(e.target.checked);
  };

  const renderProperties = (
    properties: Record<string, JsonSchemaProperty>,
    parent: string
  ) => {
    if (parent === "") {
      return (
        <div>
          <div className="property-box" key={"rootObject"}>
            <div className="json-elem disabled">
              <strong>rootObject:</strong>
            </div>
            <div className="object-properties">
              {renderProperties(properties, "rootObject")}
            </div>
          </div>
        </div>
      );
    } else {
      return Object.entries(properties).map(([key, value]) => {
        const elementKey = parent ? `${parent}-${key}` : key;
        const fullKey = `${elementKey}?key#${value.type}`;
        const isMapped = !!mappings[fullKey];
        const mappingInfo = isMapped ? mappings[fullKey] : null;
        const isActive = !!selectedMappings[fullKey];

        if (value.type === "object" && value.properties) {
          const elementValue = `${elementKey}?value`;
          const isMappedObjectValue = !!mappings[elementValue];
          const mappingInfoValue = isMappedObjectValue
            ? mappings[elementValue]
            : null;
          const isActiveValue = !!selectedMappings[elementValue];
          return (
            <div className="property-box" key={key}>
              <div className="json-elem disabled">
                <strong>{key}:</strong> object
              </div>
              <div className="json-elem object-box">
                <div className="mapping-box disabled">
                  <strong>object</strong>
                  {isMappedObjectValue && (
                    <>
                      <FaArrowRightLong />
                      <span className="mapping-info">
                        {mappingInfoValue?.map((map, index) => (
                          <span key={index} title={map.iri}>
                            {map.name}
                          </span>
                        ))}
                      </span>
                    </>
                  )}
                </div>
                <div className="object-properties">
                  {renderProperties(
                    value.properties,
                    parent ? `${parent}-${key}` : key
                  )}
                </div>
              </div>
              {isMapped && (
                <>
                  <FaArrowRightLong />
                  <span className="mapping-info">
                    {mappingInfo?.map((map, index) => (
                      <span key={index} title={map.iri}>
                        {map.name}
                      </span>
                    ))}
                  </span>
                </>
              )}
            </div>
          );
        }

        if (value.type === "array" && value.items) {
          return (
            <div className="property-box" key={key}>
              <div
                className={`json-elem ${isMapped ? "clickable" : "disabled"} ${
                  isActive ? "active" : ""
                }`}
                onClick={(e) =>
                  isMapped && handleToggleMapping(fullKey, mappingInfo, e)
                }
              >
                <strong>{key}:</strong> array
              </div>
              {isMapped && (
                <span className="mapping-info">
                  {mappingInfo?.map((map, index) => (
                    <span key={index} title={map.iri}>
                      {map.name}
                    </span>
                  ))}
                </span>
              )}
              <div className="object-properties">
                {renderArrayItems(value.items, parent + "-" + key)}
              </div>
            </div>
          );
        }

        return (
          <div className="property-box mapping-box" key={key}>
            <div
              className={`json-elem ${isMapped ? "clickable" : "disabled"} ${
                isActive ? "active" : ""
              }`}
              onClick={(e) =>
                isMapped && handleToggleMapping(fullKey, mappingInfo, e)
              }
            >
              <strong>{key}:</strong> {value.type}
            </div>
            {isMapped && (
              <>
                <FaArrowRightLong />
                <span className="mapping-info">
                  {mappingInfo?.map((map, index) => (
                    <span key={index} title={map.iri}>
                      {map.name}
                    </span>
                  ))}
                </span>
              </>
            )}
          </div>
        );
      });
    }
  };

  const renderArrayItems = (items: JsonSchemaProperty, parent: string) => {
    if (items.type === "object" && items.properties) {
      return (
        <>
          <div
            key={parent + "?value"}
            className={`json-elem array-box disabled`}
          >
            <strong>array items: object</strong>

            <div className="object-properties">
              {renderProperties(items.properties, parent)}
            </div>
          </div>
        </>
      );
    }
    return (
      <>
        <div
          className={`json-elem `}
          onClick={(e) =>
            console.log("clicked array item, doesn´t do anything")
          }
        >
          <strong>array items:</strong> {items.type}
        </div>
      </>
    );
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="container">
          <div className="title-info">
            <BackButton />
            <h1 className="title-section">Select Schema Attributes</h1>
            <InfoModal
              text={
                "Select the JSON Schema attributes where the metric will be applied."
              }
            />
          </div>
          <div className="name-select">
            <div className="dq-model-name">
              <label>DQ Model Name</label>
              <input
                type="text"
                value={dqModelName}
                onChange={(e) => setdqModelName(e.target.value)}
              ></input>
            </div>

            <button
              className="button select-all"
              onClick={handleSelectAllMappings}
            >
              {allSelected ? "Deselect All" : "Select All"}
            </button>
          </div>

          <div className="select-mappings-container">
            {mappings && (
              <div className="mappings">
                {jsonSchemaContext && (
                  <div className="json-schema-container">
                    <div className="json-schema">
                      {jsonSchemaContext
                        ? renderProperties(jsonSchemaContext.properties, "")
                        : null}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="actions">
            <button
              className="button success"
              onClick={handleCreateDQModel}
              disabled={
                !(
                  dqModelName.trim() && Object.keys(selectedMappings).length > 0
                )
              }
              style={{
                backgroundColor:
                  dqModelName.trim() && Object.keys(selectedMappings).length > 0
                    ? "#41a339"
                    : "#ccc",
                cursor:
                  dqModelName.trim() && Object.keys(selectedMappings).length > 0
                    ? "pointer"
                    : "not-allowed",
              }}
            >
              Create New DQ Model
            </button>

            <label className="checkbox-container">
              Evaluate
              <input
                type="checkbox"
                checked={evaluateAndCreate}
                onChange={handleCheckboxChange}
              />
            </label>
          </div>
        </div>
      )}
    </>
  );
};

export default SelectMappingsEvaluate;
