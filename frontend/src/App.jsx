import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<h1>Home ✅</h1>} />
        <Route path="/browse" element={<h1>Browse ✅</h1>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
