/**
 * OSINT 100X ULTIMATE — Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            const icon = this.querySelector('i');
            if (document.body.classList.contains('light-theme')) {
                icon.className = 'fas fa-sun';
            } else {
                icon.className = 'fas fa-moon';
            }
        });
    }

    // Auto-focus search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.focus();
    }

    // Keyboard shortcut: Ctrl+K to focus search
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const input = document.getElementById('searchInput');
            if (input) { input.focus(); input.select(); }
        }
        if (e.key === 'Escape') {
            const input = document.getElementById('searchInput');
            if (input) { input.value = ''; input.focus(); }
        }
    });
});

function esc(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setQuery(value) {
    const input = document.getElementById('searchInput');
    if (input) {
        input.value = value;
        performSearch();
    }
}

function performSearch() {
    const input = document.getElementById('searchInput');
    if (!input) return;

    const query = input.value.trim();
    if (!query) return;

    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');

    if (loading) loading.style.display = 'block';
    if (results) results.innerHTML = '';
    if (error) error.style.display = 'none';

    fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        if (loading) loading.style.display = 'none';
        if (data.error) {
            if (error) {
                error.innerHTML = '❌ ' + data.error;
                error.style.display = 'block';
            }
            return;
        }
        updateStats(data);
        renderResults(data);
        addToHistory(data);
    })
    .catch(err => {
        if (loading) loading.style.display = 'none';
        if (error) {
            error.innerHTML = '❌ ' + err.message;
            error.style.display = 'block';
        }
    });
}

function updateStats(data) {
    const elements = {
        totalSearches: data.total_sources || 0,
        totalRecords: data.total_records || 0,
        apiCalls: data.response_time ? 1 : 0,
        searchesUsed: data.total_records || 0,
        quickTotal: data.total_sources || 0,
        quickRecords: data.total_records || 0
    };

    for (const [id, value] of Object.entries(elements)) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        const pct = Math.min((data.total_records || 0) / 100 * 100, 100);
        progressBar.style.width = pct + '%';
    }

    const planEl = document.getElementById('userPlan');
    if (planEl && data.tier) {
        planEl.textContent = data.tier.charAt(0).toUpperCase() + data.tier.slice(1);
    }
}

function renderResults(data) {
    const container = document.getElementById('results');
    if (!container) return;

    let html = `
        <div class="result-card">
            <h3>🎯 Results for <span style="color:#7c3aed;">${esc(data.query)}</span></h3>
            <div style="font-size:13px;color:rgba(255,255,255,0.2);">
                Type: ${data.type.toUpperCase()} • ${data.response_time}ms • ${data.timestamp}
            </div>
        </div>
    `;

    if (data.sources && data.sources.length) {
        data.sources.forEach(source => {
            html += `
                <div class="result-card">
                    <h3>${source.platform_emoji || '📢'} ${esc(source.title)}</h3>
                    ${source.description ? `<div class="desc">${esc(source.description)}</div>` : ''}
                    ${source.fields.map(f => `
                        <div class="field">
                            <span class="lbl">${f.emoji} ${esc(f.label)}</span>
                            <span class="val">${esc(f.value)}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        });
    } else {
        html += `
            <div class="result-card" style="text-align:center;padding:40px;">
                <span style="font-size:48px;">🛡️</span>
                <p style="color:rgba(255,255,255,0.2);margin-top:8px;">No records found. Clean result.</p>
            </div>
        `;
    }

    container.innerHTML = html;
}

function addToHistory(data) {
    const historyItem = {
        query: data.query,
        type: data.type,
        records: data.total_records || 0,
        timestamp: data.timestamp || 'Just now'
    };

    const tbody = document.getElementById('historyTable');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr');
    if (rows.length === 1 && rows[0].querySelector('td[colspan]')) {
        tbody.innerHTML = '';
    }

    const statusClass = historyItem.records > 0 ? 'found' : 'empty';
    const statusText = historyItem.records > 0 ? 'Found' : 'No Results';
    const html = `
        <tr>
            <td><code style="background:rgba(255,255,255,0.03);padding:2px 8px;border-radius:4px;font-size:12px;">${esc(historyItem.query)}</code></td>
            <td>${esc(historyItem.type)}</td>
            <td>${historyItem.records}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td style="color:rgba(255,255,255,0.2);font-size:12px;">${esc(historyItem.timestamp)}</td>
        </tr>
    `;
    tbody.insertAdjacentHTML('afterbegin', html);

    while (tbody.querySelectorAll('tr').length > 5) {
        tbody.removeChild(tbody.lastChild);
    }
      }
