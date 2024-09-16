import React, { useEffect, useState } from "react";
import Json from "../components/JsonSchema.tsx";
import OntologyData from "../components/OntologyData.tsx";
import { useNavigate, useLocation } from "react-router-dom";
import { useDataContext } from "../context/context.tsx";
import {
  saveMappings,
  uploadOntology,
  getMapping,
  editMapping
} from "../services/mapsApi.ts";
import "./Mapping.css";
import { OntologyDataType } from "../types/OntologyData.ts";
import { FaTrash } from "react-icons/fa";
import { FaArrowRightLong } from "react-icons/fa6";
import MappingList from "../components/MappingList.tsx";
import { Spinner } from "../components/Spinner/Spinner.tsx";

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
  } = useDataContext();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [mappingName, setMappingName] = useState<string>("");
  const [mappingId, setMappingId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    //cambiar logica cuando se obtenga el id desde el back
  }, []);

    useEffect(() => {
        const state = location.state;
        if(state){
            setMappingId(state.mappingId);
            //usarlo para invocar un patch al back para actualizar el mapeo
        }
        /*else{//limpiar contexto si es nuevo mapeo
            if(mappings){
              console.log("Se ejecuta clear mappings2222222")
              clearMappings();
            }
                
        }*/
    },[]);

    useEffect(() => {
        const getMappingData = async () => {
            if(mappingId){
              setLoading(true);
                try{
                    const response = await getMapping(mappingId);
                    console.log("Response de getMapping: ", response);
                    if(response){
                        const {mapping_name,mapping,schema,ontology} = response.data;
                        setMappings(mapping);
                        setJsonSchemaContext(schema);
                        setcurrentOntologyId(ontology.ontology_id);
                        setontologyDataContext(ontology);
                        setMappingName(mapping_name);
                    }
                }
                catch(error){
                    console.error("error en getMappingData", error);
                }
                setLoading(false);
            }
        }
        getMappingData();
    },[mappingId]);

    const saveMappingsApiCall = async () => {
        try{
          if(Object.keys(mappings).length > 0){
            if(mappingId){
              //invocar put
              console.log("Flujo donde existe mappingId");
              const body = { name:mappingName,mapping: mappings, jsonSchema: jsonSchemaContext };
              const response = await editMapping(mappingId,body);
              console.log("Respuesta al editar mapping: ", response);
              if(response ){
                  const {status,message,mapping_id} = response.data;
                  navigate('/Result', {state:{mapping_process:mapping_id}});
              }
            }
            else{//new mapping
              if(currentOntologyId){
                console.log("Flujo donde no existe mappingId");
                console.log("JSON SCHEMAAA: ", jsonSchemaContext);
                const jsonschema = jsonSchemaContext;
                const body = { name:mappingName,mapping: mappings, jsonSchema: jsonschema };
                const response = await saveMappings(currentOntologyId,body);
                console.log("Response al guardar mappings: ", response);
                if(response && response.status===200 ){
                    console.log(response.data);
                    alert('Mappings enviados con exito');
                    const {status,message,mapping_id} = response.data;
                    if(mapping_id){
                       navigate('/Result', {state:{mapping_process:mapping_id}});
                    }
                    else{
                        alert('No se pudo obtener el id del mapeo');
                    }
                }
            }else{
                console.log("No hay ontologyId");
            }
          }
          }
          else{
            alert('No hay mappings para enviar');
          }
        }
        catch(error){
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
    {loading?<Spinner/>
    :
    <div className="App">
      <div className="mapping-name">
        <label>Nombre del mapeo</label>
        <input
          type="text"
          value={mappingName}
          onChange={(e) => setMappingName(e.target.value)}
        ></input>
      </div>
      {/* <input
        className="file-upload-label"
        type="file"
        onChange={handleFileChange}
      ></input>
      <button className="button" onClick={handleFileSubmit}>
        Submit archivo
      </button> */}
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
                Agregar mapping
              </button>
              <button className="button" onClick={clearMappings}>
                Limpiar mappings
              </button>
            </div>
            <MappingList isResult={false} />
            <div className="mapping-button-wrapper">
              <button className="button success" onClick={saveMappingsApiCall}>
                Validar mappings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    }
    </>
  );
};
