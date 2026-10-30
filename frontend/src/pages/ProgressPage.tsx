import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProgressStats, ProgressStatsResponse } from "../api/progress";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export default function ProgressPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<ProgressStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProgressStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-cyan-200/50 p-8">Loading progress...</div>;

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4 py-8">
      <div className="mx-auto w-full max-w-6xl space-y-6">
        <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
          <div>
            <h1 className="text-3xl font-bold text-white">Progress Tracking</h1>
            <p className="text-cyan-200/70">Monitor your fitness journey and achievements</p>
          </div>
          <button onClick={() => navigate("/dashboard")} className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-cyan-200 hover:bg-white/10">← Back</button>
        </div>

        {/* Overview Cards */}
        <div className="grid gap-4 md:grid-cols-4">
           <div className="rounded-2xl border border-orange-500/30 bg-orange-900/20 p-6 shadow-2xl backdrop-blur-lg">
              <p className="text-sm text-orange-200/70">Current Streak</p>
              <p className="mt-1 text-3xl font-bold text-orange-400">{stats?.current_streak} Days</p>
           </div>
           <div className="rounded-2xl border border-red-500/30 bg-red-900/20 p-6 shadow-2xl backdrop-blur-lg">
              <p className="text-sm text-red-200/70">Calories Burned</p>
              <p className="mt-1 text-3xl font-bold text-red-400">{Math.round(stats?.total_calories || 0)}</p>
           </div>
           <div className="rounded-2xl border border-green-500/30 bg-green-900/20 p-6 shadow-2xl backdrop-blur-lg">
              <p className="text-sm text-green-200/70">Total Workouts</p>
              <p className="mt-1 text-3xl font-bold text-green-400">{stats?.total_workouts}</p>
           </div>
           <div className="rounded-2xl border border-cyan-500/30 bg-cyan-900/20 p-6 shadow-2xl backdrop-blur-lg">
              <p className="text-sm text-cyan-200/70">Total Minutes</p>
              <p className="mt-1 text-3xl font-bold text-cyan-400">{stats?.total_minutes}m</p>
           </div>
        </div>

        {/* Charts */}
        <div className="grid gap-6 lg:grid-cols-2">
           <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
              <h3 className="mb-4 text-lg font-semibold text-white">Weekly Calories Burned</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stats?.weekly_history || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                    <XAxis dataKey="date" stroke="#a5f3fc" fontSize={12} />
                    <YAxis stroke="#a5f3fc" fontSize={12} />
                    <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#ffffff10' }} />
                    <Area type="monotone" dataKey="calories" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
           </div>
           <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
              <h3 className="mb-4 text-lg font-semibold text-white">Posture Improvement (Accuracy)</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats?.weekly_history || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                    <XAxis dataKey="date" stroke="#a5f3fc" fontSize={12} />
                    <YAxis stroke="#a5f3fc" fontSize={12} />
                    <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#ffffff10' }} />
                    <Bar dataKey="avg_score" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
           </div>
        </div>

        {/* Timeline & Insights */}
        <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
                <h3 className="mb-4 text-lg font-semibold text-white">Recent Activity</h3>
                <div className="space-y-4">
                   {stats?.recent_logs.map(log => (
                       <div key={log.id} className="flex items-center justify-between border-b border-white/5 pb-4">
                           <div>
                               <p className="font-semibold text-white">{log.exercise_name}</p>
                               <p className="text-xs text-cyan-200/70">{new Date(log.workout_date).toLocaleString()}</p>
                           </div>
                           <div className="text-right">
                               <p className="text-green-400">{Math.round(log.calories_burned)} kcal</p>
                               <p className="text-xs text-cyan-200/70">{log.duration_minutes}m • Score {Math.round(log.posture_score)}%</p>
                           </div>
                       </div>
                   ))}
                   {(!stats?.recent_logs || stats.recent_logs.length === 0) && (
                       <p className="text-cyan-200/50">No workouts recorded yet.</p>
                   )}
                </div>
            </div>
            
            <div className="space-y-6">
                <div className="rounded-2xl border border-blue-500/30 bg-blue-900/20 p-6 shadow-2xl backdrop-blur-lg">
                    <h3 className="mb-4 text-lg font-semibold text-blue-300">Smart Insights</h3>
                    <ul className="list-disc pl-5 space-y-2 text-blue-100/80 text-sm">
                        <li>You trained {stats?.weekly_history.filter(d => d.workouts > 0).length || 0} days this week.</li>
                        <li>Best accuracy recorded: {Math.round(stats?.best_posture_score || 0)}%</li>
                        <li>Longest streak achieved: {stats?.best_streak} days</li>
                        {stats?.current_streak && stats.current_streak > 3 && (
                            <li className="text-green-400">Great job maintaining a {stats.current_streak} day streak!</li>
                        )}
                    </ul>
                </div>
                
                <div className="rounded-2xl border border-yellow-500/30 bg-yellow-900/20 p-6 shadow-2xl backdrop-blur-lg">
                    <h3 className="mb-4 text-lg font-semibold text-yellow-300">Achievements</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className={`p-3 rounded-lg border ${stats?.total_workouts && stats.total_workouts > 0 ? 'border-yellow-500 bg-yellow-500/10 text-yellow-300' : 'border-white/10 opacity-50 text-white'}`}>
                            First Workout
                        </div>
                        <div className={`p-3 rounded-lg border ${(stats?.best_streak || 0) >= 7 ? 'border-yellow-500 bg-yellow-500/10 text-yellow-300' : 'border-white/10 opacity-50 text-white'}`}>
                            7 Day Streak
                        </div>
                        <div className={`p-3 rounded-lg border ${(stats?.total_calories || 0) >= 500 ? 'border-yellow-500 bg-yellow-500/10 text-yellow-300' : 'border-white/10 opacity-50 text-white'}`}>
                            500 Calories
                        </div>
                        <div className={`p-3 rounded-lg border ${(stats?.best_posture_score || 0) >= 90 ? 'border-yellow-500 bg-yellow-500/10 text-yellow-300' : 'border-white/10 opacity-50 text-white'}`}>
                            90% Accuracy
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}