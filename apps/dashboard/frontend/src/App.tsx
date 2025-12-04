import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import { TrainingNexus, BrainCore, ScraperControls } from './components';

// Placeholder components for existing routes
const Dashboard = () => (
    <div className="p-10 text-white">
        <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
        <ScraperControls />
    </div>
);
const Strategies = () => <div className="p-10 text-white">Strategies Placeholder</div>;

const App: React.FC = () => {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/brain" element={<BrainCore />} />
                    <Route path="/strategies" element={<Strategies />} />
                    <Route path="/training" element={<TrainingNexus />} />
                </Routes>
            </Layout>
        </Router>
    );
};

export default App;
