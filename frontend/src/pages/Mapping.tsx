import React, {useState} from 'react'
import Json from '../components/JsonSchema.tsx'
import OntologyData from '../components/OntologyData.tsx';
import { useNavigate } from "react-router-dom";
import { useDataContext } from '../context/context.tsx';
import {saveMappings,uploadOntology} from '../services/testApi.ts'
import './Mapping.css'
import { OntologyDataType } from '../types/OntologyData.ts';

export const Mapping = () => {    
    const navigate = useNavigate();
    const { mappings,addNewMapping,clearMappings } = useDataContext();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [ontologySelected, setOntologySelected] = useState<OntologyDataType['ontoData']>([]);

    const data = [
        {
          name: "Ontology 1",
          data: [
            {
              classes: [
                {
                  name: "Class 1",
                  iri: "http://example.com/class1",
                },
                {
                  name: "Class 2",
                  iri: "http://example.com/class2",
                },
              ],
              object_properties: [
                {
                  name: "Object Property 1",
                  iri: "http://example.com/objectproperty1",
                },
                {
                  name: "Object Property 2",
                  iri: "http://example.com/objectproperty2",
                },
              ],
              data_properties: [
                {
                  name: "Data Property 1",
                  iri: "http://example.com/dataproperty1",
                },
                {
                  name: "Data Property 2",
                  iri: "http://example.com/dataproperty2",
                },
              ],
            },
          ],
        },
        {
          name: "Ontology 2",
          data: [
            {
              classes: [
                {
                  name: "Class 3",
                  iri: "http://example.com/class3",
                },
                {
                  name: "Class 4",
                  iri: "http://example.com/class4",
                },
              ],
              object_properties: [
                {
                  name: "Object Property 3",
                  iri: "http://example.com/objectproperty3",
                },
                {
                  name: "Object Property 4",
                  iri: "http://example.com/objectproperty4",
                },
              ],
              data_properties: [
                {
                  name: "Data Property 3",
                  iri: "http://example.com/dataproperty3",
                },
                {
                  name: "Data Property 4",
                  iri: "http://example.com/dataproperty4",
                },
              ],
            },
          ],
        },
      ];
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
    

    const handleFileChange = (e:React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if(files){
            setSelectedFile(files[0]);
        }
    }
    const handleFileSubmit = () => {
        /*
        if(selectedFile){
            try{
                const responseOntology = uploadOntology(55,selectedFile);
            }
            catch(error){
                console.error("error en handleFileSubmit");
            }   
        }*/
        setOntologySelected(data);
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