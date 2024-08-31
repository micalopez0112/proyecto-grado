import React,{useEffect,useState, useRef} from 'react'
import {useDataContext} from '../context/context.tsx';
import { fetchOntologies,uploadOntology } from '../services/mapsApi.ts';
import OntologyCard from '../components/OntologyCard.tsx';
import { OntologyDataType } from "../types/OntologyData.ts";
import { useNavigate } from 'react-router-dom';

const OntologySelectScreen = () =>{

    const [ontologies,setOntologies] = useState<Array<{id:string,type:string,file:string,uri:string}>> ([]);
    const {ontologyDataContext,setontologyDataContext,setcurrentOntologyId} = useDataContext();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [idSelectedOnto,setIdSelectedOnto] = useState<string>('');
    const [nextScreen,setNextScreen] = useState<boolean>(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const navigate = useNavigate();

    useEffect (()=>{
        const retrieveOntologies = async () =>{
            const ontologies = await fetchOntologies();
            if(ontologies){
                console.log("Ontologies: ",ontologies);
                setOntologies(ontologies.data);
            }
        }
        retrieveOntologies();
    },[])

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files) {
          const fileExtension = files[0].name.split(".").pop()?.toLowerCase();
          if (fileExtension === "owl" || fileExtension === "rdf") {
            setSelectedFile(files[0]);
            setNextScreen(true);
          } else {
            alert("El archivo debe ser de tipo .owl o .rdf");
            return;
          }
        }
      };

      const handleSubmit = async () =>{
        console.log("a")
        try{
            if(selectedFile || (idSelectedOnto !== '')){
            if (selectedFile) {
                  const response = await uploadOntology("FILE", selectedFile, "");
                  console.log("Ontologia desde el back", response);
                  const ontologyData: OntologyDataType = response?.data.ontologyData;
                  const ontologyId = response?.data.ontologyData.ontology_id;
                  setcurrentOntologyId(ontologyId);
                  setontologyDataContext(ontologyData);
              }
              else{
                //get ontology data from backend
                setcurrentOntologyId(idSelectedOnto);
              }
              navigate('/SchemaSelect');
            }
            else{
                alert("Debe seleccionar una ontología");
            }
        }
        catch(error){
            console.log("error en handleSubmit: ", error);
        }
      }

      const handleSelectOntology = (id:string) =>{
        setSelectedFile(null);
        if(fileInputRef.current)
            fileInputRef.current.value = '';
        setIdSelectedOnto(id);
      }

    return (
        <div style={styles.container}>
            <h1>Seleccione la ontología de contexto</h1>
            <button className='button' onClick={handleSubmit}>Confirmar selección</button>
            <div style ={styles.selectHeader}>
                <p style={{display:'flex',alignItems:'flex-start', fontSize:'16px'}}>Se puede cargar la ontología:</p>
                <input style={{display:'flex',alignSelf:'center', fontSize:'16px'}} 
                    type='file' onChange={handleFileChange} ref={fileInputRef}>
                </input>
            </div>
            {ontologies &&
            <div>
                <p style={{fontSize:'16px'}}>
                O se puede seleccionar una de las siguientes ontologías:
                </p>
                <div style={styles.dashboard}>
                    {ontologies.map(ontology =>{
                        return(
                            <OntologyCard
                            id={ontology.id}
                            name={ontology.file}
                            style={styles.ontologyCard}
                            onClickCallback={()=>handleSelectOntology(ontology.id)}
                                />
                        )
                    })}
                </div>
            </div>
            }
        </div>
        
    );
}

const styles: { [key: string]: React.CSSProperties } = {
    container: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '20px',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh',
    },
    selectHeader:{
        display:'flex',
        flexDirection:'column',
        padding:'10px',
        width:'800px',
        
    },
    title: {
      fontSize: '2em',
      color: '#000',
      marginBottom: '20px',
    },
    button: {
      padding: '10px 20px',
      fontSize: '1em',
      color: '#fff',
      backgroundColor: '#000',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
      marginBottom: '20px',
    },
    dashboard: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
      gap: '10px',
      width: '100%',
      maxWidth: '800px',
      marginTop: '10px',
      maxHeight:'1000px',
      overflowY:'scroll'
    },
    ontologyCard: {
      backgroundColor: '#fff',
      padding: '15px',
      borderRadius: '5px',
      boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)',
      color: '#000',
      cursor: 'pointer',
      transition: 'background-color 0.3s ease', 
      wordBreak:'break-word'
    }
  };
  

export default OntologySelectScreen;