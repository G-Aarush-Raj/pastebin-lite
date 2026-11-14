
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import PasteEditor from "./components/PasteEditor";
import ViewPaste from "./pages/ViewPaste";
import "./index.css";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <main className="app-container">
        <Routes>
          <Route path="/" element={<PasteEditor />} />
          <Route path="/p/:id" element={<ViewPaste />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
