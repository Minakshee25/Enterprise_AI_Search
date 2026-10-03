import { loginRequest } from "./authConfig";


const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL;


async function getAccessToken(instance, account) {
    const tokenResponse =
        await instance.acquireTokenSilent({
            ...loginRequest,
            account,
        });

    return tokenResponse.accessToken;
}


async function authorizedFetch(
    instance,
    account,
    path,
    options = {},
) {
    const accessToken =
        await getAccessToken(instance, account);

    return fetch(
        `${API_BASE_URL}${path}`,
        {
            ...options,
            headers: {
                ...options.headers,
                Authorization:
                    `Bearer ${accessToken}`,
            },
        }
    );
}


export async function listConversations(
    instance,
    account,
) {
    const response = await authorizedFetch(
        instance,
        account,
        "/api/v1/conversations",
    );

    if (!response.ok) {
        throw new Error(
            "Could not load conversations"
        );
    }

    return response.json();
}


export async function createConversation(
    instance,
    account,
) {
    const response = await authorizedFetch(
        instance,
        account,
        "/api/v1/conversations",
        {
            method: "POST",
        }
    );

    if (!response.ok) {
        throw new Error(
            "Could not create conversation"
        );
    }

    return response.json();
}


export async function getMessages(
    instance,
    account,
    conversationId,
) {
    const response = await authorizedFetch(
        instance,
        account,
        `/api/v1/conversations/${conversationId}/messages`,
    );

    if (!response.ok) {
        throw new Error(
            "Could not load messages"
        );
    }

    return response.json();
}


export async function streamMessage(
    instance,
    account,
    conversationId,
    message,
    onChunk,
) {
    const response = await authorizedFetch(
        instance,
        account,
        "/api/v1/chat/stream",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify({
                conversation_id:
                    conversationId,

                message,
            }),
        }
    );

    if (!response.ok) {
        throw new Error(
            await response.text()
        );
    }

    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder();

    while (true) {
        const { value, done } =
            await reader.read();

        if (done) {
            break;
        }

        const chunk =
            decoder.decode(
                value,
                { stream: true }
            );

        onChunk(chunk);
    }
}