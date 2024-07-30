import { apiClient } from "../networking/apiClient.ts";

export const saveMappings = async (processId: number, data: any) => {
  try {
    const response = await apiClient.post(`/mapping/${processId}`, data);
    console.log(response);
    return response;
  } catch (error) {
    console.error("Error in saving mappings");
  }
};
