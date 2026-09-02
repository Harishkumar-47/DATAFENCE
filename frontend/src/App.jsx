import {
    useEffect,
    useState,
} from "react";

import Login from "./pages/Login";

import Dashboard from "./pages/Dashboard";

import {
    getCurrentUser,
    logout,
} from "./services/api";


function App() {

    const [
        authenticated,
        setAuthenticated,
    ] = useState(false);


    const [
        checkingAuth,
        setCheckingAuth,
    ] = useState(true);


    // ========================================================
    // CHECK SESSION
    // ========================================================

    useEffect(() => {

        async function checkSession() {

            const token =
                localStorage.getItem(
                    "datafence_token"
                );

            const storedUser =
                localStorage.getItem(
                    "datafence_user"
                );


            if (!token || !storedUser) {

                localStorage.removeItem(
                    "datafence_token"
                );

                localStorage.removeItem(
                    "datafence_user"
                );

                setAuthenticated(false);

                setCheckingAuth(false);

                return;
            }


            try {

                const result =
                    await getCurrentUser();


                if (
                    result.status ===
                    "AUTHENTICATED"
                ) {

                    localStorage.setItem(
                        "datafence_user",
                        JSON.stringify(
                            result.user
                        )
                    );

                    setAuthenticated(true);

                } else {

                    throw new Error(
                        "Invalid session"
                    );
                }

            } catch (error) {

                console.warn(
                    "Session validation failed:",
                    error
                );

                localStorage.removeItem(
                    "datafence_token"
                );

                localStorage.removeItem(
                    "datafence_user"
                );

                setAuthenticated(false);

            } finally {

                setCheckingAuth(false);
            }
        }


        checkSession();

    }, []);


    // ========================================================
    // LOGIN
    // ========================================================

    const handleLogin = (
        token,
        user
    ) => {

        localStorage.setItem(
            "datafence_token",
            token
        );

        localStorage.setItem(
            "datafence_user",
            JSON.stringify(user)
        );

        setAuthenticated(true);
    };


    // ========================================================
    // LOGOUT
    // ========================================================

    const handleLogout = async () => {

        try {

            await logout();

        } catch (error) {

            console.warn(
                "Logout request failed:",
                error
            );

        } finally {

            localStorage.removeItem(
                "datafence_token"
            );

            localStorage.removeItem(
                "datafence_user"
            );

            setAuthenticated(false);
        }
    };


    // ========================================================
    // LOADING
    // ========================================================

    if (checkingAuth) {

        return (

            <div className="loading-screen">

                <div className="loading-logo">

                    DATAFENCE

                </div>

                <span>
                    Verifying secure session...
                </span>

            </div>

        );
    }


    // ========================================================
    // LOGIN
    // ========================================================

    if (!authenticated) {

        return (

            <Login
                onLogin={handleLogin}
            />

        );
    }


    // ========================================================
    // DASHBOARD
    // ========================================================

    return (

        <Dashboard
            onLogout={handleLogout}
        />

    );
}


export default App;