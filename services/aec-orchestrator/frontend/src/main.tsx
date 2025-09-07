




import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/Dashboard';
import WorkflowBuilderPage from './pages/WorkflowBuilder';
import ProjectViewPage from './pages/ProjectView';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/workflow-builder" element={<WorkflowBuilderPage />} />
        <Route path="/projects/:projectId" element={<ProjectViewPage />} />
      </Routes>
    </Router>
  </React.StrictMode>
);

