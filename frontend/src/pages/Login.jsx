import { useState } from "react";

import {
    Shield,
    Mail,
    Lock,
    User,
    ArrowRight,
} from "lucide-react";

import {
    login,
    signup,
} from "../services/api";


function Login({ onLogin }) {

    const [mode, setMode] = useState(
        "login"
    );

    const [name, setName] = useState("");

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");


    const isSignup =
        mode === "signup";


    const submit = async (event) => {

        event.preventDefault();

        setError("");

        setLoading(true);

        try {

            let result;

            // ---------------------------------------------
            // SIGNUP
            // ---------------------------------------------

            if (isSignup) {

                result = await signup(
                    name.trim(),
                    email.trim(),
                    password
                );

            }

            // ---------------------------------------------
            // LOGIN
            // ---------------------------------------------

            else {

                result = await login(
                    email.trim(),
                    password
                );

            }


            // ---------------------------------------------
            // VALIDATE RESPONSE
            // ---------------------------------------------

            if (!result.token) {

                throw new Error(
                    "Authentication server did not return a session token."
                );
            }


            if (!result.user) {

                throw new Error(
                    "Authentication server did not return user information."
                );
            }


            // ---------------------------------------------
            // STORE SESSION
            // ---------------------------------------------

            localStorage.setItem(
                "datafence_token",
                result.token
            );

            localStorage.setItem(
                "datafence_user",
                JSON.stringify(
                    result.user
                )
            );


            // ---------------------------------------------
            // OPEN DASHBOARD
            // ---------------------------------------------

            onLogin(
                result.token,
                result.user
            );


        } catch (err) {

            console.error(
                "Authentication error:",
                err
            );

            setError(
                err.message ||
                "Authentication failed."
            );

        } finally {

            setLoading(false);
        }
    };


    return (

        <div className="auth-page">

            <div className="auth-card">

                {/* LOGO */}

                <div className="auth-logo">

                    <div className="auth-logo-icon">

                        <Shield size={28} />

                    </div>

                    <div>

                        <h1>
                            DATAFENCE
                        </h1>

                        <span>
                            Personal Data Security
                        </span>

                    </div>

                </div>


                {/* HEADING */}

                <div className="auth-heading">

                    <h2>

                        {isSignup
                            ? "Create your account"
                            : "Welcome back"}

                    </h2>

                    <p>

                        {isSignup
                            ? "Start understanding what your data reveals."
                            : "Sign in to access your personal security dashboard."}

                    </p>

                </div>


                {/* ERROR */}

                {error && (

                    <div className="auth-error">

                        {error}

                    </div>

                )}


                {/* FORM */}

                <form onSubmit={submit}>

                    {isSignup && (

                        <div className="input-group">

                            <label>
                                Full name
                            </label>

                            <div className="input-wrapper">

                                <User size={18} />

                                <input
                                    type="text"
                                    placeholder="Enter your name"
                                    value={name}
                                    onChange={(e) =>
                                        setName(
                                            e.target.value
                                        )
                                    }
                                    required
                                    minLength={2}
                                />

                            </div>

                        </div>

                    )}


                    <div className="input-group">

                        <label>
                            Email address
                        </label>

                        <div className="input-wrapper">

                            <Mail size={18} />

                            <input
                                type="email"
                                placeholder="you@example.com"
                                value={email}
                                onChange={(e) =>
                                    setEmail(
                                        e.target.value
                                    )
                                }
                                required
                            />

                        </div>

                    </div>


                    <div className="input-group">

                        <label>
                            Password
                        </label>

                        <div className="input-wrapper">

                            <Lock size={18} />

                            <input
                                type="password"
                                placeholder={
                                    isSignup
                                        ? "Minimum 8 characters"
                                        : "Enter your password"
                                }
                                value={password}
                                onChange={(e) =>
                                    setPassword(
                                        e.target.value
                                    )
                                }
                                minLength={8}
                                required
                            />

                        </div>

                    </div>


                    <button
                        className="auth-button"
                        type="submit"
                        disabled={loading}
                    >

                        {loading
                            ? "PLEASE WAIT..."
                            : isSignup
                                ? "CREATE ACCOUNT"
                                : "SIGN IN"
                        }

                        {!loading && (
                            <ArrowRight size={18} />
                        )}

                    </button>

                </form>


                {/* SWITCH */}

                <div className="auth-switch">

                    {isSignup
                        ? "Already have an account?"
                        : "Don't have an account?"
                    }

                    <button
                        type="button"
                        onClick={() => {

                            setError("");

                            setMode(
                                isSignup
                                    ? "login"
                                    : "signup"
                            );

                        }}
                    >

                        {isSignup
                            ? "Sign in"
                            : "Create account"
                        }

                    </button>

                </div>


                {/* SECURITY */}

                <div className="auth-security">

                    <Shield size={16} />

                    <span>
                        Your DATAFENCE account is protected
                    </span>

                </div>

            </div>

        </div>
    );
}


export default Login;