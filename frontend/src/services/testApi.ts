import { apiClient } from "../networking/apiClient.ts";
import { useDataContext } from "../context/context.tsx";

export const saveMappings = async (processId: number, data: any) => {
  try {
    const body = { mapping: data };
    console.log("Data to send in saveMappings: ", body);
    const response = await apiClient.post(`/mapping/${processId}`, body, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    console.log("#Se enviaron los mappings al back#: ", response);
    return response;
  } catch (error) {
    console.error("Error in Saving mappings: ", error);
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
