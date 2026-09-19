import { useState } from "react";
import { ArrowRight, Lock, Mail, Shield } from "lucide-react";
import { login } from "../services/api";

export default function Login({ onLogin, onSignup }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(email.trim(), password);
      onLogin(result.token, result.user);
    } catch (err) {
      setError(err.message || "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: "500px" }}>
        <div className="auth-logo">
          <div className="auth-logo-icon"><Shield size={28} /></div>
          <div><h1>DATAFENCE</h1><span>Personal Data Security</span></div>
        </div>
        <div className="auth-heading">
          <h2>Sign in to your security profile</h2>
          <p>Analysis is restricted to the email address associated with your account.</p>
        </div>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={submit} className="auth-form">
          <label htmlFor="email">Email address</label>
          <div className="input-wrapper"><Mail size={18} /><input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required /></div>
          <label htmlFor="password">Password</label>
          <div className="input-wrapper"><Lock size={18} /><input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required /></div>
          <button className="auth-button" type="submit" disabled={loading}>
            {loading ? "SIGNING IN..." : "SIGN IN"}{!loading && <ArrowRight size={18} />}
          </button>
        </form>
        <div className="auth-switch"><span>New to DATAFENCE?</span><button type="button" onClick={onSignup}>Create an account</button></div>
      </div>
    </div>
  );
}
