import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import App from './App';

// Mock the pages to avoid routing issues in tests
jest.mock('./pages/Home', () => {
  return function Home() {
    return <div>Home Page</div>;
  };
});

jest.mock('./pages/Dashboard', () => {
  return function Dashboard() {
    return <div>Dashboard Page</div>;
  };
});

jest.mock('./pages/SyncTaskList', () => {
  return function SyncTaskList() {
    return <div>Task List Page</div>;
  };
});

jest.mock('./pages/TaskDetail', () => {
  return function TaskDetail() {
    return <div>Task Detail Page</div>;
  };
});

jest.mock('./pages/TaskLogList', () => {
  return function TaskLogList() {
    return <div>Task Log Page</div>;
  };
});

function renderWithRouter(component) {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
}

test('renders without crashing', () => {
  renderWithRouter(<App />);
});

test('renders navigation menu', () => {
  renderWithRouter(<App />);

  // Check if navigation elements are present (using Chinese text as it appears in the app)
  expect(screen.getByText('Redis-Shake Web管理平台')).toBeInTheDocument();
});

test('renders main content area', () => {
  renderWithRouter(<App />);

  // The app should render some content - check for the app container using testing library
  const appElement = screen.getByTestId('app-container');
  expect(appElement).toBeInTheDocument();
});
