/**
 * Login Page — Split screen with brand panel and login form
 *
 * Supports: email/password, Google OAuth, Facebook OAuth
 */

import { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff, Sparkles, Target, Clock } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { BACKEND_URL } from "../../utils/constants";
import { clearAuthStorage } from "../../utils/authStorage";
import Button from "../../components/ui/Button";
import toast from "react-hot-toast";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const handleOAuthStart = (provider) => {
    clearAuthStorage();
    window.location.href = `${BACKEND_URL}/api/v1/auth/${provider}/login`;
  };

  useEffect(() => {
    const oauthError = searchParams.get("error");
    if (!oauthError) return;

    const detail = searchParams.get("detail");
    const messages = {
      oauth_failed: "Google sign-in failed on the server.",
      oauth_state_lost:
        "Sign-in timed out. Click Continue with Google again (do not restart the backend while on Google’s page).",
      redirect_uri_mismatch:
        "Redirect URI mismatch. In Google Cloud Console add exactly: http://localhost:8000/api/v1/auth/google/callback",
      oauth_denied:
        "Google denied access. Add your Gmail under OAuth consent screen → Test users (if app is in Testing).",
      oauth_not_configured:
        "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env",
      no_email:
        "Google did not return an email. Use another account or email login.",
    };
    let message = messages[oauthError] || "Sign-in failed. Please try again.";
    if (detail) {
      message += ` (${decodeURIComponent(detail)})`;
    }
    setError(message);
    setSearchParams({}, { replace: true });
  }, [searchParams, setSearchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err) {
      setError(err?.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left: Brand Panel */}
      <div className="hidden lg:flex lg:w-[40%] bg-gradient-to-br from-indigo-950 via-slate-950 to-violet-950 relative overflow-hidden flex-col justify-center p-12">
        {/* Gradient orbs for visual interest */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-600/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl" />

        <div className="relative z-10">
          <h1 className="text-4xl font-display font-bold text-white mb-3">
            Job<span className="text-indigo-400">Lense</span>
          </h1>
          <p className="text-lg text-slate-300 mb-10">
            Track smarter. Apply better. Land faster.
          </p>

          <div className="space-y-5">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-indigo-500/20 rounded-lg mt-0.5">
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <p className="text-slate-100 font-medium text-sm">
                  AI-powered ATS analysis
                </p>
                <p className="text-slate-400 text-sm">
                  Know your resume score before applying
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="p-2 bg-violet-500/20 rounded-lg mt-0.5">
                <Target className="w-4 h-4 text-violet-400" />
              </div>
              <div>
                <p className="text-slate-100 font-medium text-sm">
                  Smart job application tracker
                </p>
                <p className="text-slate-400 text-sm">
                  Track every application in one place
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="p-2 bg-emerald-500/20 rounded-lg mt-0.5">
                <Clock className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <p className="text-slate-100 font-medium text-sm">
                  Interview reminders on autopilot
                </p>
                <p className="text-slate-400 text-sm">
                  Never miss an interview again
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right: Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-app">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <h1 className="text-2xl font-display font-bold text-center mb-2 lg:hidden">
            Job<span className="text-indigo-400">Lense</span>
          </h1>

          <h2 className="text-2xl font-display font-bold text-slate-100 mb-1">
            Welcome back
          </h2>
          <p className="text-slate-400 text-sm mb-8">
            Sign in to continue tracking your applications
          </p>

          {error && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-3 rounded-xl text-sm mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="form-label" htmlFor="login-email">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
                <input
                  id="login-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-10"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="form-label" htmlFor="login-password">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10 pr-10"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3.5 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              loading={loading}
              className="w-full"
              size="lg"
            >
              Sign In
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-slate-700" />
            <span className="text-slate-500 text-xs">or continue with</span>
            <div className="flex-1 h-px bg-slate-700" />
          </div>

          {/* OAuth Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => handleOAuthStart("google")}
              className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-50 text-gray-800 font-medium px-4 py-2.5 rounded-xl transition-all duration-200"
              id="google-login-btn"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </button>

            <button
              onClick={() => handleOAuthStart("facebook")}
              className="w-full flex items-center justify-center gap-3 bg-[#1877F2] hover:bg-[#166FE5] text-white font-medium px-4 py-2.5 rounded-xl transition-all duration-200"
              id="facebook-login-btn"
            >
              <svg className="w-5 h-5" fill="white" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
              Continue with Facebook
            </button>
          </div>

          <p className="text-center text-slate-400 text-sm mt-8">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="text-indigo-400 hover:text-indigo-300 font-medium"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
