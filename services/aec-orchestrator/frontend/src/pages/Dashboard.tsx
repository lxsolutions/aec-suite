





import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard: React.FC = () => {
  const [agentRuns, setAgentRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch agent runs data
    axios.get('/api/agents/runs')
      .then(response => {
        setAgentRuns(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching agent runs:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading dashboard data...</div>;
  }

  return (
    <div>
      <h1>AEC Orchestrator Dashboard</h1>

      <section>
        <h2>Recent Agent Runs</h2>
        {agentRuns.length > 0 ? (
          <ul>
            {agentRuns.map((run: any) => (
              <li key={run.id}>
                <strong>{run.agent_type}</strong>: {run.status} - {new Date(run.created_at).toLocaleString()}
              </li>
            ))}
          </ul>
        ) : (
          <p>No agent runs found.</p>
        )}
      </section>

      <section>
        <h2>Quick Actions</h2>
        <button onClick={() => window.location.href = '/workflow-builder'}>
          Create New Workflow
        </button>
      </section>
    </div>
  );
};

export default Dashboard;


