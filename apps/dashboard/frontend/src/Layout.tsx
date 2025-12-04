import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Activity, Zap, Settings, Cpu } from 'lucide-react';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/brain', label: 'Neural Swarm', icon: Cpu },
        { path: '/strategies', label: 'Strategies', icon: Zap },
        { path: '/training', label: 'Training Nexus', icon: Activity },
        { path: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <div className="flex min-h-screen bg-slate-950">
            {/* Sidebar */}
            <aside className="w-64 bg-slate-900 border-r border-slate-800">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-cyan-400 tracking-wider">OMNITRADE</h1>
                    <p className="text-xs text-slate-500 tracking-widest mt-1">AI CORE v2.0</p>
                </div>

                <nav className="mt-6 px-4 space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;

                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${isActive
                                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                                        : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                                    }`}
                            >
                                <Icon className="w-5 h-5" />
                                <span className="font-medium">{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                {children}
            </main>
        </div>
    );
};

export default Layout;
