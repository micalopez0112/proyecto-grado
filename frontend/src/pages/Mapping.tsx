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
    const { mappings,clearMappings,addNewMapping,currentMappingProcessId ,setCurrentMappingProcessId} = useDataContext();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [ontologySelected, setOntologySelected] = useState<OntologyDataType['ontoData']>([]);

    useEffect(() => { //cambiar logica cuando se obtenga el id desde el back
        if(currentMappingProcessId === undefined){
            setCurrentMappingProcessId(11);
        }
    },[]);

    const saveMappingsApiCall = async () => {
        try{
          if(Object.keys(mappings).length > 0){
            const response = await saveMappings(55,mappings);
            console.log(response);
            if(response && response.status===200 ){
                console.log(response.data);
                alert('Mappings enviados con exito');
                const {status,message} = response.data;
                navigate('/Result');
            }
            //setMappings({});
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
              const response = await uploadOntology(55, selectedFile);
              console.log("Ontologia desde el back", response);
              const ontologyData: OntologyDataType['ontoData'] = response?.data.ontologyData.ontoData;
  
              console.log("Ontology Data desde el back", ontologyData);
  
              if (Array.isArray(ontologyData)) {//borrar este ifelse
                setOntologySelected(ontologyData);//era para confirmar que se tomaba bien la data
              } else {
                console.error("La data de ontología no es un arreglo.");
              }

              setOntologySelected(ontologyData);
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
                    <OntologyData ontoData = {ontologySelected}></OntologyData>
                </div>
        </div>
        <div>
            <h1>Mappings</h1>
            <div style ={{display:'flex',gap:'10px', backgroundColor:'#f9f9f9',padding: '20px'}}>
                <button onClick={addNewMapping}>Agregar mapping</button>
                <button onClick={clearMappings}>Limpiar mappings</button>
                <button onClick={saveMappingsApiCall}>Enviar mappings al back</button>
                <input className='file-upload-label' type='file' onChange={handleFileChange}></input>
                <button onClick={handleFileSubmit}>Submit archivo</button>
            </div>
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
        </div>
    </div>
    )
}