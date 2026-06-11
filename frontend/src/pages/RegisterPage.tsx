import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register, RegisterCredentials } from "../api/auth";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data: RegisterCredentials = { email, password, confirm_password: confirmPassword };
      await register(data);
      navigate("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4">
      <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-white">Create Account</h1>
          <p className="mt-2 text-sm text-cyan-200/70">Sign up for a new account</p>
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
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-cyan-200">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
            {loading ? "Registering..." : "Register"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-cyan-200/70">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-cyan-400 hover:text-cyan-300">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}