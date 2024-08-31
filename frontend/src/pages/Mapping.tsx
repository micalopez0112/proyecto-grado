import React, {useEffect, useState} from 'react'
import Json from '../components/JsonSchema.tsx'
import OntologyData from '../components/OntologyData.tsx';
import { useNavigate, useLocation } from "react-router-dom";
import { useDataContext } from '../context/context.tsx';
import {saveMappings,uploadOntology,getMapping, editMapping} from '../services/mapsApi.ts'
import './Mapping.css'
import { OntologyDataType } from '../types/OntologyData.ts';

export const Mapping = () => {    
    const navigate = useNavigate();
    const location = useLocation();

    const { mappings,clearMappings,addNewMapping,
        currentOntologyId ,setcurrentOntologyId,jsonSchemaContext,
        ontologyDataContext,setontologyDataContext,setMappings,setJsonSchemaContext,
        removeMapping
    } = useDataContext();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [mappingName, setMappingName] = useState<string>('');
    const [mappingId, setMappingId] = useState<string>('');
    useEffect(() => { //cambiar logica cuando se obtenga el id desde el back
        
    },[]);

    useEffect(() => {
        const state = location.state;
        if(state){
            setMappingId(state.mappingId);
            //usarlo para invocar un patch al back para actualizar el mapeo
        }
        else{//limpiar contexto si es nuevo mapeo
            if(mappings)
                clearMappings();
        }
    },[]);

    useEffect(() => {
        const getMappingData = async () => {
            if(mappingId){
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
            }
        }
        getMappingData();
    },[mappingId]);

    const saveMappingsApiCall = async () => {
        try{
          if(Object.keys(mappings).length > 0){
            if(mappingId){
              //invocar put
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
                console.log("JSON SCHEMAAA: ", jsonSchemaContext);
                const jsonschema = jsonSchemaContext;
                const body = { mapping_name:mappingName,mapping: mappings, jsonSchema: jsonschema };
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
    }
    

    const handleFileChange = (e:React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if(files){
          const fileExtension = files[0].name.split('.').pop()?.toLowerCase();
          if(fileExtension === 'owl' || fileExtension === 'rdf'){
            setSelectedFile(files[0]);
          }
          else{
            alert('El archivo debe ser de tipo .owl o .rdf');
            //capaz se puede hacer un toast o un div que muestre error dependiendo de un
            //useState que se setea en true si el archivo no es valido
            return;
          }
        }
    }
    const handleFileSubmit = async () => {
        if(selectedFile){
            try{
              const response = await uploadOntology('FILE', selectedFile,'');
              console.log("Ontologia desde el back", response);
              const ontologyData: OntologyDataType = response?.data.ontologyData;
              const ontologyId = response?.data.ontologyData.ontology_id;
              setcurrentOntologyId(ontologyId);
              setontologyDataContext(ontologyData);
            }
            catch(error){
                console.error("error en handleFileSubmit");
            }   
        }
    }

    return(
    <div className="App">
        <div className='content-container'>
                <div className='content-box'>
                    <Json></Json>    
                </div>
                <div className='content-box'>
                    <OntologyData />
                </div>
        </div>
        <div 
                style={{display:'flex',gap:'4px'}}>
                    <label>Nombre del mapeo</label>
                    <input type='text' value={mappingName} onChange={(e) => setMappingName(e.target.value)}></input>
                    <button style={{marginBottom:'0px'}} onClick={saveMappingsApiCall}>Validar mappings</button>
                </div>
        <div>
            <h1>Mappings</h1>
            <div style ={{display:'flex',gap:'10px', backgroundColor:'#f9f9f9',padding: '20px'}}>
                <button onClick={addNewMapping}>Agregar mapping</button>
                <button onClick={clearMappings}>Limpiar mappings</button>
                <input className='file-upload-label' type='file' onChange={handleFileChange}></input>
                <button onClick={handleFileSubmit}>Submit archivo</button>
            </div>
            {
                Object.keys(mappings).map((key) => {
                    return (
                        <div>
                            <h2>{key}</h2>
                            <ul>
                                {mappings[key].map((element, index) => (
                                    <li key={index}>
                                        {element.name}
                                        <button
                                            style={{ marginLeft: '5px' }}
                                            onClick={() => 
                                                removeMapping(key, element as { name: string; iri: string })}
                                        >
                                            Eliminar mapping
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )
                })
            }
        </div>
    </div>
    )
    /*
     {
                Object.keys(mappings).map((key) => {
                    return (
                        <div>
                            <h2>{key}</h2>
                            <ul>
                                {
                                    mappings[key].map((element) => {
                                        return <li>{element.name}</li>
                                    })
                                }
                            </ul>
                        </div>
                    )
                })
            }
    */
}
