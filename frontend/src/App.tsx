import React from "react";
import "./App.css";
import Json from "./components/JsonSchema.tsx";
import OntologyData from "./components/OntologyData.tsx";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useNavigate,
  Outlet,
} from "react-router-dom";
import {Mapping} from './pages/Mapping.tsx';
import MappingResult from "./pages/MappingResult.tsx";
import HomeScreen from "./pages/HomeScreen.tsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element = {<HomeScreen/>} />
        <Route path="/Mappings" element={<Mapping />} />
        <Route path="/Ontology" element={<OntologyData />} />
        <Route path="/Result" element={<MappingResult />} />
      </Routes>
    </Router>
  );
}

export default App;
