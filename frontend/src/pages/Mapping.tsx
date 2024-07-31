import React, {useState} from 'react'
import Json from '../components/JsonSchema.tsx'
import OntologyData from '../components/OntologyData.tsx';
import { useNavigate } from "react-router-dom";
import { useDataContext } from '../context/context.tsx';
import {saveMappings,uploadOntology} from '../services/testApi.ts'
import './Mapping.css'

export const Mapping = () => {

    const mappingExample = {
        mapping : {
            key1:"value1",
            key2:"value2",
            key3:["list","of","values"]
        }
    };

    const apiCall = async () => {
        try{
            const response = await saveMappings(55,mappingExample);
            console.log(response);
        }
        catch(error){
            console.error("error en apiCall");
        }
    }
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const navigate = useNavigate();

    const handleClick = () => {
        navigate('./Ontology');
    }

    const { mappings,addNewMapping,clearMappings } = useDataContext();

    const handleFileChange = (e:React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if(files){
            setSelectedFile(files[0]);
        }
    }
    const handleFileSubmit = () => {
        if(selectedFile){
            try{
                uploadOntology(55,selectedFile);
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
                <OntologyData></OntologyData>
            </div>  
        </div>
        <div>
            <h1>Mappings</h1>
            <div style ={{display:'flex',gap:'10px', backgroundColor:'#f9f9f9',padding: '20px'}}>
                <button onClick={addNewMapping}>Agregar mapping</button>
                <button onClick={clearMappings}>Limpiar mappings</button>
                <button onClick={apiCall}>Enviar mappings</button>
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