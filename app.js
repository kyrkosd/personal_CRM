const API_URL = "http://localhost:8000";
let currentClientId = null;
let currentClientName = "";  

document.getElementById("add-client-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const clientData = {
        name: document.getElementById("name").value,
        tag: document.getElementById("tag").value,
        email: document.getElementById("email").value,
        telephone: document.getElementById("telephone").value
    };

    await fetch(`${API_URL}/clients/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(clientData)
    });
    
    e.target.reset();
    loadClients();
});

async function loadClients() {
    const response = await fetch(`${API_URL}/clients/`);
    const clients = await response.json();
    const list = document.getElementById("clients-list");
    list.innerHTML = "";
    
    clients.forEach(client => {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${client.name}</strong> <span>[${client.tag}]</span>`;
        li.onclick = () => loadCorrespondence(client.id, client.name);
        list.appendChild(li);
    });
}

async function loadCorrespondence(clientId, clientName) {
    currentClientId = clientId;
    currentClientName = clientName;
    
    document.getElementById("correspondence-section").style.display = "block";
    document.getElementById("active-client-name").textContent = `Correspondence: ${clientName}`;
    
    const response = await fetch(`${API_URL}/clients/${clientId}/correspondence/`);
    const messages = await response.json();
    
    const messagesDiv = document.getElementById("messages");
    messagesDiv.innerHTML = "";
    
    messages.forEach(msg => {
        const div = document.createElement("div");
        div.className = "message";
        const date = new Date(msg.timestamp).toLocaleString();
        div.innerHTML = `<strong>${msg.sender.toUpperCase()}</strong> <small>(${date})</small><br>${msg.message}`;
        messagesDiv.appendChild(div);
    });
}

document.getElementById("add-message-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!currentClientId) return;

    const msgData = {
        message: document.getElementById("message-content").value,
        sender: document.getElementById("message-sender").value
    };

    await fetch(`${API_URL}/clients/${currentClientId}/correspondence/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(msgData)
    });

    e.target.reset();
    loadCorrespondence(currentClientId, currentClientName);
});

// Initialization
loadClients();
