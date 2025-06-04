// // frontend/script.js

// const chatWindow = document.getElementById("chat-window");
// const userInput = document.getElementById("user-input");
// const sendBtn = document.getElementById("send-btn");

// // Utility: append a message bubble
// function appendMessage(text, sender) {
//   const messageDiv = document.createElement("div");
//   messageDiv.classList.add("message", sender);
//   messageDiv.innerText = text;
//   chatWindow.appendChild(messageDiv);
//   chatWindow.scrollTop = chatWindow.scrollHeight;
// }

// // Send the user's message to the backend
// async function sendMessage() {
//   const text = userInput.value.trim();
//   if (!text) return;

//   // Append user’s message
//   appendMessage(text, "user");
//   userInput.value = "";

//   try {
//     // Call backend /chat endpoint
//     const response = await fetch("http://localhost:8000/chat", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json"
//       },
//       body: JSON.stringify({ message: text })
//     });

//     if (!response.ok) {
//       throw new Error(`Server error: ${response.status}`);
//     }

//     const data = await response.json();
//     const botReply = data.response || "No response from server.";
//     appendMessage(botReply, "bot");
//   } catch (err) {
//     console.error(err);
//     appendMessage("Error: could not reach server.", "bot");
//   }
// }

// // Send on button click
// sendBtn.addEventListener("click", sendMessage);

// // Send on Enter key
// userInput.addEventListener("keydown", (e) => {
//   if (e.key === "Enter") {
//     e.preventDefault();
//     sendMessage();
//   }
// });



// script.js

// 1) Grab references to all needed DOM elements

// Sidebar “New chat” button
const newChatBtn = document.getElementById("new-chat-btn");

// Splash elements
const splashSection = document.getElementById("chat-splash");
const splashForm = document.getElementById("splash-form");
const splashInput = document.getElementById("splash-input");

// Chat elements
const chatHeader = document.querySelector(".chat-header");
const chatArea = document.getElementById("chat-area");
const chatHistory = document.getElementById("chat-history");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendButton = chatForm.querySelector(".send-button");

// 2) Backend endpoint
const API_URL = "http://localhost:8000/chat";

// 3) Utility: scroll chat history to bottom
function scrollToBottom() {
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 4) Append a message bubble
//    role = "user" or "bot"; text = string; loading = boolean (optional)
function appendMessage(role, text, loading = false) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", role);

  const bubbleDiv = document.createElement("div");
  bubbleDiv.classList.add("bubble");
  if (loading) bubbleDiv.classList.add("loading");
  bubbleDiv.textContent = text;

  messageDiv.appendChild(bubbleDiv);
  chatHistory.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
}

// 5) Clear the current chat session and show the splash screen again
function resetToSplash() {
  // 5a. Hide chat header & chat area
  chatHeader.classList.add("hidden");
  chatArea.classList.add("hidden");

  // 5b. Show splash
  splashSection.classList.remove("hidden");

  // 5c. Clear out any old messages
  chatHistory.innerHTML = "";

  // 5d. Focus the splash input
  setTimeout(() => {
    splashInput.value = "";
    splashInput.focus();
  }, 50);
}

// 6) Show the chat area (hide splash, reveal header + chat)
function openChat(initialUserMessage) {
  // 6a. Hide splash
  splashSection.classList.add("hidden");

  // 6b. Reveal header & chat area
  chatHeader.classList.remove("hidden");
  chatArea.classList.remove("hidden");

  // 6c. Prepend the user's initial message into chat history
  if (initialUserMessage) {
    appendMessage("user", initialUserMessage);
    // Immediately send that to the backend as if user just typed it
    sendToBackend(initialUserMessage);
  }
}

// 7) Send a user message to the backend and display the bot response
async function sendToBackend(userText) {
  // 7a. Append a “loading” bubble for bot
  const botBubble = appendMessage("bot", "…", true);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText }),
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json(); // expecting { response: "..." }
    const botText = data.response || "(no response)";

    // 7b. Replace loading text with actual bot response
    const bubbleDiv = botBubble.querySelector(".bubble");
    bubbleDiv.classList.remove("loading");
    bubbleDiv.textContent = botText;
  } catch (err) {
    console.error("Error while fetching:", err);
    const bubbleDiv = botBubble.querySelector(".bubble");
    bubbleDiv.classList.remove("loading");
    bubbleDiv.textContent = "⚠️ Oops, something went wrong.";
  } finally {
    sendButton.disabled = false;
    scrollToBottom();
  }
}

// 8) Handle splash form submit (user presses Enter or clicks arrow on splash)
splashForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const userText = splashInput.value.trim();
  if (!userText) return;

  openChat(userText);
  splashInput.value = "";
});

// 9) Handle actual chat form submit (once chat is open)
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userText = chatInput.value.trim();
  if (!userText) return;

  // 9a. Append user bubble
  appendMessage("user", userText);

  // 9b. Clear input & disable button while waiting
  chatInput.value = "";
  sendButton.disabled = true;

  // 9c. Send it to backend
  await sendToBackend(userText);
});

// 10) Auto-expand textarea height as user types
chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = chatInput.scrollHeight + "px";
});

// 11) Hook up New Chat button to reset everything
newChatBtn.addEventListener("click", (e) => {
  e.preventDefault();
  resetToSplash();
});

// 12) On initial page load, ensure we start at the splash
window.addEventListener("DOMContentLoaded", () => {
  resetToSplash();
});
