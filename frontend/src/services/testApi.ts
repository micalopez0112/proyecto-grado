import { apiClient } from "../networking/apiClient.ts";

export const saveMappings = async (processId: number, data: any) => {
  try {
    const response = await apiClient.post(`/mapping/${processId}`, data, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    console.log(response);
    return response;
  } catch (error) {
    console.error("Error in Saving mappings");
  }
};

export const uploadOntology = async (processId: number, file: File) => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post(
      `/ontologies/${processId}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    console.log(response);
    return response;
  } catch (error) {
    console.error("Error in uploading ontology");
  }
};
