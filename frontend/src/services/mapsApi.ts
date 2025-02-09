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
  aggregation: string,
  dqModelId: string | null,
  body: any
) => {
  try {
    const query = new URLSearchParams({
      aggregation,
      ...(dqModelId ? { dq_model_id: dqModelId } : {}),
    }).toString();

    const response = await apiClient.post(
      `/data-quality/evaluate/${qualityRuleId}?${query}`,
      body
    );

    return response;
  } catch (error) {
    console.error("Error in call of evaluating mapping: ", error);
    throw error;
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

export const getDQModels = async (
  mappingProcessId: string,
  qualityRuleId: string
) => {
  const response = await apiClient.get("/data-quality/models", {
    params: {
      mapping_process_id: mappingProcessId,
      quality_method_id: qualityRuleId,
    },
  });
  return response;
};

export const createDQModel = async (
  mappingProcessId: string | null,
  dqModelName: string,
  dqAggregatedMethodId: string,
  dqMethodId: string,
  body: any
) => {
  console.log(
    "API call to create DQ model with dqMethodId: " +
      dqMethodId +
      " and dqAggregatedMethodId: " +
      dqAggregatedMethodId
  );
  const params = mappingProcessId
    ? {
        mapping_process_id: mappingProcessId,
        dq_model_name: dqModelName,
        dq_aggregated_method_id: dqAggregatedMethodId, //"D1F1M2MD1",
        dq_method_id: dqMethodId, // "D1F1M1MD1",
      }
    : {};
  return await apiClient.post("/data-quality/model", body, {
    params,
  });
};

export const connectNeo4jDB = async (
  uri: string,
  user: string,
  password: string
) => {
  try {
    console.log("Connecting to Neo4j database");
    console.log("URI: ", uri);
    console.log("User: ", user);
    console.log("Password: ", password);
    const response = await apiClient.post(
      "/data-quality/update-neo4j-connection",
      {
        uri,
        user,
        password,
      }
    );
    return response;
  } catch (error) {
    console.error("Error connecting to Neo4j database", error);
  }
};

export const getAppliedMethods = async (dqModelId: string) => {
  try {
    const response = await apiClient.get(`/data-quality/applied_methods`, {
      params: { dq_model_id: dqModelId },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching applied methods:", error);
    throw error;
  }
};
