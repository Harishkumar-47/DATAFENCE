import { useState } from "react";
import { Shield, Mail, Phone, ArrowRight } from "lucide-react";
import { login } from "../services/api";

function Login({ onLogin }) {
    const [email, setEmail] = useState("");
    const [emailDomain, setEmailDomain] = useState("@gmail.com");
    const [phone, setPhone] = useState("");
    const [countryCode, setCountryCode] = useState("+1");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const validateInputs = () => {
        if (!email && !phone) {
            return "Please provide either an email or a phone number to analyze.";
        }
        
        if (email) {
            const actualEmail = email.includes('@') ? email : (email + emailDomain);
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(actualEmail)) {
                return "Please enter a valid email address.";
            }
        }
        
        if (phone) {
            const fullPhone = countryCode + phone.replace(/\D/g, '');
            const phoneRegex = /^\+[1-9]\d{6,14}$/;
            if (!phoneRegex.test(fullPhone)) {
                return "Please enter a valid phone number (6-14 digits).";
            }
        }
        
        return null;
    };

    const submit = async (event) => {
        event.preventDefault();
        
        const validationError = validateInputs();
        if (validationError) {
            setError(validationError);
            return;
        }
        
        setError("");
        setLoading(true);

        try {
            const fullPhone = phone ? (countryCode + phone.replace(/\D/g, '')) : "";
            const actualEmail = email ? (email.includes('@') ? email.trim() : email.trim() + emailDomain) : "";
            
            const authEmail = actualEmail ? actualEmail.toLowerCase() : `${fullPhone.replace('+', '')}@datafence.local`;
            const result = await login(authEmail, "DATAFENCE_GUEST_ACCOUNT_8829!");

            if (!result.token || !result.user) {
                throw new Error("Authentication server did not return valid session data.");
            }

            // Store target data for the Dashboard to use
            localStorage.setItem("datafence_target_email", actualEmail);
            localStorage.setItem("datafence_target_phone", fullPhone);

            localStorage.setItem("datafence_token", result.token);
            localStorage.setItem("datafence_user", JSON.stringify(result.user));

            onLogin(result.token, result.user);
        } catch (err) {
            console.error("Analysis initiation error:", err);
            setError(err.message || "Failed to connect to the analysis engine.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card" style={{ maxWidth: "500px" }}>
                <div className="auth-logo">
                    <div className="auth-logo-icon">
                        <Shield size={28} />
                    </div>
                    <div>
                        <h1>DATAFENCE</h1>
                        <span>Personal Data Security</span>
                    </div>
                </div>

                <div className="auth-heading">
                    <h2>Check Your Data Exposure</h2>
                    <p>Enter your email or phone number to scan live datasets and find data breaches.</p>
                </div>

                {error && <div className="auth-error">{error}</div>}

                <form onSubmit={submit}>
                    <div className="input-group">
                        <label>Email Address</label>
                        <div className="input-wrapper" style={{ display: 'flex', padding: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', paddingLeft: '14px', width: '100%' }}>
                                <Mail size={18} style={{ marginRight: '8px', minWidth: '18px' }} />
                                <input
                                    type={emailDomain === "" ? "email" : "text"}
                                    placeholder={emailDomain === "" ? "you@example.com" : "username"}
                                    value={email}
                                    onChange={(e) => {
                                        setEmail(e.target.value);
                                        if (e.target.value.includes('@') && emailDomain !== "") {
                                            setEmailDomain("");
                                        }
                                    }}
                                    style={{ padding: '0', width: '100%', paddingRight: '14px' }}
                                />
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', paddingRight: '14px', background: 'rgba(0,0,0,0.2)', borderLeft: '1px solid #202b31', borderTopRightRadius: '9px', borderBottomRightRadius: '9px' }}>
                                <select 
                                    value={emailDomain} 
                                    onChange={(e) => setEmailDomain(e.target.value)}
                                    style={{ background: 'transparent', border: 'none', color: '#f5f7fa', fontSize: '14px', outline: 'none', cursor: 'pointer', padding: '14px 0' }}
                                >
                                    <option value="@gmail.com">@gmail.com</option>
                                    <option value="@yahoo.com">@yahoo.com</option>
                                    <option value="@outlook.com">@outlook.com</option>
                                    <option value="">Custom...</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="input-group">
                        <label>Phone Number</label>
                        <div className="input-wrapper" style={{ display: 'flex', padding: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', paddingLeft: '14px', background: 'rgba(0,0,0,0.2)', borderRight: '1px solid #202b31', borderTopLeftRadius: '9px', borderBottomLeftRadius: '9px' }}>
                                <Phone size={18} style={{ marginRight: '8px' }} />
                                <select 
                                    value={countryCode} 
                                    onChange={(e) => setCountryCode(e.target.value)}
                                    style={{ background: 'transparent', border: 'none', color: '#f5f7fa', fontSize: '14px', outline: 'none', cursor: 'pointer', paddingRight: '8px' }}
                                >
                                    <option value="+1">🇺🇸 +1</option>
                                    <option value="+44">🇬🇧 +44</option>
                                    <option value="+91">🇮🇳 +91</option>
                                    <option value="+61">🇦🇺 +61</option>
                                    <option value="+81">🇯🇵 +81</option>
                                    <option value="+49">🇩🇪 +49</option>
                                    <option value="+33">🇫🇷 +33</option>
                                    <option value="+86">🇨🇳 +86</option>
                                    <option value="+55">🇧🇷 +55</option>
                                    <option value="+27">🇿🇦 +27</option>
                                </select>
                            </div>
                            <input
                                type="tel"
                                placeholder="Phone Number (e.g. 9876543210)"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                                style={{ paddingLeft: '14px' }}
                            />
                        </div>
                    </div>

                    <button className="auth-button" type="submit" disabled={loading}>
                        {loading ? "ANALYZING DATA..." : "ANALYZE NOW"}
                        {!loading && <ArrowRight size={18} />}
                    </button>
                </form>

                <div className="auth-security">
                    <Shield size={16} />
                    <span>Your search is secure and confidential</span>
                </div>
            </div>
        </div>
    );
}

export default Login;