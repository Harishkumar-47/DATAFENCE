import { useState } from "react";

import {
    Shield,
    UserPlus,
    User,
    Mail,
    Lock,
    AlertCircle,
    CheckCircle,
} from "lucide-react";

import {
    signup,
} from "../services/api";


function Signup({
    onLogin,
}) {

    const [name, setName] =
        useState("");

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [confirmPassword, setConfirmPassword] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    const [success, setSuccess] =
        useState("");


    const handleSubmit =
        async (event) => {

            event.preventDefault();

            setError("");
            setSuccess("");


            if (name.trim().length < 2) {

                setError(
                    "Please enter your full name."
                );

                return;
            }


            if (!email.trim()) {

                setError(
                    "Please enter your email address."
                );

                return;
            }


            if (password.length < 8) {

                setError(
                    "Password must contain at least 8 characters."
                );

                return;
            }


            if (password !== confirmPassword) {

                setError(
                    "Passwords do not match."
                );

                return;
            }


            setLoading(true);


            try {

                const result =
                    await signup(
                        name.trim(),
                        email.trim(),
                        password
                    );


                setSuccess(
                    result.message ||
                    "Account created successfully."
                );


                setName("");
                setEmail("");
                setPassword("");
                setConfirmPassword("");


            } catch (err) {

                setError(
                    err.message ||
                    "Unable to create account."
                );

            } finally {

                setLoading(false);

            }
        };


    return (

        <div className="auth-page">

            <div className="auth-background" />

            <div className="auth-card">

                <div className="auth-brand">

                    <div className="brand-icon">

                        <Shield
                            size={28}
                        />

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


                <div className="auth-heading">

                    <p className="eyebrow">
                        CREATE YOUR ACCOUNT
                    </p>

                    <h2>
                        Start protecting your data.
                    </h2>

                    <p>
                        Create your DATAFENCE
                        security profile.
                    </p>

                </div>


                {error && (

                    <div className="auth-error">

                        <AlertCircle
                            size={18}
                        />

                        <span>
                            {error}
                        </span>

                    </div>

                )}


                {success && (

                    <div className="auth-success">

                        <CheckCircle
                            size={18}
                        />

                        <span>
                            {success}
                        </span>

                    </div>

                )}


                <form
                    onSubmit={handleSubmit}
                    className="auth-form"
                >

                    <label>
                        Full name
                    </label>

                    <div className="input-wrapper">

                        <User
                            size={18}
                        />

                        <input
                            type="text"
                            placeholder="Your name"
                            value={name}
                            onChange={
                                (event) =>
                                    setName(
                                        event.target.value
                                    )
                            }
                            autoComplete="name"
                        />

                    </div>


                    <label>
                        Email address
                    </label>

                    <div className="input-wrapper">

                        <Mail
                            size={18}
                        />

                        <input
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={
                                (event) =>
                                    setEmail(
                                        event.target.value
                                    )
                            }
                            autoComplete="email"
                        />

                    </div>


                    <label>
                        Password
                    </label>

                    <div className="input-wrapper">

                        <Lock
                            size={18}
                        />

                        <input
                            type="password"
                            placeholder="Minimum 8 characters"
                            value={password}
                            onChange={
                                (event) =>
                                    setPassword(
                                        event.target.value
                                    )
                            }
                            autoComplete="new-password"
                        />

                    </div>


                    <label>
                        Confirm password
                    </label>

                    <div className="input-wrapper">

                        <Lock
                            size={18}
                        />

                        <input
                            type="password"
                            placeholder="Repeat your password"
                            value={confirmPassword}
                            onChange={
                                (event) =>
                                    setConfirmPassword(
                                        event.target.value
                                    )
                            }
                            autoComplete="new-password"
                        />

                    </div>


                    <button
                        className="auth-button"
                        type="submit"
                        disabled={loading}
                    >

                        <UserPlus
                            size={19}
                        />

                        {loading
                            ? "CREATING ACCOUNT..."
                            : "CREATE ACCOUNT"}

                    </button>

                </form>


                <div className="auth-switch">

                    <span>
                        Already have an account?
                    </span>

                    <button
                        type="button"
                        onClick={onLogin}
                    >
                        Sign in
                    </button>

                </div>

            </div>

        </div>

    );
}


export default Signup;