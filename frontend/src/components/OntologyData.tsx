import React, { useEffect, useState } from 'react';
import "./OntologyData.css";
import { useDataContext} from '../context/context.tsx';
import { OntologyDataType } from '../types';
import Modal from 'react-modal';

Modal.setAppElement('#root');

const OntologyData: React.FC<{}> = () => {
  const isMapping = true;

  const { OntoElementSelected, setOntoElementSelected, ontologyDataContext } = useDataContext();
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [rangeList, setRangeList] = useState<Array<string>>([]);
  const [selectedRange, setSelectedRange] = useState<Array<string>>([]);


  const handleClickOntoElem = (element: any, type:string) => {
    console.log("Onto element selected",element);
    console.log("Type of element selected",type);
    if (isMapping && type !=='object_property') {
      setOntoElementSelected({type:type, ontoElement: element});
    }
    else if(isMapping && type === 'object_property'){
      console.log("Object Property selected",element);
      console.log("Range of object property",element.range);
      setRangeList([...rangeList, element.range.name]);
      setModalIsOpen(true);
      //agregar boton de aceptar y ahí hacer el setOntoElementSelected para este caso.
    }
  };

  const handleAddElemToRange = (rangeItem: string) => {
    if (selectedRange.includes(rangeItem)) {
      setSelectedRange(selectedRange.filter(selected => selected !== rangeItem));
    } else {
      setSelectedRange([...selectedRange, rangeItem]);
    }
  }

  useEffect(() => {
    console.log("Ontology Data Context: ", ontologyDataContext);
  }, []);



  return (
    <div className='onto-data-display-container'>
      <Modal 
        isOpen={modalIsOpen} 
        onRequestClose={() => setModalIsOpen(false)}
        style={ModalStyles}
        >
        <div style={ModalStyles.modalContent}>
        <label style={{border:'solid 3px black', padding:'2px'}}>Mapeo de rango</label>
          <div style={{marginTop:'10px'}}> 
          <p>Selecciona los elementos del rango que deben ser mapeados:</p>
        <ul style={ModalStyles.listStyle}>
          {rangeList.map((item) => (
            <li 
              key={item} 
              onClick={() => handleAddElemToRange(item)} 
              style={{...ModalStyles.listItemStyle,
                    ...(selectedRange.includes(item)?ModalStyles.selectedItemStyle:{})}}>
              {item}
            </li>
          ))}
        </ul>
          </div>
          <div style={ModalStyles.modalfooter}>
            <button
              onClick={() => setModalIsOpen(false)}>Cerrar</button>
          </div>
          
        </div>
        
        
      </Modal>
      <span className='ontology-title'>Elementos de la ontología: </span>
      {OntoElementSelected.type != undefined ? <strong style={{ fontFamily: 'cursive' }}> An Element is selected {OntoElementSelected.ontoElement.iri}</strong> : null}
      {ontologyDataContext?.ontoData.map((ontology, i) => (
        <div className='onto-container' key={`ontology-${i}`}>
          {ontology?.data?.map((x, i) => (
            <div className='styled-input' key={`data-${i}`}>
              {x?.classes?.length > 0 && (
                <>
                  <span className='text'>Classes:</span>
                  <div className='columns-container'>
                    {x?.classes?.map((c) => (
                      <div
                        className={`column-name-container ${isMapping ? 'is-mapping' : ''}`}
                        onClick={() => handleClickOntoElem(c,"class")}
                        key={c?.iri}
                      >
                        <span className='text'>{c?.name}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
              {x?.object_properties?.length > 0 && (
                <>
                  <span className='text'>Object Properties:</span>
                  <div className='columns-container'>
                    {x?.object_properties?.map((objectProperty) => (
                      <div
                        className={`column-name-container ${isMapping ? 'is-mapping' : ''}`}
                        onClick={() => handleClickOntoElem(objectProperty,"object_property")}
                        key={objectProperty?.iri}
                      >
                        <span className='text'>{objectProperty?.name}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
              {x?.data_properties?.length > 0 && (
                <>
                  <span className='text'>Data Properties:</span>
                  <div className='columns-container'>
                    {x?.data_properties?.map((dataProperty) => (
                      <div
                        className={`column-name-container ${isMapping ? 'is-mapping' : ''}`}
                        onClick={() => handleClickOntoElem(dataProperty,"data_property")}
                        key={dataProperty?.iri}
                      >
                        <span className='text'>{dataProperty?.name}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

const ModalStyles: { [key: string]: React.CSSProperties } = {
  content: {
    top: '30%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)',
  },
  modalContent:{
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    width: '220px', 
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '4px 4px 6px rgba(0, 0, 0, 0.1)',
  },
  listStyle: {
    listStyleType: 'none',
    padding: 0,
  },
  listItemStyle: {
    padding: '10px',
    backgroundColor: '#f0f0f0',
    margin: '5px 0',
    cursor: 'pointer',
  },
  selectedItemStyle: {
    backgroundColor: '#007BFF',
    color: 'white',
    fontWeight: 'bold',
  },
  modalfooter:{
    marginTop: '20px',
    display: 'flex',
    justifyContent: 'flex-end',
    width: '100%',
  },
  modalcontainer:{

  },
 
}

export default OntologyData;