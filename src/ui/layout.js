export function createLayout(){
    document.body.innerHTML = `
        <div id="app-shell">
            <header id="topbar">
                <div>
                    <div class="brand">Climb Motion</div>
                    <div class="subtitle">Attempt comparison prototype</div>
                </div>
                <div class="session-meta">
                    <span>MoonBoard</span>
                    <span>40&deg;</span>
                    <span>Prototype Climb</span>
                </div>
            </header>

            <aside id="sidebar">
                <section class="panel-section">
                    <div class="section-label">Attempts</div>
                    <button class="upload-button" type="button">Upload videos</button>
                    <div class="attempt-list">
                        <div class="attempt-row">
                            <span class="attempt-color attempt-color-primary"></span>
                            <span>Attempt 1</span>
                        </div>
                        <div class="attempt-row muted">
                            <span class="attempt-color attempt-color-secondary"></span>
                            <span>Attempt 2</span>
                        </div>
                        <div class="attempt-row muted">
                            <span class="attempt-color attempt-color-tertiary"></span>
                            <span>Attempt 3</span>
                        </div>
                    </div>
                </section>

                <section class="panel-section">
                    <div class="section-label">Board Setup</div>
                    <div class="detail-row"><span>Board</span><strong>MoonBoard</strong></div>
                    <div class="detail-row"><span>Angle</span><strong>40&deg;</strong></div>
                    <div class="detail-row"><span>Calibration</span><strong>Placeholder</strong></div>
                </section>
            </aside>

            <main id="viewer">
                <div class="viewer-label">Board-relative reconstruction</div>
            </main>

            <footer id="timeline">
                <button class="control-button" type="button">Play</button>
                <input class="timeline-range" type="range" min="0" max="100" value="0" />
                <div class="timeline-meta">Frame 0</div>
            </footer>
        </div>
    `;

    return {
        viewer: document.getElementById("viewer")
    };
}
