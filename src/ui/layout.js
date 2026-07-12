import { BOARD_OPTIONS, CLIMBS_BY_BOARD } from "./climbFixtures.js";

const ANGLES = [30, 35, 40, 45, 50, 55, 60];

export function createLayout(){
    document.body.innerHTML = `
        <div id="setup-screen">
            <header class="app-header">
                <div>
                    <div class="brand">Climb Motion</div>
                    <div class="subtitle">Attempt analysis prototype</div>
                </div>
                <div class="prototype-badge">Local prototype</div>
            </header>

            <main class="setup-main">
                <form id="attempt-form" class="setup-form" novalidate>
                    <div class="form-heading">
                        <div class="step-label">New attempt</div>
                        <h1>Set up your climb</h1>
                        <p>Choose one video and the board configuration used for the attempt.</p>
                    </div>

                    <div class="field-group">
                        <label class="field-label" for="attempt-video">Attempt video</label>
                        <label class="video-picker" for="attempt-video">
                            <span class="video-picker-action">Choose video</span>
                            <span id="video-file-name" class="video-file-name">MP4 from your camera roll</span>
                        </label>
                        <input id="attempt-video" class="visually-hidden" type="file" accept="video/mp4,video/*" />
                        <div id="video-error" class="field-error"></div>
                    </div>

                    <div class="form-grid">
                        <div class="field-group">
                            <label class="field-label" for="board-select">Board</label>
                            <select id="board-select" required>
                                <option value="">Select a board</option>
                                ${BOARD_OPTIONS.map((board) => `
                                    <option value="${board.id}">${board.label}</option>
                                `).join("")}
                            </select>
                            <div id="board-error" class="field-error"></div>
                        </div>

                        <div class="field-group">
                            <label class="field-label" for="angle-select">Angle</label>
                            <select id="angle-select" required>
                                <option value="">Select an angle</option>
                                ${ANGLES.map((angle) => `
                                    <option value="${angle}">${angle}&deg;</option>
                                `).join("")}
                            </select>
                            <div id="angle-error" class="field-error"></div>
                        </div>
                    </div>

                    <div class="field-group climb-field">
                        <label class="field-label" for="climb-input">Climb</label>
                        <div class="autocomplete">
                            <input
                                id="climb-input"
                                type="text"
                                placeholder="Select a board, then search climbs"
                                autocomplete="off"
                                disabled
                                aria-autocomplete="list"
                                aria-controls="climb-options"
                            />
                            <div id="climb-options" class="autocomplete-options" role="listbox" hidden></div>
                        </div>
                        <div class="field-hint">Prototype climb data is filtered to the selected board.</div>
                        <div id="climb-error" class="field-error"></div>
                    </div>

                    <div id="form-status" class="form-status" aria-live="polite"></div>
                    <button class="primary-button" type="submit">Analyze attempt</button>
                </form>
            </main>
        </div>

        <div id="app-shell" hidden>
            <header id="topbar">
                <div>
                    <div class="brand">Climb Motion</div>
                    <div class="subtitle">Attempt analysis</div>
                </div>
                <div class="topbar-actions">
                    <div class="session-meta">
                        <span id="session-board"></span>
                        <span id="session-angle"></span>
                        <span id="session-climb"></span>
                    </div>
                    <button id="new-attempt-button" class="secondary-button" type="button">New attempt</button>
                </div>
            </header>

            <aside id="sidebar">
                <section class="panel-section">
                    <div class="section-label">Attempt</div>
                    <div class="attempt-row">
                        <span class="attempt-color"></span>
                        <div class="attempt-copy">
                            <strong>Attempt 1</strong>
                            <span id="attempt-file-name"></span>
                        </div>
                    </div>
                </section>

                <section class="panel-section">
                    <div class="section-label">Board Setup</div>
                    <div class="detail-row"><span>Board</span><strong id="detail-board"></strong></div>
                    <div class="detail-row"><span>Angle</span><strong id="detail-angle"></strong></div>
                    <div class="detail-row"><span>Climb</span><strong id="detail-climb"></strong></div>
                </section>

                <div class="prototype-note">This preview reuses the current generated motion data. The uploaded video is not processed yet.</div>
            </aside>

            <main id="viewer">
                <div class="viewer-label">Reconstruction preview</div>
            </main>

            <footer id="timeline">
                <button class="control-button" type="button">Play</button>
                <input class="timeline-range" type="range" min="0" max="100" value="0" />
                <div class="timeline-meta">Frame 0</div>
            </footer>
        </div>
    `;

    const elements = getElements();
    setupVideoPicker(elements);
    setupClimbAutocomplete(elements);

    return {
        viewer: elements.viewer,
        onAnalyze(callback) {
            elements.form.addEventListener("submit", (event) => {
                event.preventDefault();
                const selection = validateForm(elements);

                if (selection) {
                    callback(selection);
                }
            });
        },
        showAnalysis(selection) {
            updateAnalysisDetails(elements, selection);
            elements.setupScreen.hidden = true;
            elements.appShell.hidden = false;
        },
        showSetup() {
            elements.appShell.hidden = true;
            elements.setupScreen.hidden = false;
        },
        setStatus(message) {
            elements.formStatus.textContent = message;
        }
    };
}

function getElements() {
    return {
        setupScreen: document.getElementById("setup-screen"),
        appShell: document.getElementById("app-shell"),
        viewer: document.getElementById("viewer"),
        form: document.getElementById("attempt-form"),
        videoInput: document.getElementById("attempt-video"),
        videoFileName: document.getElementById("video-file-name"),
        boardSelect: document.getElementById("board-select"),
        angleSelect: document.getElementById("angle-select"),
        climbInput: document.getElementById("climb-input"),
        climbOptions: document.getElementById("climb-options"),
        formStatus: document.getElementById("form-status"),
        newAttemptButton: document.getElementById("new-attempt-button")
    };
}

function setupVideoPicker(elements) {
    elements.videoInput.addEventListener("change", () => {
        const file = elements.videoInput.files?.[0];
        elements.videoFileName.textContent = file?.name ?? "MP4 from your camera roll";
        clearError("video");
    });
}

function setupClimbAutocomplete(elements) {
    const renderOptions = () => {
        const climbs = CLIMBS_BY_BOARD[elements.boardSelect.value] ?? [];
        const query = elements.climbInput.value.trim().toLowerCase();
        const matches = climbs
            .filter((climb) => climb.toLowerCase().includes(query))
            .slice(0, 6);

        elements.climbOptions.replaceChildren();

        for (const climb of matches) {
            const option = document.createElement("button");
            option.type = "button";
            option.className = "autocomplete-option";
            option.textContent = climb;
            option.setAttribute("role", "option");
            option.addEventListener("click", () => {
                elements.climbInput.value = climb;
                elements.climbOptions.hidden = true;
                clearError("climb");
            });
            elements.climbOptions.appendChild(option);
        }

        elements.climbOptions.hidden = matches.length === 0;
    };

    elements.boardSelect.addEventListener("change", () => {
        const hasBoard = Boolean(elements.boardSelect.value);
        elements.climbInput.disabled = !hasBoard;
        elements.climbInput.placeholder = hasBoard
            ? "Type a climb name"
            : "Select a board, then search climbs";
        elements.climbInput.value = "";
        elements.climbOptions.hidden = true;
        clearError("board");
        clearError("climb");
    });

    elements.angleSelect.addEventListener("change", () => clearError("angle"));
    elements.climbInput.addEventListener("input", renderOptions);
    elements.climbInput.addEventListener("focus", renderOptions);
    document.addEventListener("click", (event) => {
        if (!event.target.closest(".autocomplete")) {
            elements.climbOptions.hidden = true;
        }
    });
}

function validateForm(elements) {
    const file = elements.videoInput.files?.[0];
    const boardId = elements.boardSelect.value;
    const angle = Number(elements.angleSelect.value);
    const climb = elements.climbInput.value.trim();
    const boardClimbs = CLIMBS_BY_BOARD[boardId] ?? [];
    const matchedClimb = boardClimbs.find(
        (candidate) => candidate.toLowerCase() === climb.toLowerCase()
    );

    setError("video", file ? "" : "Choose one video to continue.");
    setError("board", boardId ? "" : "Select a board.");
    setError("angle", angle ? "" : "Select an angle.");
    setError("climb", matchedClimb ? "" : "Choose a climb from the matching board list.");

    if (!file || !boardId || !angle || !matchedClimb) {
        return null;
    }

    const board = BOARD_OPTIONS.find((candidate) => candidate.id === boardId);
    return {
        fileName: file.name,
        boardId,
        boardLabel: board.label,
        angle,
        climb: matchedClimb
    };
}

function updateAnalysisDetails(elements, selection) {
    const values = {
        "session-board": selection.boardLabel,
        "session-angle": `${selection.angle}°`,
        "session-climb": selection.climb,
        "attempt-file-name": selection.fileName,
        "detail-board": selection.boardLabel,
        "detail-angle": `${selection.angle}°`,
        "detail-climb": selection.climb
    };

    for (const [id, value] of Object.entries(values)) {
        document.getElementById(id).textContent = value;
    }
}

function setError(field, message) {
    document.getElementById(`${field}-error`).textContent = message;
}

function clearError(field) {
    setError(field, "");
}
