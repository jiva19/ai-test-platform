let currentProjectId = null;

const projectSelect = document.getElementById("project-select");
const testCaseSection = document.getElementById("test-case-section");
const testCaseForm = document.getElementById("test-case-form");
const testCasesBody = document.querySelector("#test-cases-table tbody");
const historySection = document.getElementById("history-section");
const historyTitle = document.getElementById("history-title");
const historyBody = document.querySelector("#history-table tbody");
const statusEl = document.getElementById("run-status");

async function loadProjects() {
    const response = await fetch("/projects");
    const projects = await response.json();

    projectSelect.innerHTML = '<option value="">-- Select a project --</option>';
    projects.forEach(p => {
        const option = document.createElement("option");
        option.value = p.id;
        option.textContent = p.name;
        projectSelect.appendChild(option);
    });
}

projectSelect.addEventListener("change", () => {
    currentProjectId = projectSelect.value;
    historySection.style.display = "none";
    if (currentProjectId) {
        testCaseSection.style.display = "block";
        loadTestCases();
    } else {
        testCaseSection.style.display = "none";
    }
});

document.getElementById("create-project-button").addEventListener("click", async () => {
    const nameInput = document.getElementById("new-project-name");
    const name = nameInput.value.trim();
    if (!name) return;

    await fetch("/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });

    nameInput.value = "";
    await loadProjects();
});

document.getElementById("show-add-form-button").addEventListener("click", () => {
    testCaseForm.style.display = testCaseForm.style.display === "none" ? "block" : "none";
});

testCaseForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const body = {
        name: document.getElementById("tc-name").value,
        preconditions: document.getElementById("tc-preconditions").value.split("\n").filter(l => l.trim()),
        steps: document.getElementById("tc-steps").value.split("\n").filter(l => l.trim()),
        expected_result: document.getElementById("tc-expected-result").value
    };

    await fetch(`/projects/${currentProjectId}/test-cases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    testCaseForm.reset();
    testCaseForm.style.display = "none";
    loadTestCases();
});

async function loadTestCases() {
    const response = await fetch(`/projects/${currentProjectId}/test-cases`);
    const testCases = await response.json();

    testCasesBody.innerHTML = "";

    for (const tc of testCases) {
        const runsResponse = await fetch(`/test-cases/${tc.id}/runs`);
        const runs = await runsResponse.json();
        const lastResult = runs.length > 0 ? runs[0].result : "Never run";

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${tc.name}</td>
            <td>${resultBadge(lastResult)}</td>
            <td>
                <button onclick="runTestCase(${tc.id})">Run</button>
                <button onclick="showHistory(${tc.id}, '${tc.name}')">History</button>
            </td>
        `;
        testCasesBody.appendChild(row);
    }
}

async function runTestCase(testCaseId) {
    const response = await fetch("/run-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ test_case_id: testCaseId })
    });
    const data = await response.json();

    showHistory(testCaseId, null);
    statusEl.textContent = `Run started (id ${data.id})...`;
    pollResult(data.id, testCaseId);
}

function pollResult(runDbId, testCaseId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/results/${runDbId}`);
        const run = await response.json();

        if (run.result !== "RUNNING") {
            clearInterval(interval);
            statusEl.textContent = `Test finished: ${run.result} — ${run.reason}`;
            loadTestCases();
            showHistory(testCaseId, null);
        } else {
            statusEl.textContent = `Run ${runDbId} still running...`;
        }
    }, 3000);
}

async function showHistory(testCaseId, name) {
    historySection.style.display = "block";
    if (name) historyTitle.textContent = `Run History: ${name}`;

    const response = await fetch(`/test-cases/${testCaseId}/runs`);
    const runs = await response.json();

    historyBody.innerHTML = "";
    runs.forEach(run => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${resultBadge(run.result)}</td><td>${run.reason}</td><td>${new Date(run.timestamp).toLocaleString()}</td>`;
        historyBody.appendChild(row);
    });
}

function resultBadge(result) {
    const classes = {
        "PASS": "badge badge-pass",
        "FAIL": "badge badge-fail",
        "BLOCKED": "badge badge-blocked",
        "RUNNING": "badge badge-running",
        "Never run": "badge badge-neutral"
    };
    return `<span class="${classes[result] || 'badge badge-neutral'}">${result}</span>`;
}


loadProjects();
