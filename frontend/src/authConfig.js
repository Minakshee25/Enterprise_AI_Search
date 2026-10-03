export const msalConfig = {
    auth: {
        clientId:
            import.meta.env.VITE_ENTRA_FRONTEND_CLIENT_ID,

        authority:
            `https://login.microsoftonline.com/${
                import.meta.env.VITE_ENTRA_TENANT_ID
            }`,

        redirectUri:
            `${window.location.origin}/redirect.html`,
    },
};


export const loginRequest = {
    scopes: [
        import.meta.env.VITE_AIASSISTANT_API_SCOPE
    ],
};