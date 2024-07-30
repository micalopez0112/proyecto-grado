import axios from "axios";
import { API_URLS } from "./apiUrls.ts";

export const apiClient = axios.create({
  baseURL: API_URLS.BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});
