let currentIndustry = 'Hollywood';
let currentSessionId = 'web_session_' + Date.now();

function setIndustry(industry, btnElement) {
    currentIndustry = industry;
    document.querySelectorAll('.ind-btn').forEach(btn => btn.classList.remove('active'));
    btnElement.classList.add('active');
}

function updateYearLabel() {
    const start = document.getElementById('startYear').value;
    const end = document.getElementById('endYear').value;
    document.getElementById('yearRangeVal').innerText = `${start} - ${end}`;
}

async function handleFormSubmit(event) {
    event.preventDefault();

    const genre = document.getElementById('genreSelect').value;
    const startYear = parseInt(document.getElementById('startYear').value);
    const endYear = parseInt(document.getElementById('endYear').value);

    if (startYear > endYear) {
        alert("Start Year cannot be greater than End Year.");
        return;
    }

    // UI Loading state
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('loader').classList.remove('hidden');
    document.getElementById('submitBtn').disabled = true;

    const requestPayload = {
        genre: genre,
        industry: currentIndustry,
        start_year: startYear,
        end_year: endYear,
        limit: 10,
        user_session_id: currentSessionId
    };

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestPayload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to fetch recommendations.');
        }

        const data = await response.json();
        renderResults(data);
    } catch (err) {
        alert(`Error: ${err.message}`);
    } finally {
        document.getElementById('loader').classList.add('hidden');
        document.getElementById('submitBtn').disabled = false;
    }
}

function renderResults(data) {
    const grid = document.getElementById('movieGrid');
    grid.innerHTML = '';

    document.getElementById('resultsTitle').innerText = `🏆 Top 10 ${data.genre} Movies in ${data.industry} (${data.year_range})`;
    document.getElementById('executionBadge').innerText = `⚡ Executed in ${data.execution_time_ms} ms`;

    data.movies.forEach((movie, index) => {
        const card = document.createElement('div');
        card.className = 'movie-card';

        const posterImg = movie.poster_url 
            ? `<img src="${movie.poster_url}" alt="${movie.title}" class="movie-poster" onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">`
            : `<div class="poster-placeholder">🎬</div>`;

        const providersHtml = movie.watch_providers.map(p => 
            `<span class="provider-chip">📺 ${p.provider_name}</span>`
        ).join('');

        card.innerHTML = `
            <div class="poster-container">
                ${posterImg}
                <div class="rank-badge">#${index + 1}</div>
                <div class="rating-badge">⭐ ${movie.rating}/10</div>
            </div>
            <div class="movie-info">
                <div class="movie-title">${movie.title}</div>
                <div class="movie-meta">
                    <span>📅 ${movie.release_year}</span>
                    <span>• Quality Score: <strong>${movie.composite_score}/100</strong></span>
                </div>
                <p class="movie-synopsis">${movie.synopsis}</p>
                <div class="agent-reasoning-box">
                    <strong>🤖 Agent Insight:</strong> ${movie.agent_reasoning}
                </div>
                <div class="provider-chips">
                    ${providersHtml}
                </div>
            </div>
        `;
        grid.appendChild(card);
    });

    document.getElementById('resultsSection').classList.remove('hidden');
}

async function toggleTraceModal() {
    const modal = document.getElementById('traceModal');
    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        await fetchAndRenderTraces();
    } else {
        modal.classList.add('hidden');
    }
}

async function fetchAndRenderTraces() {
    const traceBody = document.getElementById('traceContent');
    traceBody.innerHTML = '<p>Loading agent trace steps...</p>';

    try {
        const res = await fetch(`/api/trace/${currentSessionId}`);
        const data = await res.json();

        if (!data.steps || data.steps.length === 0) {
            traceBody.innerHTML = '<p>No trace steps recorded for this session yet. Run a search query to generate traces.</p>';
            return;
        }

        let html = '';
        data.steps.forEach(step => {
            html += `
                <div class="trace-step-item">
                    <div><span class="trace-agent-name">[Step ${step.step_number}] ${step.agent_name}</span> &rarr; Action: <code>${step.action}</code></div>
                    <div><small style="color:#9ca3af;">Latency: ${step.latency_ms} ms | Timestamp: ${step.timestamp}</small></div>
                    <pre style="margin-top:0.5rem; color:#e2e8f0; font-size:0.75rem;">Inputs: ${JSON.stringify(step.inputs, null, 2)}\nOutputs: ${JSON.stringify(step.outputs, null, 2)}</pre>
                </div>
            `;
        });
        traceBody.innerHTML = html;
    } catch (err) {
        traceBody.innerHTML = `<p style="color:#ef4444;">Failed to load traces: ${err.message}</p>`;
    }
}
