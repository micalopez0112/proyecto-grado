import { apiClient } from "../networking/apiClient.ts";

export const saveMappings = async (ontologyId: string, data: any) => {
  try {
    const body = data;
    console.log("Data to send in saveMappings: ", body);
    const response = await apiClient.post(
      `/mapping/ontology_id/${ontologyId}`,
      body,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    console.log("#Se enviaron los mappings al back#: ", response);
    return response;
  } catch (error) {
    console.error("Error in Saving mappings: ", error);
  }
};

export const uploadOntology = async (type: string, file: File, uri: string) => {
  try {
    const formData = new FormData();
    formData.append("type", type);
    formData.append("ontology_file", file);
    if (uri) formData.append("uri", uri);
    const response = await apiClient.post(`/ontologies/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response;
  } catch (error) {
    console.error("Error in uploading ontology");
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

export const fetchMappings = async () => {
  try {
    const response = await apiClient.get("/mapping/");
    return response;
  } catch (error) {
    console.error("Error fetching mappings", error);
  }
};

export const getMapping = async (mappingId: string) => {
  try {
    const response = await apiClient.get(`/mapping/${mappingId}`);
    return response;
  } catch (error) {
    console.error(`Error getting mapping with id ${mappingId}: `, error);
  }
};

export const editMapping = async (mappingId: string, data: any) => {
  try {
    const response = await apiClient.put(`/mapping/${mappingId}`, data);
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
