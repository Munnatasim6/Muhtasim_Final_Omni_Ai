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
    CandleChart,
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

        {/* Middle Row: Logs Only (LiveChart removed from dashboard main view as per design) */}
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
        <div className="grid gap-10">
            {/* New Candle Chart Section */}
            <section>
                <div className="flex items-center gap-2 mb-4">
                    <span className="w-1 h-6 bg-emerald-500 rounded-full"></span>
                    <h2 className="text-xl font-bold text-slate-200">Advanced Analysis</h2>
                    <span className="text-xs text-slate-500 border border-slate-700 px-2 py-0.5 rounded-full">Heiken Ashi</span>
                </div>
                <div className="h-[500px]">
                    <CandleChart />
                </div>
            </section>

            {/* Old Line Chart Section */}
            <section>
                <div className="flex items-center gap-2 mb-4">
                    <span className="w-1 h-6 bg-blue-500 rounded-full"></span>
                    <h2 className="text-xl font-bold text-slate-200">Quick Trend</h2>
                    <span className="text-xs text-slate-500 border border-slate-700 px-2 py-0.5 rounded-full">1s Ticker</span>
                </div>
                <div className="h-[350px]">
                    <LiveChart />
                </div>
            </section>
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
