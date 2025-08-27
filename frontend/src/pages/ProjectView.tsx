





import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const ProjectView: React.FC = () => {
  const { projectId } = useParams();
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch project data
    axios.get(`/api/projects/${projectId}`)
      .then(response => {
        setProjectData(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching project:', error);
        setLoading(false);
      });
  }, [projectId]);

  if (loading) {
    return <div>Loading project data...</div>;
  }

  if (!projectData) {
    return <div>Project not found.</div>;
  }

  return (
    <div>
      <h1>{projectData.name}</h1>

      <section>
        <h2>Project Overview</h2>
        <p>{projectData.description || 'No description available.'}</p>
      </section>

      <section>
        <h2>Agent Runs</h2>
        {projectData.agent_runs && projectData.agent_runs.length > 0 ? (
          <ul>
            {projectData.agent_runs.map((run: any) => (
              <li key={run.id}>
                <strong>{run.agent_type}</strong>: {run.status} - {new Date(run.created_at).toLocaleString()}
              </li>
            ))}
          </ul>
        ) : (
          <p>No agent runs for this project.</p>
        )}
      </section>

      <button onClick={() => alert('Run new workflow!')}>
        Run New Workflow
      </button>
    </div>
  );
};

export default ProjectView;




