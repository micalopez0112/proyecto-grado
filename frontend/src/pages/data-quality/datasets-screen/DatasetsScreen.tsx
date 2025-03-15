import React, { useState, useEffect } from "react";
import { useDataContext } from "../../../context/context.tsx";
import { useNavigate } from "react-router-dom";
import { Spinner } from "../../../components/Spinner/Spinner.tsx";
import { fetchDatasets } from "../../../services/mapsApi.ts";
import MappingCard from "../../../components/MappingCard.tsx";

import "./DatasetsScreen.css";
import InfoModal from "../../../components/InfoModal/InfoModal.tsx";
import BackButton from "../../../components/BackButton/BackButton.tsx";

const DatasetsScreen = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [datasets, setDatasets] = useState<
    Array<{ id: string; collection_name: string; properties }>
  >([]);
  const navigate = useNavigate();
  const { externalFlow } = useDataContext();

  useEffect(() => {
    const retrieveDatasets = async () => {
      try {
        setLoading(true);
        // if(externalFlow){
        //     navigate to home with outOfExternalFlow
        // }
        const response = await fetchDatasets();
        if (response?.status === 200) {
          const datasets = response.data;
          // if(!externalFlow){
          //     //Se muestran solo los datasets que no son externalFlow, cambiar?
          //     const datasetsFiltered = datasets.filter((dataset) => dataset.is_external !== true);
          //     datasets = datasetsFiltered;
          // }
          const datasetsFiltered = datasets.filter(
            (dataset) => dataset.is_external !== true
          );
          setDatasets(datasetsFiltered);
          console.log(
            "Datasets (is_external !== true) en DatasetsScreen: ",
            datasetsFiltered
          );
        }
        setLoading(false);
      } catch (error) {
        console.log("Error while loading datasets");
      }
    };
    retrieveDatasets();
  }, []);

  const selectDataset = (id: string) => {
    navigate(`/DataQualityScreen/${id}`);
  };

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <>
          <div className="container">
            <div className="title-info">
              <BackButton />
              <h1 className="title-section">Loaded Datasets</h1>
              <InfoModal
                text={
                  "On this screen, you can select a dataset to evaluate the quality of its attributes. The datasets listed here are those uploaded in the mapping section of the application."
                }
              />
            </div>
            <p className="subtitle">
              Select a dataset to evaluate the quality of its attributes
            </p>
            <div className="dataset-list-container">
              {datasets.map((dataset) => (
                <MappingCard
                  key={dataset.id}
                  id={dataset.id}
                  name={dataset.collection_name}
                  onClickCallback={() => selectDataset(dataset.id)}
                />
              ))}
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default DatasetsScreen;
