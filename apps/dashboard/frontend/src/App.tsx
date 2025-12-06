import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import {
    TrainingNexus,
    BrainCore,
    ScraperControls,
    DashboardControls,
    SystemHealth,
    LiveChart,
    LogTerminal,
    ConfigPanel
} from './components';

const Dashboard = () => (
    <div className="p-6 space-y-6 text-white">
        {/* Top Row: Stats & Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
                <BrainCore />
            </div>
            <div>
                <SystemHealth />
            </div>
        </div>

        {/* Middle Row: Logs Only (LiveChart removed) */}
        <div className="grid grid-cols-1 h-[350px]">
            <LogTerminal />
        </div>

        {/* Bottom Row: Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <DashboardControls />
            <ConfigPanel />
            <ScraperControls />
        </div>
    </div>
);

// Strategies Component Placeholder
const Strategies = () => <div className="p-10 text-white">Strategies Placeholder</div>;

// Live Chart Page (Standalone if accessed via sidebar)
const LiveChartPage = () => (
    <div className="p-8 text-white max-w-[1600px] mx-auto">
        <h1 className="text-3xl font-bold mb-8 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
            Market Intelligence
        </h1>
        <div className="h-[600px]">
            <LiveChart />
        </div>
    </div>
);

const App: React.FC = () => {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/live-chart" element={<LiveChartPage />} />
                    <Route path="/brain" element={<BrainCore />} />
                    <Route path="/strategies" element={<Strategies />} />
                    <Route path="/training" element={<TrainingNexus />} />
                </Routes>
            </Layout>
        </Router>
    );
};

export default App;
