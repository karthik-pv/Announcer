const authBox = document.getElementById("auth-box");
const alertBox = document.getElementById("alert-box");
authBox.style.color = "black";

let token = null;
let isAuthenticated = false;

const password = prompt("Enter password to connect:");

if (password) {
  // Authenticate via HTTP first
  fetch("/auth", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ password }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        token = data.token;
        authBox.innerText = "Authenticated successfully.";
        authBox.style.color = "green";
        connectSocket();
      } else {
        authBox.innerText = data.error || "Authentication failed.";
        authBox.style.color = "red";
      }
    })
    .catch((err) => {
      authBox.innerText = "Error connecting to auth.";
      authBox.style.color = "red";
      console.error(err);
    });
}

function connectSocket() {
  const socket = io({ autoConnect: false });

  socket.on("connect", () => {
    console.log("Socket connected. Registering token...");
    socket.emit("register_token", { token });
    isAuthenticated = true;
  });

  socket.on("new_alert", (data) => {
    if (!isAuthenticated) return;

    const message = data.message;
    console.log("New alert received:", message);
    alertBox.innerText = message;

    const utterance = new SpeechSynthesisUtterance(message);
    speechSynthesis.speak(utterance);
  });

  socket.on("disconnect", () => {
    console.warn("Disconnected from server.");
    isAuthenticated = false;
  });

  socket.connect();
}
