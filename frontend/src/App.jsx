import { useState } from "react";

import {
    useIsAuthenticated,
    useMsal,
} from "@azure/msal-react";

import { loginRequest } from "./authConfig";


function App() {
    const { instance, accounts } = useMsal();

    const isAuthenticated =
        useIsAuthenticated();

    const [backendUser, setBackendUser] =
        useState(null);

    const [error, setError] =
        useState(null);


    const signIn = async () => {
        try {
            setError(null);

            await instance.loginPopup(
                loginRequest
            );
        } catch (err) {
            console.error(err);
            setError(err.message);
        }
    };


    const callBackend = async () => {
        try {
            setError(null);

            const account = accounts[0];

            const tokenResponse =
                await instance.acquireTokenSilent({
                    ...loginRequest,
                    account,
                });

            const response = await fetch(
                `${
                    import.meta.env.VITE_API_BASE_URL
                }/me`,
                {
                    headers: {
                        Authorization:
                            `Bearer ${tokenResponse.accessToken}`,
                    },
                }
            );

            if (!response.ok) {
                throw new Error(
                    await response.text()
                );
            }

            const data =
                await response.json();

            setBackendUser(data);

        } catch (err) {
            console.error(err);
            setError(err.message);
        }
    };


    return (
        <div style={{ padding: "40px" }}>
            <h1>KHub</h1>

            {!isAuthenticated && (
                <button onClick={signIn}>
                    Sign in with Microsoft
                </button>
            )}

            {isAuthenticated && (
                <>
                    <p>
                        Signed in as{" "}
                        {accounts[0]?.name}
                    </p>

                    <button onClick={callBackend}>
                        Call KHub API
                    </button>
                </>
            )}

            {backendUser && (
                <pre>
                    {JSON.stringify(
                        backendUser,
                        null,
                        2
                    )}
                </pre>
            )}

            {error && (
                <pre>{error}</pre>
            )}
        </div>
    );
}


export default App;