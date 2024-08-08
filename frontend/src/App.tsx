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
import Test from "./pages/test.tsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Mapping />} />
        <Route path="/testroute" element={<Test />}/>
        <Route path="/Ontology" element={<OntologyData />} />
      </Routes>
    </Router>
  );
}

export default App;
