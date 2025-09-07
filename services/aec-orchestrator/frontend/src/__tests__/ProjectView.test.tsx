






import React from 'react';
import { render, screen } from '@testing-library/react';
import ProjectView from '../pages/ProjectView';

describe('ProjectView Component', () => {
  it('renders loading state initially', () => {
    // Mock useParams and axios to avoid real API calls
    jest.mock('react-router-dom', () => ({
      __esModule: true,
      useParams: () => ({ projectId: '123' }),
    }));
    jest.mock('axios');

    render(<ProjectView />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  // Add more tests as needed
});



