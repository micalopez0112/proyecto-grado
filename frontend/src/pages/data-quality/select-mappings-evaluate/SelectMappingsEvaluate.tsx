import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { evaluateMapping, getMapping } from "../../../services/mapsApi.ts";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { useDataContext } from "../../../context/context.tsx";
import { FaArrowRightLong } from "react-icons/fa6";
import "./SelectMappingsEvaluate.css";
import { JsonSchemaProperty } from "../../../types/JsonSchema.ts";

const SYNTCTATIC_ACCURACY = "syntactic_accuracy";
const QUALITY_RULES = [SYNTCTATIC_ACCURACY];

const SelectMappingsEvaluate = () => {
  const navigate = useNavigate();
  const {
    mappings,
    setcurrentOntologyId,
    setontologyDataContext,
    setMappings,
    setJsonSchemaContext,
    jsonSchemaContext,
  } = useDataContext();

  const location = useLocation();
  const mappingId = location.state?.mappingId;
  const ruleId = location.state?.ruleId;

  const [mappingName, setMappingName] = useState<string>("");
  const [selectedMappings, setSelectedMappings] = useState<Record<string, any>>(
    {}
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [allSelected, setAllSelected] = useState<boolean>(false);

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingId) {
        setLoading(true);
        try {
          const response = await getMapping(mappingId);
          if (response) {
            const { mapping_name, mapping, schema, ontology } = response.data;
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
      console.log("updated:", { updated });
      return updated;
    });
  };

  const handleSelectAllMappings = () => {
    if (!allSelected) {
      const allMappings: Record<string, any> = {};
      Object.keys(mappings).forEach((key) => {
        allMappings[key] = mappings[key];
      });
      setSelectedMappings(allMappings);
    } else {
      setSelectedMappings({});
    }
    setAllSelected(!allSelected);
  };

  const handleEvaluateSelectedMappings = async () => {
    const response = await evaluateMapping(
      SYNTCTATIC_ACCURACY,
      mappingId,
      selectedMappings
    );
    navigate("/EvaluateMappings", {
      state: {
        selectedMappings,
        ruleId,
      },
    });
  };

  const renderProperties = (
    properties: Record<string, JsonSchemaProperty>,
    parent: string
  ) => {
    return Object.entries(properties).map(([key, value]) => {
      let elementKey = parent ? `${parent}-${key}` : key;
      elementKey = elementKey.replace(/^rootObject-/, "");

      const fullKey = `${elementKey}_key#${value.type}`;

      // Check if this property has a mapping
      const isMapped = !!mappings[fullKey];
      console.log(isMapped);
      console.log(fullKey);
      console.log({ mappings });
      const mappingInfo = isMapped ? mappings[fullKey] : null;
      const isActive = !!selectedMappings[fullKey];

      if (parent === "") {
        return (
          <div>
            <div className="property-box" key={"rootObject"}>
              <div className={`json-elem`}>
                <strong>rootObject:</strong>
              </div>
              <div className="object-properties">
                {renderProperties(properties, "rootObject")}
              </div>
            </div>
          </div>
        );
      }
      if (value.type === "object" && value.properties) {
        const elementValue = elementKey + "_value";
        console.log("elementValue: " + elementValue);
        const isMappedObjectValue = !!mappings[elementKey + "_value"];
        console.log("isMappedObjectValue " + isMappedObjectValue);
        const mappingInfoValue = isMappedObjectValue
          ? mappings[elementValue]
          : null;
        const isActiveValue = !!selectedMappings[elementValue];
        return (
          <>
            <div className={`property-box disabled`} key={key}>
              <div className={`json-elem disabled`}>
                <strong>{key}:</strong> object
              </div>

              {
                <div
                  key={key + "_value"}
                  className={`json-elem `}
                  style={{
                    marginLeft: "20px",
                    backgroundColor: "#e3fae3",
                    borderColor: "#67cb6f",
                    border: "1px solid",
                  }}
                >
                  <div className="mapping-box">
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
                      parent ? parent + "-" + key : key
                    )}
                  </div>
                </div>
              }

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
          </>
        );
      }

      // Handling for "array" type
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
                  onClick={handleEvaluateSelectedMappings}
                  disabled={Object.keys(selectedMappings).length === 0}
                >
                  Evaluate Selected Mappings
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
