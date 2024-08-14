import React, {useEffect, useState} from 'react'
import Json from '../components/JsonSchema.tsx'
import OntologyData from '../components/OntologyData.tsx';
import { useNavigate } from "react-router-dom";
import { useDataContext } from '../context/context.tsx';
import {saveMappings,uploadOntology} from '../services/mapsApi.ts'
import './Mapping.css'
import { OntologyDataType } from '../types/OntologyData.ts';

export const Mapping = () => {    
    const navigate = useNavigate();
    const { mappings,clearMappings,addNewMapping,
        currentOntologyId ,setcurrentOntologyId,jsonSchemaContext,
        ontologyDataContext,setontologyDataContext
    } = useDataContext();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [mappingName, setMappingName] = useState<string>('');
    useEffect(() => { //cambiar logica cuando se obtenga el id desde el back
        
    },[]);

    useEffect(() => {
        console.log('ontologyDataContext has changed:', ontologyDataContext);
      }, [ontologyDataContext]);


    const prueba = async () => {
        navigate('/Ontology');
    }

    const saveMappingsApiCall = async () => {
        try{
          if(Object.keys(mappings).length > 0){
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
                    navigate('/Result', {state:{mapping_process:mapping_id}});
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
              console.log("Ontology ID desde el back", ontologyId);
              console.log("Ontology Data desde el back", ontologyData);
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
