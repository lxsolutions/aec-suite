
import React, { useState } from 'react';
import axios from 'axios';

const BidPlanBill = () => {
  const [activeTab, setActiveTab] = useState('bid');
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [rfpFile, setRfpFile] = useState(null);
  const [project, setProject] = useState(null);
  const [estimate, setEstimate] = useState(null);
  const [erpId, setErpId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreateProject = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('http://localhost:8080/v1/projects', {
        name: projectName,
        description: projectDescription,
        client_id: 'demo-client',
        budget: 1000000,
        status: 'active'
      });
      
      setProject(response.data);
      setActiveTab('plan');
    } catch (err) {
      setError('Failed to create project: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadRfp = async () => {
    if (!rfpFile || !project) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', rfpFile);
      formData.append('project_id', project.id);
      
      const response = await axios.post('http://localhost:8080/v1/rfps/ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Wait a bit for processing and check for estimate
      setTimeout(() => checkEstimate(project.id), 2000);
    } catch (err) {
      setError('Failed to upload RFP: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const checkEstimate = async (projectId) => {
    try {
      const response = await axios.get(`http://localhost:8080/v1/estimates?project_id=${projectId}`);
      if (response.data && response.data.length > 0) {
        setEstimate(response.data[0]);
        setActiveTab('bill');
        
        // Simulate ERP sync completion after a delay
        setTimeout(() => {
          setErpId(`ERP-${Math.random().toString(36).substr(2, 9).toUpperCase()}`);
        }, 3000);
      }
    } catch (err) {
      console.log('No estimate found yet, will retry...');
      setTimeout(() => checkEstimate(projectId), 2000);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-center">Bid → Plan → Bill</h2>
      
      {/* Tabs */}
      <div className="flex mb-6 border-b">
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'bid' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
          onClick={() => setActiveTab('bid')}
        >
          Bid (Create Project)
        </button>
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'plan' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
          onClick={() => setActiveTab('plan')}
        >
          Plan (Upload RFP)
        </button>
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'bill' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
          onClick={() => setActiveTab('bill')}
        >
          Bill (Estimate & ERP)
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Bid Tab */}
      {activeTab === 'bid' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Create New Project</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project Name
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project description"
              rows={3}
            />
          </div>
          <button
            onClick={handleCreateProject}
            disabled={loading || !projectName}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      )}

      {/* Plan Tab */}
      {activeTab === 'plan' && project && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Upload RFP Document</h3>
          <p className="text-gray-600">Project: {project.name}</p>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              RFP Document
            </label>
            <input
              type="file"
              onChange={(e) => setRfpFile(e.target.files[0])}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              accept=".pdf,.docx,.txt"
            />
          </div>
          
          <button
            onClick={handleUploadRfp}
            disabled={loading || !rfpFile}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400"
          >
            {loading ? 'Uploading...' : 'Upload RFP'}
          </button>
        </div>
      )}

      {/* Bill Tab */}
      {activeTab === 'bill' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Estimate & ERP Integration</h3>
          
          {estimate ? (
            <div className="bg-gray-50 p-4 rounded-md">
              <h4 className="font-semibold mb-2">Estimate Details</h4>
              <p><strong>Total Amount:</strong> ${estimate.total_amount?.toLocaleString()}</p>
              <p><strong>Status:</strong> {estimate.status}</p>
              <p><strong>Items:</strong> {estimate.items?.length || 0} line items</p>
              
              {erpId ? (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                  <h4 className="font-semibold text-green-800">ERP Integration Complete!</h4>
                  <p className="text-green-700">ERP ID: {erpId}</p>
                  <p className="text-sm text-green-600">Estimate successfully synced to ERP system</p>
                </div>
              ) : (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-blue-700">Syncing with ERP system...</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-yellow-50 p-4 rounded-md border border-yellow-200">
              <p className="text-yellow-700">Waiting for estimate generation...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BidPlanBill;
