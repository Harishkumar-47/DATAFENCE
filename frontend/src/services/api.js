const API_BASE_URL = "";


// ============================================================
// TOKEN
// ============================================================

function getToken() {

    return localStorage.getItem(
        "datafence_token"
    );
}


// ============================================================
// RESPONSE HANDLER
// ============================================================

async function parseResponse(response) {

    const data = await response
        .json()
        .catch(() => ({}));

    if (!response.ok) {

        let errorMsg = data.detail;
        if (Array.isArray(errorMsg)) {
            errorMsg = errorMsg.map(e => e.msg).join(", ");
        }

        throw new Error(
            errorMsg ||
            `Request failed: ${response.status}`
        );
    }

    return data;
}


// ============================================================
// SIGNUP
// ============================================================

export async function signup(
    name,
    email,
    password
) {

    const response = await fetch(
        `${API_BASE_URL}/api/auth/signup`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                name,
                email,
                password,
            }),
        }
    );

    return parseResponse(
        response
    );
}


// ============================================================
// LOGIN
// ============================================================

export async function login(
    email,
    password
) {

    const response = await fetch(
        `${API_BASE_URL}/api/auth/login`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                email,
                password,
            }),
        }
    );

    return parseResponse(
        response
    );
}


// ============================================================
// CURRENT USER
// ============================================================

export async function getCurrentUser() {

    const token = getToken();

    if (!token) {

        throw new Error(
            "Not authenticated"
        );
    }

    const response = await fetch(
        `${API_BASE_URL}/api/auth/me`,
        {
            method: "GET",

            headers: {
                Authorization:
                    `Bearer ${token}`,
            },
        }
    );

    return parseResponse(
        response
    );
}


// ============================================================
// LOGOUT
// ============================================================

export async function logout() {

    const token = getToken();

    if (!token) {
        return;
    }

    const response = await fetch(
        `${API_BASE_URL}/api/auth/logout`,
        {
            method: "POST",

            headers: {
                Authorization:
                    `Bearer ${token}`,
            },
        }
    );

    return parseResponse(
        response
    );
}


// ============================================================
// BASIC ANALYSIS
// ============================================================

export async function runAnalysis() {

    const token = getToken();

    if (!token) {

        throw new Error(
            "Please login before running analysis."
        );
    }

    const response = await fetch(
        `${API_BASE_URL}/api/analysis/run`,
        {
            method: "POST",

            headers: {
                Authorization:
                    `Bearer ${token}`,
            },
        }
    );

    return parseResponse(
        response
    );
}


// ============================================================
// FULL SECURITY ANALYSIS
// ============================================================

export async function runFullSecurityAnalysis(email, phone) {

    const token = getToken();

    if (!token) {

        throw new Error(
            "Please login before running analysis."
        );
    }

    const response = await fetch(
        `${API_BASE_URL}/api/security/full-analysis`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                Authorization:
                    `Bearer ${token}`,
            },
            
            body: JSON.stringify({
                email: email,
                phone: phone
            }),
        }
    );

    return parseResponse(
        response
    );
}


// ============================================================
// PROTECTION
// ============================================================

export async function activateProtection() {

    const token = getToken();

    if (!token) {

        throw new Error(
            "Please login first."
        );
    }

    /*
     * Temporary frontend-safe protection.
     * Replace this with the real protection
     * endpoint when remediation is connected.
     */

    return {

        status: "PROTECTION_READY",

        result: {

            verification: {

                successful: 0,

                pending: 0,
            },
        },
    };
}