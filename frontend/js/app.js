const enteredElem = document.getElementById("entered");
const exitedElem = document.getElementById("exited");
const currentElem = document.getElementById("current");
const alertTextElem = document.getElementById("alertText");
const historyBody = document.getElementById("historyBody");

const ws = new WebSocket("ws://127.0.0.1:8000/ws");

async function startCounter() {
    try {
        const response = await fetch("http://127.0.0.1:8000/start");
        const data = await response.json();
        console.log(data.status);
    } catch (err) {
        console.error("Erro ao iniciar contador:", err);
    }
}

window.addEventListener("DOMContentLoaded", () => {
    startCounter();
});

ws.onopen = () => {
    console.log("WebSocket conectado!");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    enteredElem.textContent = data.entered;
    exitedElem.textContent = data.exited;
    currentElem.textContent = data.current;

    if (data.alert && data.alert !== "") {
        alertTextElem.textContent = data.alert;
        alertTextElem.classList.remove("d-none");
    } else {
        alertTextElem.textContent = "";
        alertTextElem.classList.add("d-none");
    }

    // Atualiza histórico se enviado pelo backend
    if (data.history) {
        renderHistory(data.history);
    }
};

// Atualiza a tabela de histórico
function renderHistory(historyData) {
    historyBody.innerHTML = "";  // limpa a tabela

    // Exibe os últimos 25 registros
    historyData.slice(-25).reverse().forEach(record => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${record.timestamp}</td>
            <td>${record.entered}</td>
            <td>${record.exited}</td>
            <td>${record.current_people}</td>
        `;
        historyBody.appendChild(tr);
    });
}

// Carrega histórico ao abrir a página
async function loadHistory() {
    try {
        const response = await fetch("http://127.0.0.1:8000/history");
        const data = await response.json();
        renderHistory(data);
    } catch (err) {
        console.error("Erro ao carregar histórico:", err);
    }
}

loadHistory();
setInterval(loadHistory, 5000);

ws.onclose = () => {
    console.log("WebSocket fechado!");
};
