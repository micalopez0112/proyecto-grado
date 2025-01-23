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
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const SYNTCTATIC_ACCURACY = "syntactic_accuracy";

const SelectMappingsEvaluate = () => {
  const navigate = useNavigate();
  const {
    mappings,
    setcurrentOntologyId,
    setontologyDataContext,
    setMappings,
    setJsonSchemaContext,
    jsonSchemaContext,
    setMappingProcessId,
    mappingProcessId,
  } = useDataContext();

  console.log(mappings);

  const location = useLocation();
  const mappingId = location.state?.mappingId;
  const ruleId = location.state?.ruleId;

  const [mappingName, setMappingName] = useState<string>("");
  const [selectedMappings, setSelectedMappings] = useState<Record<string, any>>(
    {}
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [allSelected, setAllSelected] = useState<boolean>(false);

  const getSimpleMappings = () => {
    return Object.keys(mappings).filter(
      (key) =>
        key.endsWith("#string") ||
        key.endsWith("#number") ||
        key.endsWith("#boolean")
    );
  };

  useEffect(() => {
    console.log("aaa", mappingProcessId);
    const getMappingData = async () => {
      if (mappingProcessId) {
        setLoading(true);
        try {
          const response = await getMapping(mappingProcessId);
          if (response) {
            const { mapping_name, mapping, schema, ontology } = response.data;
            console.log("mappingProcessId: ", mappingProcessId);
            setMappings(mapping);
            setJsonSchemaContext(schema);
            setcurrentOntologyId(ontology.ontology_id);
            setontologyDataContext(ontology);
            setMappingName(mapping_name);
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
      console.log("selectedMappings", selectedMappings);
      const response = await createDQModel(mappingProcessId, selectedMappings);

      if (response.status === 200) {
        toast.success("DQ Model created successfully!");
        navigate("/EvaluateMappings", {
          state: {
            selectedMappings,
            ruleId,
            validationResults: response.data,
          },
        });
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
        const fullKey = `${elementKey}_key#${value.type}`;
        const isMapped = !!mappings[fullKey];
        const mappingInfo = isMapped ? mappings[fullKey] : null;
        const isActive = !!selectedMappings[fullKey];

        if (value.type === "object" && value.properties) {
          const elementValue = `${elementKey}_value`;
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
            key={parent + "_value"}
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
          className={`json-arrayItem-elem `}
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
          <h1 className="title-section">
            Select schema values to evaluate data
          </h1>

          <div className="select-mappings-container">
            {mappings && (
              <div className="mappings">
                <button
                  className="button select-all"
                  onClick={handleSelectAllMappings}
                >
                  {allSelected ? "Deselect All" : "Select All"}
                </button>
                {jsonSchemaContext && (
                  <div className="json-schema-container">
                    <div className="json-schema">
                      {jsonSchemaContext
                        ? renderProperties(jsonSchemaContext.properties, "")
                        : null}
                    </div>
                  </div>
                )}
                <button
                  className="button success"
                  onClick={handleCreateDQModel}
                >
                  Create New DQ Model
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default SelectMappingsEvaluate;
