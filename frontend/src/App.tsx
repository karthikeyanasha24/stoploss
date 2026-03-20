import { Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./lib/theme";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import TradeDetails from "./pages/TradeDetails";
import Analysis from "./pages/Analysis";
import SheetReference from "./pages/SheetReference";
import Logs from "./pages/Logs";

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trade/:id" element={<TradeDetails />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/sheet-reference" element={<SheetReference />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </ThemeProvider>
  );
}
