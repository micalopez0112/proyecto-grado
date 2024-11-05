import React, { useState } from "react";
import "./OntologyData.css";
import { useDataContext } from "../context/context.tsx";
import { OntoElement } from "../context/context.tsx";
import Modal from "react-modal";
import { IoRemoveOutline } from "react-icons/io5";
import { getOntologyGraph } from "../services/mapsApi.ts";
import Graph from "react-graph-vis";
import { v4 as uuidv4 } from "uuid";
import { Spinner } from "./Spinner/Spinner.tsx";

Modal.setAppElement("#root");

const OntologyData: React.FC<{}> = () => {
  const isMapping = true;
  const {
    OntoElementSelected,
    setOntoElementSelected,
    ontologyDataContext,
    currentOntologyId,
  } = useDataContext();
  const [ontoModalIsOpen, setOntoModalIsOpen] = useState(false);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [rangeList, setRangeList] = useState<Array<OntoElement>>([]);
  const [selectedRange, setSelectedRange] = useState<Array<OntoElement>>([]);
  const [objectPropertyElement, setObjectPropertyElement] = useState<any>();
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const graph = graphData
    ? {
        nodes: graphData.nodes,
        edges: graphData.edges,
      }
    : null;

  const options = {
    edges: {
      color: "#000000",
      arrows: {
        to: false,
      },
      font: {
        face: "RobotoBold",
      },
      length: 250,
    },
    nodes: {
      shape: "box",
      color: "rgb(51, 102, 204)",
      margin: 6,
      font: {
        color: "white",
        face: "Roboto",
      },
    },
  };

  const handleClickOntoElem = (element: any, type: string) => {
    if (isMapping && type !== "object_property") {
      setOntoElementSelected({ type: type, ontoElement: element });
    } else if (isMapping && type === "object_property") {
      const OntoElementToSelect = {
        type: type,
        ontoElement: {
          name: element.name,
          iri: element.iri,
          range: [],
        },
      };
      console.log("Element selected: ", OntoElementToSelect);
      setOntoElementSelected(OntoElementToSelect);

      // es necesario mapear el rango de la propiedad de objeto

      // if(//chequear si el jsonElementSelected _value está en mapping){

      // }
      // else{
      //   setRangeList([...rangeList, element.range]);
      //   setObjectPropertyElement(element);
      //   setModalIsOpen(true);
      //   }
    }
  };

  const handleAddElemToRange = (rangeItem: OntoElement) => {
    if (rangeItem === undefined) return;
    else {
      if (selectedRange.includes(rangeItem)) {
        setSelectedRange(
          selectedRange.filter((selected) => selected !== rangeItem)
        );
      } else {
        setSelectedRange([...selectedRange, rangeItem]);
      }
    }
  };

  const closeOntoModal = () => {
    setOntoModalIsOpen(false);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setRangeList([]);
    setObjectPropertyElement({});
    setSelectedRange([]);
  };

  const confirmationModal = (objectPropertyElement: any) => {
    setOntoElementSelected({
      type: "object_property",
      ontoElement: {
        name: objectPropertyElement.name,
        iri: objectPropertyElement.iri,
        range: selectedRange,
      },
    });
    setSelectedRange([]);
    setObjectPropertyElement({});
    setRangeList([]);
    setModalIsOpen(false);
  };

  const getGraphData = async () => {
    try {
      setLoading(true);
      if (currentOntologyId && currentOntologyId !== "") {
        const response = await getOntologyGraph(currentOntologyId);
        console.log("Ontology Graph: ", response);
        if (response) setGraphData(response.data);
      }
      setLoading(false);
    } catch (error) {
      console.error("Error en getGraphData (MappingResult)", error);
    }
  };

  const openModal = () => {
    try {
      if (graphData === null) {
        getGraphData();
      }
      setOntoModalIsOpen(true);
    } catch (error) {
      console.error("Error en getGraphData (MappingResult)", error);
    }
  };

  return (
    <div className="container">
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        shouldCloseOnOverlayClick={false}
        style={ModalOPStyles}
      >
        <div style={ModalOPStyles.modalContent}>
          <label style={{ border: "solid 3px black", padding: "2px" }}>
            Mapeo de rango
          </label>
          <div style={{ marginTop: "10px" }}>
            <p>Selecciona los elementos del rango que deben ser mapeados:</p>
            <ul style={ModalOPStyles.listStyle}>
              {rangeList.map((item, i) => (
                <li
                  key={i}
                  onClick={() => handleAddElemToRange(item)}
                  style={{
                    ...ModalOPStyles.listItemStyle,
                    ...(selectedRange.includes(item)
                      ? ModalOPStyles.selectedItemStyle
                      : {}),
                  }}
                >
                  {item.name}
                </li>
              ))}
            </ul>
          </div>
          <div style={ModalOPStyles.modalfooter}>
            <button className="button danger" onClick={closeModal}>
              Cerrar
            </button>
            <button
              className="button success"
              style={ModalOPStyles.modalOkButton}
              onClick={() => confirmationModal(objectPropertyElement)}
            >
              Aceptar
            </button>
          </div>
        </div>
      </Modal>

      {/*OntoModal*/}
      <Modal
        isOpen={ontoModalIsOpen}
        onRequestClose={closeOntoModal}
        shouldCloseOnOverlayClick={false}
        style={ModalOntoStyles}
      >
        <div style={ModalOntoStyles.modalContent}>
          {loading ? (
            <Spinner />
          ) : (
            <>
              <label>Ontología Seleccionada:</label>
              <div style={ModalOntoStyles.graphContainer}>
                {graphData ? (
                  <Graph
                    key={uuidv4()}
                    graph={graph}
                    options={options}
                    events={{}}
                  />
                ) : null}
              </div>
            </>
          )}

          <button className="button" onClick={closeOntoModal}>
            Cerrar
          </button>
        </div>
      </Modal>

      <div className="title-wrapper">
        <h1 className="title">Ontology elements</h1>
        <h1 className="title">Ontology Elements</h1>
      </div>
      {/* {OntoElementSelected.type && (
        <strong style={{ fontFamily: "cursive" }}>
          An Element is selected: {OntoElementSelected.ontoElement.iri}
        </strong>
      )} */}
      {ontologyDataContext?.ontoData.map((ontology, i) => (
        <div className="onto-container" key={`ontology-${i}`}>
          {ontology?.data?.map((x, i) => (
            <div className="styled-input" key={`data-${i}`}>
              {x?.classes?.length > 0 && (
                <div className="ontolo-elems-container">
                  <div className="onto-elem">Classes:</div>
                  <div className="columns-container">
                    {x?.classes?.map((c) => (
                      <div
                        className={`column-name-container ${
                          isMapping ? "is-mapping" : ""
                        } ${
                          OntoElementSelected?.ontoElement?.iri === c?.iri
                            ? "active"
                            : ""
                        }`}
                        onClick={() => handleClickOntoElem(c, "class")}
                        key={c?.iri}
                      >
                        <div className="line">
                          <IoRemoveOutline size={20} />
                        </div>
                        <span className="text">{c?.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {x?.object_properties?.length > 0 && (
                <div className="ontolo-elems-container">
                  <div className="onto-elem">Object Properties:</div>
                  <div className="columns-container">
                    {x?.object_properties?.map((objectProperty, index) => (
                      <div
                        className={`column-name-container ${
                          isMapping ? "is-mapping" : ""
                        } ${
                          OntoElementSelected?.ontoElement?.iri ===
                          objectProperty?.iri
                            ? "active"
                            : ""
                        }`}
                        onClick={() =>
                          handleClickOntoElem(objectProperty, "object_property")
                        }
                        key={`${objectProperty?.iri}-${index}`}
                      >
                        <div className="line">
                          <IoRemoveOutline size={20} />
                        </div>
                        <span className="text">{objectProperty?.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {x?.data_properties?.length > 0 && (
                <div className="ontolo-elems-container">
                  <div className="onto-elem">Data Properties:</div>
                  <div className="columns-container">
                    {x?.data_properties?.map((dataProperty) => (
                      <div
                        className={`column-name-container ${
                          isMapping ? "is-mapping" : ""
                        } ${
                          OntoElementSelected?.ontoElement?.iri ===
                          dataProperty?.iri
                            ? "active"
                            : ""
                        }`}
                        onClick={() =>
                          handleClickOntoElem(dataProperty, "data_property")
                        }
                        key={dataProperty?.iri}
                      >
                        <div className="line">
                          <IoRemoveOutline size={20} />
                        </div>
                        <span className="text">{dataProperty?.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <button
                style={{ fontSize: "16px" }}
                className="button"
                onClick={() => openModal()}
              >
                Visualize Ontology
              </button>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

const ModalOPStyles: { [key: string]: React.CSSProperties } = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
  },
  modalContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    width: "220px",
    padding: "20px",
  },
  listStyle: {
    listStyleType: "none",
    padding: 0,
  },
  listItemStyle: {
    padding: "10px",
    backgroundColor: "#f0f0f0",
    margin: "5px 0",
    cursor: "pointer",
  },
  selectedItemStyle: {
    backgroundColor: "#007BFF",
    color: "white",
    fontWeight: "bold",
  },
  modalfooter: {
    marginTop: "20px",
    display: "flex",
    justifyContent: "flex-end",
    width: "100%",
  },
};
const ModalOntoStyles: { [key: string]: React.CSSProperties } = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
  },
  modalContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    width: "1200px",
    height: "600px",
    padding: "20px",
  },
  graphContainer: {
    border: "solid 2px black",
    borderRadius: "10px",
    marginTop: "20px",
    width: "1000px",
    height: "500px",
    paddingBottom: "30px",
  },
};

export default OntologyData;
