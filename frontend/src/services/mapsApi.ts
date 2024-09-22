import { apiClient } from "../networking/apiClient.ts";

export const saveAndValidateMappings = async (
  ontologyId: string,
  mapping_pid: string,
  data: any
) => {
  try {
    const body = data;
    const response = await apiClient.post(
      `/mapping/ontology_id/${ontologyId}`,
      body,
      {
        headers: {
          "Content-Type": "application/json",
        },
        params: {
          mapping_proccess_id: mapping_pid,
        },
      }
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

export const getJsonSchema = async (jsonFile: any /*JsonFile?? */) => {
  //este método va a tener que recibir un File en un futuro
  try {
    const body = {
      jsonInstances: jsonFile,
    };
    const response = await apiClient.post("/mapping/generate-schema/", body);
    return response;
  } catch (error) {
    console.error("Error fetching JsonSchema", error);
  }
};
