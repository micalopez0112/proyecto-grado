import React, { useEffect, useState } from "react";
import Json from "../components/JsonSchema.tsx";
import OntologyData from "../components/OntologyData.tsx";
import { useNavigate, useLocation } from "react-router-dom";
import { useDataContext } from "../context/context.tsx";
import {
  saveMappings,
  uploadOntology,
  getMapping,
} from "../services/mapsApi.ts";
import "./Mapping.css";
import { OntologyDataType } from "../types/OntologyData.ts";
import { FaTrash } from "react-icons/fa";
import { FaArrowRightLong } from "react-icons/fa6";

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
  useEffect(() => {
    //cambiar logica cuando se obtenga el id desde el back
  }, []);

  useEffect(() => {
    const state = location.state;
    if (state) {
      setMappingId(state.mappingId);
      //usarlo para invocar un patch al back para actualizar el mapeo
    } else {
      //limpiar contexto si es nuevo mapeo
      if (mappings) 
      {
        console.log("JsonSchemaContext: ", jsonSchemaContext);
        console.log("OntologyDataContext: ", ontologyDataContext);
        console.log("Se ejecuta clearMappings")
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

  const saveMappingsApiCall = async () => {
    try {
      if (Object.keys(mappings).length > 0) {
        if (currentOntologyId) {
          console.log("JSON SCHEMAAA: ", jsonSchemaContext);
          const jsonschema = jsonSchemaContext;
          const body = {
            mapping_name: mappingName,
            mapping: mappings,
            jsonSchema: jsonschema,
          };
          const response = await saveMappings(currentOntologyId, body);
          console.log("Response al guardar mappings: ", response);
          if (response && response.status === 200) {
            console.log(response.data);
            alert("Mappings enviados con exito");
            const { status, message, mapping_id } = response.data;
            navigate("/Result", { state: { mapping_process: mapping_id } });
          }
        } else {
          console.log("No hay ontologyId");
        }
      } else {
        alert("No hay mappings para enviar");
      }
    } catch (error) {
      console.error("error en apiCall", error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const fileExtension = files[0].name.split(".").pop()?.toLowerCase();
      if (fileExtension === "owl" || fileExtension === "rdf") {
        setSelectedFile(files[0]);
      } else {
        alert("El archivo debe ser de tipo .owl o .rdf");
        //capaz se puede hacer un toast o un div que muestre error dependiendo de un
        //useState que se setea en true si el archivo no es valido
        return;
      }
    }
  };
  const handleFileSubmit = async () => {
    if (selectedFile) {
      try {
        const response = await uploadOntology("FILE", selectedFile, "");
        console.log("Ontologia desde el back", response);
        const ontologyData: OntologyDataType = response?.data.ontologyData;
        const ontologyId = response?.data.ontologyData.ontology_id;
        setcurrentOntologyId(ontologyId);
        setontologyDataContext(ontologyData);
      } catch (error) {
        console.error("error en handleFileSubmit");
      }
    }
  };

  return (
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
            <div className="mappings">
              {Object.keys(mappings).map((key) => {
                return (
                  <div className="mapping">
                    <ul className="list-container">
                      {mappings[key].map((element, index) => (
                        <li key={index} className="list-elem">
                          <div className="mapping-container">
                            <div className="value-wrapper">
                              <div className="key-title">JSON schema value</div>
                              <div className="key-text" title={key}>
                                {key}
                              </div>
                            </div>

                            <FaArrowRightLong className="arrow-icon" />
                            <div className="value-wrapper">
                              <div className="element-title">
                                Ontology element
                              </div>
                              <div
                                className="element-name"
                                title={element.name}
                              >
                                {element.name}
                              </div>
                            </div>
                          </div>

                          <button
                            className="trash-icon"
                            style={{ marginLeft: "5px" }}
                            onClick={() =>
                              removeMapping(
                                key,
                                element as { name: string; iri: string }
                              )
                            }
                          >
                            <FaTrash />
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
            <div className="mapping-button-wrapper">
              <button className="button" onClick={saveMappingsApiCall}>
                Validar mappings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
