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
    removeMapping,
    collectionPath,
    resetMappingState,
  } = useDataContext();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [mappingName, setMappingName] = useState<string>("");
  const [mappingId, setMappingId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    //cambiar logica cuando se obtenga el id desde el back
    console.log("#COLLECTION PATH EN MAPPINGS.TSX: ", collectionPath);
  }, []);

  useEffect(() => {
    const state = location.state;
    if (state) {
      setMappingId(state.mappingId);
      //usarlo para invocar un patch al back para actualizar el mapeo
    }
    /*else{//limpiar contexto si es nuevo mapeo
            if(mappings){
              console.log("Se ejecuta clear mappings2222222")
              clearMappings();
            }
                
        }*/
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
        if (mappingId) {
          //invocar put
          console.log("Flujo donde existe mappingId: ", mappingId);
          const body = {
            ontology_id: "",
            name: mappingName,
            mapping: mappings,
            jsonSchema: {},//null because it is not updated in the collection
            mapping_proccess_id: mappingId,
            // documentStoragePath: collectionPath
          };
          const response = await saveMapping(body);
          console.log("Respuesta al editar mapping: ", response);
          if (response) {
            const { status, message, mapping_id } = response.data;
            //navigate('/Result', {state:{mapping_process:mapping_id}});
            if(status === "success"){
              resetMappingState();
              alert(`Process Mapping saved successfully`);
              navigate("/")
            }
            else{
              alert(`Error saving Mapping Process`);
            }
          }
        } else {
          //new mapping
          if (currentOntologyId) {
            const body = {
              ontology_id: currentOntologyId,
              name: mappingName,
              mapping: mappings,
              jsonSchema: jsonSchemaContext,
              mapping_proccess_id: mappingId,
              documentStoragePath: collectionPath
            };
            const response = await saveMapping(body);
            console.log("Response al guardar mappings (save): ", response);
            if (response ) {
              const { status, message, mapping_id } = response.data;
              if (status === "success") {
                //navigate('/Result', {state:{mapping_process:mapping_id}});
                resetMappingState();
                alert("Process Mapping saved successfully");
                navigate("/")
              } else {
                alert("Error saving Mapping Process");
              }
            }
          } else {
            console.error("#ERROR#: No hay ontologyId al editar");
          }
        }
      } else {
        alert("Mappings must not be empty");
      }
    } catch (error) {
      console.error("error en apiCall", error);
    }
  };

  const validateAndSaveMappingsApiCall = async () => {
    try {
      if (Object.keys(mappings).length > 0) {
        if (mappingId) {
          //invocar post con mapping_proccess_id
          console.log("Flujo donde existe mappingId");
          const body = {
            ontology_id: currentOntologyId,
            name: mappingName,
            mapping: mappings,
            jsonSchema: jsonSchemaContext,
            mapping_proccess_id: mappingId,
            // documentStoragePath: collectionPath
          };
          const response = await saveAndValidateMappings(
            currentOntologyId!,
            mappingId,
            body
          );
          //capaz chequear que si currentOntologyId es undefined no se haga el post
          console.log("Respuesta al editar mapping: ", response);
          if (response) {
            const { status, message, mapping_id } = response.data;
            if(status === "success"){
              resetMappingState();
              alert("Mapping procces successfully validated and saved");
              navigate("/");
            }
            else{
              alert("Error validating mapping, please check: " + message);
            }
            //navigate("/Result", { state: { mapping_process: mapping_id } });
          }
        } else {
          //new mapping
          if (currentOntologyId) {
            const jsonschema = jsonSchemaContext;
            const body = {
              name: mappingName,
              mapping: mappings,
              jsonSchema: jsonschema,
              documentStoragePath: collectionPath
            };
            const response = await saveAndValidateMappings(
              currentOntologyId,
              "",
              body
            );
            console.log("Response al guardar mappings (validate): ", response);
            if (response) {
              const { status, message, mapping_id } = response.data;
              if(status === "success"){
                resetMappingState();
                alert("Mapping procces successfully validated and saved");
                navigate("/");
              }
              else{
                alert("Error validating mapping, please check: " + message);
              }
            }
          } else {
            console.log("No hay ontologyId");
          }
        }
      } else {
        alert("Mappings must not be empty");
      }
    } catch (error) {
      console.error("error en apiCall", error);
    }
  };

  useEffect(() => {
    const state = location.state;
    if (state) {
      setMappingId(state.mappingId);
      //usarlo para invocar un patch al back para actualizar el mapeo
    } else {
      //limpiar contexto si es nuevo mapeo
      if (mappings) {
        console.log("JsonSchemaContext: ", jsonSchemaContext);
        console.log("OntologyDataContext: ", ontologyDataContext);
        console.log("Se ejecuta clearMappings");
        //clearMappings();
      }
    }
  }, []);

  useEffect(() => {
    const getMappingData = async () => {
      if (mappingId) {
        try {
          const response = await getMapping(mappingId);
          console.log("Response de getMapping: ", response);
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
          <div className="mapping-name">
            <label>Mapping Process Name</label>
            <input
              type="text"
              value={mappingName}
              onChange={(e) => setMappingName(e.target.value)}
            ></input>
          </div>
          <div className="content-container">
            <div className="content-box">
              <Json></Json>
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
                    Clean mappings
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
                  <button
                    className="button success"
                    onClick={saveMappingsApiCall}
                  >
                    Save
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
