import {
    useEffect,
    useState,
} from "react";

import {
    useIsAuthenticated,
    useMsal,
} from "@azure/msal-react";

import { loginRequest } from "./authConfig";

import {
    createConversation,
    getMessages,
    listConversations,
    streamMessage,
} from "./api";

import "./App.css";


function App() {
    const { instance, accounts } =
        useMsal();

    const isAuthenticated =
        useIsAuthenticated();

    const account = accounts[0];

    const [
        conversations,
        setConversations,
    ] = useState([]);

    const [
        selectedConversationId,
        setSelectedConversationId,
    ] = useState(null);

    const [
        messages,
        setMessages,
    ] = useState([]);

    const [input, setInput] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState(null);


    const signIn = async () => {
        try {
            setError(null);

            await instance.loginPopup(
                loginRequest
            );

        } catch (err) {
            setError(err.message);
        }
    };


    const signOut = async () => {
        await instance.logoutPopup();
    };


    const loadConversations =
        async () => {

        if (!account) {
            return;
        }

        try {
            const data =
                await listConversations(
                    instance,
                    account,
                );

            setConversations(data);

        } catch (err) {
            setError(err.message);
        }
    };


    useEffect(() => {
        if (isAuthenticated && account) {
            loadConversations();
        }
    }, [
        isAuthenticated,
        account,
    ]);


    const startNewConversation =
        async () => {

        try {
            setError(null);

            const result =
                await createConversation(
                    instance,
                    account,
                );

            const conversationId =
                result.conversation_id;

            setSelectedConversationId(
                conversationId
            );

            setMessages([]);

            await loadConversations();

        } catch (err) {
            setError(err.message);
        }
    };


    const openConversation =
        async (conversationId) => {

        try {
            setError(null);

            setSelectedConversationId(
                conversationId
            );

            const data =
                await getMessages(
                    instance,
                    account,
                    conversationId,
                );

            setMessages(data);

        } catch (err) {
            setError(err.message);
        }
    };


    const sendMessage = async () => {
        const text = input.trim();

        if (!text || loading) {
            return;
        }

        try {
            setLoading(true);
            setError(null);
            setInput("");

            let conversationId =
                selectedConversationId;

            if (!conversationId) {
                const created =
                    await createConversation(
                        instance,
                        account,
                    );

                conversationId =
                    created.conversation_id;

                setSelectedConversationId(
                    conversationId
                );
            }


            setMessages(
                previous => [
                    ...previous,
                    {
                        role: "user",
                        content: text,
                    },
                    {
                        role: "assistant",
                        content: "",
                    },
                ]
            );


            await streamMessage(
                instance,
                account,
                conversationId,
                text,

                chunk => {
                    setMessages(
                        previous => {

                            const updated =
                                [...previous];

                            const lastIndex =
                                updated.length - 1;

                            updated[lastIndex] = {
                                ...updated[lastIndex],

                                content:
                                    updated[lastIndex]
                                        .content +
                                    chunk,
                            };

                            return updated;
                        }
                    );
                },
            );

            await loadConversations();

        } catch (err) {
            setError(err.message);

        } finally {
            setLoading(false);
        }
    };


    const handleKeyDown = event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            sendMessage();
        }
    };


    if (!isAuthenticated) {
        return (
            <div className="login-page">
                <div className="login-card">
                    <h1>KHub</h1>

                    <p>
                        Enterprise Knowledge Hub
                    </p>

                    <button onClick={signIn}>
                        Sign in with Microsoft
                    </button>
                </div>
            </div>
        );
    }


    return (
        <div className="app">

            <aside className="sidebar">

                <div className="sidebar-header">
                    <h2>KHub</h2>
                </div>

                <button
                    className="new-chat"
                    onClick={
                        startNewConversation
                    }
                >
                    + New Chat
                </button>

                <div className="conversation-list">

                    {conversations.map(
                        conversation => (

                        <button
                            key={
                                conversation
                                    .conversation_id
                            }

                            className={
                                selectedConversationId ===
                                conversation
                                    .conversation_id
                                    ? "conversation active"
                                    : "conversation"
                            }

                            onClick={() =>
                                openConversation(
                                    conversation
                                        .conversation_id
                                )
                            }
                        >
                            {
                                conversation.title
                            }
                        </button>
                    ))}

                </div>

                <div className="user-section">
                    <div>
                        {account?.name}
                    </div>

                    <button
                        onClick={signOut}
                    >
                        Sign out
                    </button>
                </div>

            </aside>


            <main className="chat">

                <div className="messages">

                    {messages.length === 0 && (
                        <div className="welcome">
                            <h1>
                                How can KHub help?
                            </h1>

                            <p>
                                Ask about policies,
                                procedures or internal
                                knowledge.
                            </p>
                        </div>
                    )}


                    {messages.map(
                        (message, index) => (

                        <div
                            key={index}

                            className={
                                `message ${
                                    message.role
                                }`
                            }
                        >
                            <div className="message-content">
                                {message.content}
                            </div>
                        </div>
                    ))}

                </div>


                <div className="input-area">

                    <textarea
                        value={input}

                        onChange={event =>
                            setInput(
                                event.target.value
                            )
                        }

                        onKeyDown={
                            handleKeyDown
                        }

                        placeholder="Ask KHub about a policy..."

                        disabled={loading}
                    />

                    <button
                        onClick={sendMessage}
                        disabled={
                            loading ||
                            !input.trim()
                        }
                    >
                        {loading
                            ? "..."
                            : "Send"}
                    </button>

                </div>

                {error && (
                    <div className="error">
                        {error}
                    </div>
                )}

            </main>

        </div>
    );
}


export default App;