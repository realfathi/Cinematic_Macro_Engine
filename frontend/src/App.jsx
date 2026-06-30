import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ExecutiveSnapshot from './pages/ExecutiveSnapshot';
import MacroCrisisImpact from './pages/MacroCrisisImpact';
import StructuralRuntimeTrends from './pages/StructuralRuntimeTrends';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ExecutiveSnapshot />} />
          <Route path="macro" element={<MacroCrisisImpact />} />
          <Route path="structural" element={<StructuralRuntimeTrends />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
