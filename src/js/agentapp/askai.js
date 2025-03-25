import $ from "jquery";

const chatForm = document.getElementById("chat-form");
const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");


if (chatForm && chatForm && userInput){
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
    
        const inputText = userInput.value.trim();
        if (!inputText) return;
        userInput.value = "";
        await sendChatMessage({"agent": "qutations_agent", "text": inputText});
    
        
    });

    $("#test-1").on("click", async (e) => {
        e.preventDefault();
        await sendChatMessage({"agent": "google_search", "text": "what is python?"});
    });
    $("#test-2").on("click", async (e) => {
        e.preventDefault();
        await sendChatMessage({"agent": "quotations", "text": "quotations"});
    });
}

async function sendChatMessage(message) {
    addMessage("user-message", message.text);

    const company_id = $("#chat-container").data("company-id");

    const dataToSend = {
        "message": message,
        "company_id": company_id,
    };

    const url = `/ask-ai/`; 
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": window.csrfToken,
        },
        body: JSON.stringify(dataToSend),
    });

    if (response.ok) {
        const data = await response.json();
        addMessage("ai-message", data.response);
    } else {
        addMessage("ai-message", "Error: Could not get a response.");
    }
}

function addMessage(className, message) {
    if (chatWindow){
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-message ${className}`;
        msgDiv.innerHTML = message;
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight; 
    }
}

