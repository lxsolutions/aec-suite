





import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

const Dashboard = () => <div>Dashboard Page</div>;
const WorkflowBuilder = () => <div>Workflow Builder Page</div>;
const ProjectView = () => <div>Project View Page</div>;

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/workflows" element={<WorkflowBuilder />} />
        <Route path="/projects/:id" element={<ProjectView />} />
      </Routes>
    </Router>
  );
}

export default App;

