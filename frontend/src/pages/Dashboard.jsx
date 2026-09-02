import { useState } from "react";

import {
    Shield,
    Search,
    AlertTriangle,
    Brain,
    Activity,
    Lock,
    LogOut,
    UserCircle,
} from "lucide-react";

import {
    runFullSecurityAnalysis,
    activateProtection,
} from "../services/api";


function Dashboard({ onLogout }) {

    const [analysis, setAnalysis] =
        useState(null);

    const [protection, setProtection] =
        useState(null);

    const [loading, setLoading] =
        useState(false);

    const [protecting, setProtecting] =
        useState(false);


    // ========================================================
    // USER
    // ========================================================

    const storedUser =
        localStorage.getItem(
            "datafence_user"
        );


    let user = null;

    try {

        user = storedUser
            ? JSON.parse(storedUser)
            : null;

    } catch {

        user = null;
    }


    const userName =
        user?.name || "DATAFENCE User";

    const userEmail =
        user?.email || "";


    // ========================================================
    // ANALYZE
    // ========================================================

    const analyze = async () => {

        setLoading(true);

        try {

            const result =
                await runFullSecurityAnalysis();

            setAnalysis(result);

        } catch (error) {

            console.error(
                "Analysis error:",
                error
            );


            if (
                error.message.includes(
                    "Session expired"
                ) ||
                error.message.includes(
                    "Authentication"
                ) ||
                error.message.includes(
                    "401"
                )
            ) {

                alert(
                    "Your session has expired. Please login again."
                );

                onLogout();

                return;
            }


            alert(
                error.message ||
                "Unable to connect to DATAFENCE backend."
            );

        } finally {

            setLoading(false);
        }
    };


    // ========================================================
    // PROTECTION
    // ========================================================

    const protect = async () => {

        setProtecting(true);

        try {

            const result =
                await activateProtection();

            setProtection(result);

        } catch (error) {

            console.error(
                "Protection error:",
                error
            );

            alert(
                error.message ||
                "Protection engine unavailable."
            );

        } finally {

            setProtecting(false);
        }
    };


    const security =
        analysis?.security;

    const intelligence =
        analysis?.intelligence;


    // ========================================================
    // UI
    // ========================================================

    return (

        <div className="dashboard">

            {/* =================================================
                HEADER
            ================================================= */}

            <header className="topbar">

                <div className="brand">

                    <Shield size={28} />

                    <div>

                        <h1>
                            DATAFENCE
                        </h1>

                        <span>
                            Personal Data Security
                        </span>

                    </div>

                </div>


                {/* USER */}

                <div className="topbar-user">

                    <UserCircle size={32} />

                    <div className="user-info">

                        <strong>
                            {userName}
                        </strong>

                        <span>
                            {userEmail}
                        </span>

                    </div>

                </div>


                {/* STATUS */}

                <div className="status">

                    <span className="status-dot"></span>

                    SYSTEM ONLINE

                </div>


                {/* LOGOUT */}

                <button
                    className="logout-button"
                    onClick={onLogout}
                >

                    <LogOut size={18} />

                    LOGOUT

                </button>

            </header>


            {/* =================================================
                HERO
            ================================================= */}

            <section className="hero">

                <div>

                    <p className="eyebrow">
                        PERSONAL DATA INTELLIGENCE
                    </p>

                    <h2>

                        Understand what your

                        <span>
                            {" "}data reveals.
                        </span>

                    </h2>

                    <p className="hero-text">

                        DATAFENCE analyzes your
                        digital exposure, hidden
                        inferences and security risks.

                    </p>


                    <p className="analyzing-account">

                        Analyzing account:

                        <strong>
                            {" "}
                            {userEmail}
                        </strong>

                    </p>

                </div>


                <button
                    className="analyze-button"
                    onClick={analyze}
                    disabled={loading}
                >

                    <Search size={20} />

                    {loading
                        ? "ANALYZING..."
                        : "ANALYZE MY DATA"
                    }

                </button>

            </section>


            {/* =================================================
                SCORE
            ================================================= */}

            {security && (

                <section className="score-section">

                    <div className="score-card">

                        <div className="score-ring">

                            <strong>
                                {
                                    security.security_score
                                }
                            </strong>

                            <span>
                                /100
                            </span>

                        </div>


                        <div>

                            <p>
                                SECURITY SCORE
                            </p>

                            <h3>
                                {
                                    security.risk_level
                                }
                            </h3>

                            <span>
                                Risk Score:{" "}
                                {
                                    security.risk_score
                                }
                            </span>

                        </div>

                    </div>


                    <button
                        className="protect-button"
                        onClick={protect}
                        disabled={protecting}
                    >

                        <Shield size={22} />

                        {protecting
                            ? "PROTECTING..."
                            : "PROTECT ME"
                        }

                    </button>

                </section>

            )}


            {/* =================================================
                SECURITY INTELLIGENCE
            ================================================= */}

            {intelligence && (

                <>

                    <h3 className="section-title">
                        Security Intelligence
                    </h3>


                    <section className="risk-grid">

                        <RiskCard
                            icon={
                                <AlertTriangle />
                            }
                            title="Data Exposure"
                            value={
                                intelligence
                                    .exposure
                                    .score
                            }
                            subtitle={
                                `${intelligence.exposure.total_items} data points`
                            }
                        />


                        <RiskCard
                            icon={
                                <Brain />
                            }
                            title="Inference Risk"
                            value={
                                intelligence
                                    .inference
                                    .score
                            }
                            subtitle={
                                `${intelligence.inference.findings.length} inferred profiles`
                            }
                        />


                        <RiskCard
                            icon={
                                <Activity />
                            }
                            title="Threat Level"
                            value={
                                intelligence
                                    .threat
                                    .score
                            }
                            subtitle={
                                intelligence
                                    .threat
                                    .level
                            }
                        />


                        <RiskCard
                            icon={
                                <Lock />
                            }
                            title="Blast Radius"
                            value={
                                intelligence
                                    .blast_radius
                                    .score
                            }
                            subtitle={
                                `${intelligence.blast_radius.connected_services} connected services`
                            }
                        />

                    </section>


                    {/* =========================================
                        INFERENCE
                    ========================================= */}

                    <section className="inference-section">

                        <div className="section-header">

                            <Brain />

                            <div>

                                <h3>
                                    What Your Data Can Reveal
                                </h3>

                                <p>
                                    DATAFENCE detected
                                    potential inferred
                                    characteristics.
                                </p>

                            </div>

                        </div>


                        <div className="inference-list">

                            {
                                intelligence
                                    .inference
                                    .findings
                                    .map(
                                        (
                                            finding,
                                            index
                                        ) => (

                                            <div
                                                className="inference-item"
                                                key={index}
                                            >

                                                <div>

                                                    <strong>
                                                        {
                                                            finding.inference
                                                        }
                                                    </strong>

                                                    <span>
                                                        Sources:{" "}
                                                        {
                                                            finding
                                                                .source_categories
                                                                .join(
                                                                    ", "
                                                                )
                                                        }
                                                    </span>

                                                </div>

                                                <b>
                                                    {
                                                        finding.severity
                                                    }
                                                </b>

                                            </div>

                                        )
                                    )
                            }

                        </div>

                    </section>

                </>

            )}


            {/* =================================================
                PROTECTION
            ================================================= */}

            {protection && (

                <section className="protection-result">

                    <Shield size={24} />

                    <div>

                        <h3>
                            Protection Processed
                        </h3>

                        <p>

                            Successful:{" "}

                            {
                                protection.result
                                    ?.verification
                                    ?.successful ?? 0
                            }

                            {" • "}

                            Pending approval:{" "}

                            {
                                protection.result
                                    ?.verification
                                    ?.pending ?? 0
                            }

                        </p>

                    </div>

                </section>

            )}

        </div>
    );
}


// ============================================================
// RISK CARD
// ============================================================

function RiskCard({
    icon,
    title,
    value,
    subtitle,
}) {

    return (

        <div className="risk-card">

            <div className="risk-icon">
                {icon}
            </div>

            <span>
                {title}
            </span>

            <strong>
                {value}
            </strong>

            <small>
                {subtitle}
            </small>

        </div>
    );
}


export default Dashboard;