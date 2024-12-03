import { apiClient } from "../networking/apiClient.ts";

export const saveAndValidateMappings = async (
  ontologyId: string,
  mapping_pid: string,
  data: any
) => {
  try {
    const body = data;
    let options = {
      headers: {
        "Content-Type": "application/json",
      },
      params: {
        mapping_proccess_id: mapping_pid,
      },
    };
    // if (mapping_pid !== "") {
    //   options = {
    //     headers: {
    //       "Content-Type": "application/json",
    //     },
    //     params: {
    //       mapping_proccess_id: mapping_pid,
    //     },
    //   };
    // } else {
    //   options = {
    //     headers: {
    //       "Content-Type": "application/json",
    //     },
    //   };
    // }

    const response = await apiClient.post(
      `/mapping/ontology_id/${ontologyId}`,
      body,
      options
    );
    console.log("#Se enviaron los mappings al back#: ", response);
    return response;
  } catch (error) {
    console.error("Error in Saving mappings: ", error);
  }
};

export const uploadOntology = async (
  type: string,
  file?: File,
  uri?: string
) => {
  try {
    const formData = new FormData();
    formData.append("type", type);

    if (file) {
      formData.append("ontology_file", file);
    }

    if (uri) {
      formData.append("uri", uri);
    }

    const response = await apiClient.post(`/ontologies/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response;
  } catch (error) {
    console.error("Error in uploading ontology", error);
    throw error; // Recomendable lanzar el error para manejarlo fuera
  }
};

export const getMappingGraph = async (processId: string) => {
  try {
    const response = await apiClient.get(`/mapping/graph/${processId}`);
    console.log("Mapping Graph: ", response);
    return response;
  } catch (error) {
    console.error("Error in getting Mapping Graph");
  }
};

export const getOntologyGraph = async (ontologyId: string) => {
  try {
    const response = await apiClient.get(
      `/ontologies/ontology-graph/${ontologyId}`
    );
    return response;
  } catch (error) {
    console.error("Error in getting Ontology Graph");
  }
};

export const fetchMappings = async (filter_validated_mappings?: boolean) => {
  try {
    let params = {};
    if (filter_validated_mappings) {
      params = {
        validated_mappings: filter_validated_mappings,
      };
    }
    const response = await apiClient.get("/mapping/", { params });
    return response;
  } catch (error) {
    console.error("Error fetching mappings", error);
  }
};

export const getDatasetMappings = async (datasetId: string) => {
  try {
    const response = await apiClient.get(`/mapping/schemas/${datasetId}`);
    return response;
  } catch (error) {
    console.log("Error fetching mappings for dataset: ", error);
  }
};

export const getMapping = async (mappingId: string, filter_dp?: boolean) => {
  try {
    let params = {};
    if (filter_dp) {
      params = {
        filter_dp: filter_dp,
      };
    }
    const response = await apiClient.get(`/mapping/${mappingId}`, { params });
    return response;
  } catch (error) {
    console.error(`Error getting mapping with id ${mappingId}: `, error);
  }
};

export const deleteMapping = async (mappingId: string) => {
  try {
    const response = await apiClient.delete(`/mapping/${mappingId}`);
    return response;
  } catch (error) {
    console.error(`Error getting mapping with id ${mappingId}: `, error);
  }
};

export const saveMapping = async (data: any) => {
  try {
    //Tal vez agregar mapping_id como query parameter por prolijidad
    console.log("Se manda en el put: ", data);
    const response = await apiClient.put(`/mapping/`, data);
    //console.log("Response from editing mapping: ", response);
    return response;
  } catch (error) {
    console.error("Error in call of editing mapping: ", error);
  }
};

export const fetchOntologies = async () => {
  try {
    const response = await apiClient.get("/ontologies");
    return response;
  } catch (error) {
    console.error("Error fetching ontologies", error);
  }
};

export const fetchDatasets = async () => {
  try {
    const response = await apiClient.get("/schemas");
    return response;
  } catch (error) {
    console.error("Error fetching ontologies", error);
  }
};

export const getJsonSchema = async (jsonFilePath: string /*JsonFile?? */) => {
  try {
    const queryParam = `?collectionPath=${jsonFilePath}`;
    const response = await apiClient.get(
      `/schemas/generateSchema${queryParam}`
    );
    console.log("Response from generating schema: ", response);
    return response;
  } catch (error) {
    //handle error al no poder levantar el schema
    console.error("Error fetching JsonSchema", error);
    throw error;
  }
};

export const evaluateMapping = async (
  qualityRuleId: string,
  mapping_pid: string | null,
  body: any
) => {
  try {
    const query = mapping_pid ? `?mapping_process_id=${mapping_pid}` : "";

    const response = await apiClient.post(
      `/data-quality/evaluate/${qualityRuleId}${query}`,
      body
    );

    return response;
  } catch (error) {
    console.error("Error in call of evaluating mapping: ", error);
  }
};

export const fetchDetailedEvaluationResults = async (
  mappingProcessId: string,
  mappingName: string
) => {
  if (!mappingProcessId) {
    throw new Error("Mapping process ID is not available.");
  }

  try {
    const response = await apiClient.get("/data-quality/results", {
      params: {
        mapping_process_id: mappingProcessId,
        json_key: mappingName,
      },
    });

    if (response.data?.status === "error") {
      throw new Error(response.data.message);
    }

    return response.data;
  } catch (error) {
    console.error("Error fetching detailed results:", error);
    throw new Error("Failed to fetch detailed results.");
  }
};
