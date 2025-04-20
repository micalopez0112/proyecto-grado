import { useLocation, useNavigate } from "react-router-dom";
import { useDataContext } from "../../context/context.tsx";
import { useEffect, useState } from "react";
import {
  getMapping,
  saveAndValidateMappings,
  saveMapping,
} from "../../services/mapsApi.ts";
import { Spinner } from "../../components/Spinner/Spinner.tsx";
import OntologyData from "../../components/OntologyData.tsx";
import React from "react";
import MappingList from "../../components/MappingList.tsx";
import Json from "../../components/JsonSchema.tsx";
import "./Mapping.css";
import { toast } from "react-toastify";
import InfoModal from "../../components/InfoModal/InfoModal.tsx";
import BackButton from "../../components/BackButton/BackButton.tsx";

export const Mapping = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    mappings,
    clearMappings,
    addNewMapping,
    currentOntologyId,
    setcurrentOntologyId,
    jsonSchemaContext,
    ontologyDataContext,
    setontologyDataContext,
    setMappings,
    setJsonSchemaContext,
    collectionPath,
    resetMappingState,
    externalFlow,
    externalDatasetId,
  } = useDataContext();
  const [mappingName, setMappingName] = useState<string>("");
  const [mappingId, setMappingId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const state = location.state;
    if (state) {
      setMappingId(state.mappingId);
    }
  }, []);

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
          console.error("error en getMappingData", error);
        }
        setLoading(false);
      }
    };
    getMappingData();
  }, [mappingId]);

  const saveMappingsApiCall = async () => {
    try {
      if (Object.keys(mappings).length > 0) {
        if (mappingName !== "") {
          if (mappingId) {
            const body = {
              ontology_id: "",
              name: mappingName,
              mapping: mappings,
              jsonSchema: jsonSchemaContext, // OJO sume esto!
              mapping_proccess_id: mappingId,
            };
            setLoading(true);
            const response = await saveMapping(body);
            setLoading(false);
            if (response) {
              const { status } = response.data;
              if (status === "success") {
                resetMappingState();
                toast.success(`Process Mapping saved successfully`);
                navigate("/");
              } else {
                toast.success(`Error saving Mapping Process`);
              }
            }
          } else {
            //new mapping
            if (currentOntologyId) {
              const schemaAndCollectionName = jsonSchemaContext;
              schemaAndCollectionName.collection_name =
                collectionPath.split(".")[0];

              const body = {
                ontology_id: currentOntologyId,
                name: mappingName,
                mapping: mappings,
                jsonSchema: schemaAndCollectionName,
                mapping_proccess_id: mappingId,
                documentStoragePath: collectionPath,
              };

              const response = await saveMapping(body);
              if (response) {
                const { status } = response.data;
                if (status === "success") {
                  resetMappingState();
                  toast.success("Process Mapping saved successfully");
                  navigate("/");
                } else {
                  toast.error("Error saving Mapping Process");
                }
              }
            } else {
              console.error("#ERROR#: No hay ontologyId al editar");
            }
          }
        } else {
          toast.error("Mapping name must not be empty");
        }
      } else {
        toast.error("Mappings must not be empty");
      }
    } catch (error) {
      console.error("error en apiCall", error);
    }
  };

  const validateAndSaveMappingsApiCall = async () => {
    try {
      if (Object.keys(mappings).length > 0) {
        if (mappingId) {
          const body = {
            ontology_id: currentOntologyId,
            name: mappingName,
            mapping: mappings,
            jsonSchema: jsonSchemaContext,
            mapping_proccess_id: mappingId,
            ...(externalFlow && { jsonSchemaId: externalDatasetId }),
          };
          setLoading(true);
          const response = await saveAndValidateMappings(
            currentOntologyId!,
            mappingId,
            body
          );
          setLoading(false);
          console.log("Response", response)
          if (response) {
            const { status, message } = response.data;
            if (status === "success") {
              resetMappingState();
              toast.success("Set of mappings successfully validated and saved");
              if (externalFlow && externalDatasetId) {
                //en flujo externo que vaya directo a evaluar calidad de los atributos con los
                //mappings y las métricas definidas
                console.log("External flow: ", externalFlow);
                navigate(`/DataQualityScreen/${externalDatasetId}`);
              } else navigate("/");
            } else {
              if (response.data && response.data.mapping_id) {
                setMappingId(response.data.mapping_id);
              }
              toast.error("Error validating mapping, please check: " + message);
            }
          }
        } else {
          if (currentOntologyId) {
            const schemaAndCollectionName = jsonSchemaContext;
            schemaAndCollectionName.collection_name =
              collectionPath.split(".")[0];
            const body = {
              name: mappingName,
              mapping: mappings,
              jsonSchema: schemaAndCollectionName,
              documentStoragePath: collectionPath,
              ...(externalFlow && { jsonSchemaId: externalDatasetId }),
            };
            setLoading(true);
            const response = await saveAndValidateMappings(
              currentOntologyId,
              "",
              body
            );
            setLoading(false);
            if (response) {
              const { status, message } = response.data;
              if (status === "success") {
                // resetMappingState();
                toast.success("Set of mappings successfully validated and saved");
                if (externalFlow && externalDatasetId) {
                  //en flujo externo que vaya directo a evaluar calidad de los atributos con los
                  //mappings y las métricas definidas
                  console.log("External flow: ", externalFlow);
                  navigate(`/DataQualityScreen/${externalDatasetId}`);
                } else {
                  resetMappingState();
                  navigate("/");
                }
              } else {
                if (response.data && response.data.mapping_id) {
                  setMappingId(response.data.mapping_id);
                }
                toast.error(
                  "Error validating mapping, please check: " + message
                );
              }
            }
          } else {
            console.log("No hay ontologyId");
          }
        }
      } else {
        toast.error("Mapping entries must not be empty");
      }
    } catch (error) {
      console.error("error en apiCall", error);
    }
  };

  useEffect(() => {
    const state = location.state;
    if (state) {
      setMappingId(state.mappingId);
    }
  }, []);

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingId) {
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
          console.error("error en getMappingData", error);
        }
      }
    };
    getMappingData();
  }, [mappingId]);

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="App">
          <div className="title-info">
            <BackButton />
            <div className="mapping-name">
              <label>Name</label>
              <input
                type="text"
                value={mappingName}
                onChange={(e) => setMappingName(e.target.value)}
              ></input>
            </div>
            <InfoModal
              text={
                'On this screen, you can define mappings between the domain ontology and the JSON Schema structure of the uploaded dataset. These mappings can be used to evaluate the quality of the dataset on the Data Quality flow of the application. The "Name" input field will be displayed on the Mappings List screen to identify this mapping.'
              }
            />
          </div>
          <div className="content-container">
            <div className="content-box">
              <Json />
            </div>
            <div className="content-box">
              <OntologyData />
            </div>
            <div className="content-box">
              <div className="container">
                <div className="title-wrapper">
                  <h1 className="title">Mappings</h1>
                </div>
                <div className="add-clean-buttons">
                  <button className="button" onClick={addNewMapping}>
                    Add mapping
                  </button>
                  <button className="button" onClick={clearMappings}>
                    Clear mappings
                  </button>
                </div>
                <MappingList isResult={false} />
                <div className="mapping-button-wrapper">
                  <button
                    className="button success"
                    onClick={validateAndSaveMappingsApiCall}
                  >
                    Validate & Save
                  </button>
                  {!externalFlow ? (
                    <button
                      className="button success"
                      onClick={saveMappingsApiCall}
                    >
                      Save
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
