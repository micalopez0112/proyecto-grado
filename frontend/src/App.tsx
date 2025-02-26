import React from "react";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import HomeScreen from "./pages/home/HomeScreen.tsx";
import DataQualityScreen from "./pages/data-quality/data-quality-screen/DataQualityScreen.tsx";
import OntologySelectScreen from "./pages/mappings/OntologySelect.tsx";
import MappingsScreen from "./pages/mappings/MappingsScreen.tsx";
import { Mapping } from "./pages/mappings/Mapping.tsx";
import SchemaSelect from "./pages/mappings/SchemaSelect.tsx";
import SelectMappingsValidate from "./pages/data-quality/select-mappings-evaluate/SelectMappingsEvaluate.tsx";
import OntologyData from "./components/OntologyData.tsx";
import Navbar from "./components/Navbar/Navbar.tsx";
import EvaluateMappings from "./pages/data-quality/evaluate-mappings/EvaluateMappings.tsx";
import DatasetsScreen from "./pages/data-quality/datasets-screen/DatasetsScreen.tsx";
import DQModelsScreen from "./pages/data-quality/dq-models/DQModelsScreen.tsx";
import ProtectedRoute from "./components/ProtectedRoute/ProtectedRouteComponent.tsx";
import UnauthorizedPage from "./components/ProtectedRoute/Unauthorized.tsx";

function App() {
  return (
    <>
      <ToastContainer position="top-right" autoClose={3000} />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/Unauthorized" element={<UnauthorizedPage />} />

          <Route
            path="/"
            element={<ProtectedRoute fallbackRoute="/Unauthorized" />}
          >
            <Route path="" element={<HomeScreen />} />
          </Route>

          <Route path="/MappingsScreen" element={<MappingsScreen />} />
          <Route
            path="/DataQualityScreen/:idDataset"
            element={<DataQualityScreen />}
          />
          <Route
            path="/OntologySelect/:collection_name?"
            element={<OntologySelectScreen />}
          />
          <Route path="/SchemaSelect" element={<SchemaSelect />} />
          <Route path="/Mapping" element={<Mapping />} />
          <Route path="/Ontology" element={<OntologyData />} />
          <Route path="/DatasetsScreen" element={<DatasetsScreen />} />
          <Route
            path="/SelectMappingsValidate"
            element={<SelectMappingsValidate />}
          />
          <Route path="/EvaluateMappings" element={<EvaluateMappings />} />
          <Route path="/DQModelsScreen" element={<DQModelsScreen />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
