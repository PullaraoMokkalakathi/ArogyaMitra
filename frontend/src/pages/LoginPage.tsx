import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login, LoginCredentials } from "../api/auth";
import { checkHealthProfile } from "../api/health";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const credentials: LoginCredentials = { email, password };
      const response = await login(credentials);

      const token = response.tokens?.access_token;
      if (!token) {
        throw new Error("No access token received from server");
      }

      localStorage.setItem("access_token", token);

      const profileCheck = await checkHealthProfile();
      navigate(profileCheck.exists ? "/dashboard" : "/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4">
      <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-white">Welcome Back</h1>
          <p className="mt-2 text-sm text-cyan-200/70">Sign in to your account</p>
        </div>
        {error && (
          <div className="mt-4 rounded-lg border border-red-500/30 bg-red-600/20 p-3">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-cyan-200">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-cyan-200">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-cyan-600/80 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-cyan-600/25 transition-all hover:bg-cyan-500 hover:shadow-cyan-500/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-gray-950 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-cyan-200/70">
          Don't have an account?{" "}
          <Link to="/register" className="font-medium text-cyan-400 hover:text-cyan-300">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}