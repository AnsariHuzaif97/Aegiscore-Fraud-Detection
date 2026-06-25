function switchTab(tabId) {
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
    document.querySelector(`.nav-links li[onclick="switchTab('${tabId}')"]`).classList.add('active');
    
    document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');

    const titles = {
        'dashboard': 'Command Center',
        'investigation': 'Investigation Center',
        'audit': 'Global Transaction Audit',
        'batch': 'Batch Telemetry Processor',
        'explainability': 'Explainability Hub'
    };
    document.getElementById('page-title').innerText = titles[tabId];

    if (tabId === 'audit') loadAuditTable();
}

async function loadDashboardStats() {
    try {
        const stats = await FraudAPI.getStats();
        document.getElementById('stat-alerts').innerText = stats.activeAlerts;
        document.getElementById('stat-scanned').innerText = stats.transactionsScanned;
        document.getElementById('stat-savings').innerText = stats.financialSavings;
        document.getElementById('stat-health').innerText = stats.anomalyRatio || stats.systemHealth;
        
        if (stats.chartData) {
            initCharts(stats.chartData);
        }
    } catch (e) {
        console.error("Error fetching stats", e);
    }
}

async function runPrediction() {
    const payload = { features: {} };
    payload.features["Time"] = parseFloat(document.getElementById('inp-Time').value) || 0;
    payload.features["Amount"] = parseFloat(document.getElementById('inp-Amount').value) || 0;
    
    for (let i = 1; i <= 28; i++) {
        const el = document.getElementById(`inp-V${i}`);
        if(el) {
            payload.features[`V${i}`] = parseFloat(el.value) || 0.0;
        }
    }
    
    // UI Loading state
    const btn = document.querySelector('button');
    btn.innerText = "Processing Telemetry...";
    
    try {
        const res = await FraudAPI.predictFraud(payload);
        
        if (res.error) {
            throw new Error(res.error + "\n\nTraceback:\n" + res.traceback);
        }
        
        // Update Risk Gauge & Text
        const probPct = (res.fraudProbability * 100).toFixed(1);
        document.getElementById('risk-prob').innerText = `${probPct}%`;
        
        const gauge = document.getElementById('risk-gauge-fill');
        gauge.style.width = `${probPct}%`;
        
        const badge = document.getElementById('risk-badge');
        badge.innerText = res.riskLevel;
        if (res.riskLevel === 'CRITICAL' || res.riskLevel === 'HIGH') {
            gauge.style.background = '#ff0055';
            badge.style.background = 'rgba(255, 0, 85, 0.2)';
            badge.style.color = '#ff0055';
        } else {
            gauge.style.background = '#00e676';
            badge.style.background = 'rgba(0, 230, 118, 0.2)';
            badge.style.color = '#00e676';
        }

        // Render SHAP Force Plot equivalent
        renderSHAP(res.shapValues, res.riskLevel);
        
        // Refresh dashboard stats so alerts go up if critical
        loadDashboardStats();
    } catch (e) {
        console.error(e);
        alert("API Error:\n" + e.message);
    } finally {
        btn.innerText = "Execute Model Inference";
    }
}

function renderSHAP(shapDict, riskLevel) {
    const container = document.getElementById('shap-container');
    container.innerHTML = '';
    
    // Find max absolute value to scale bars properly
    let maxAbs = 0;
    for (const val of Object.values(shapDict)) {
        if (Math.abs(val) > maxAbs) maxAbs = Math.abs(val);
    }
    if (maxAbs === 0) maxAbs = 1;

    let topPosFeat = null;
    let topNegFeat = null;
    let maxPos = -9999;
    let minNeg = 9999;

    for (const [feat, val] of Object.entries(shapDict)) {
        const row = document.createElement('div');
        row.className = 'shap-row';
        
        const isPos = val > 0;
        if (isPos && val > maxPos) { maxPos = val; topPosFeat = feat; }
        if (!isPos && val < minNeg) { minNeg = val; topNegFeat = feat; }
        
        const color = isPos ? '#ff0055' : '#00e5ff';
        // Scale width relative to max absolute value (up to 95% of half-width)
        const widthPct = (Math.abs(val) / maxAbs) * 95; 
        
        let barHtml = '';
        if (isPos) {
            barHtml = `
                <div class="shap-bar-left-container"></div>
                <div class="shap-bar-right-container"><div class="shap-bar positive" style="width: ${widthPct}%"></div></div>
            `;
        } else {
            barHtml = `
                <div class="shap-bar-left-container"><div class="shap-bar negative" style="width: ${widthPct}%"></div></div>
                <div class="shap-bar-right-container"></div>
            `;
        }
        
        row.innerHTML = `
            <div class="shap-label">${feat}</div>
            <div class="shap-bar-wrapper">
                <div class="shap-center-line"></div>
                ${barHtml}
            </div>
            <div class="shap-val" style="color: ${color}">${val > 0 ? '+' : ''}${val.toFixed(3)}</div>
        `;
        container.appendChild(row);
    }
    
    // Generate AI Explanation
    const explDiv = document.getElementById('ai-explanation');
    const explText = document.getElementById('ai-explanation-text');
    explDiv.style.display = 'block';
    
    if (riskLevel === 'CRITICAL' || riskLevel === 'HIGH') {
        explDiv.style.borderLeftColor = '#ff0055';
        explText.innerHTML = `The pipeline flags this as <strong>fraudulent</strong>. The primary driver is <span style="color:#ff0055; font-weight:bold;">${topPosFeat || 'Amount'}</span>, which drastically increases the anomaly score. Immediate interdiction is recommended.`;
    } else {
        explDiv.style.borderLeftColor = '#00e5ff';
        explText.innerHTML = `The pipeline verifies this as <strong>genuine</strong>. Factors like <span style="color:#00e5ff; font-weight:bold;">${topNegFeat || 'V14'}</span> strongly anchor the transaction within normal behavioral boundaries, overpowering any slight anomalies.`;
    }
}

async function loadAuditTable() {
    try {
        const txs = await FraudAPI.getTransactions();
        const tbody = document.getElementById('audit-table-body');
        tbody.innerHTML = '';
        
        txs.forEach(tx => {
            const tr = document.createElement('tr');
            const d = new Date(tx.timestamp);
            const timeStr = `${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
            const color = tx.risk_level === 'CRITICAL' || tx.risk_level === 'HIGH' ? '#ff0055' : '#00e676';
            
            tr.innerHTML = `
                <td style="color: #94a3b8">${tx.id.split('-')[0]}</td>
                <td>${timeStr}</td>
                <td>₹${tx.amount.toFixed(2)}</td>
                <td>${(tx.probability * 100).toFixed(1)}%</td>
                <td><span class="badge" style="background: ${color}22; color: ${color}">${tx.risk_level}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
    }
}

let myChart = null;
function initCharts(data) {
    const ctx = document.getElementById('volumeChart');
    if(!ctx || !data || data.length === 0) return;
    
    if(myChart) myChart.destroy();

    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
            datasets: [{
                label: 'Transactions',
                data: data,
                backgroundColor: [
                    'rgba(0, 230, 118, 0.7)', 'rgba(0, 230, 118, 0.4)', 'rgba(0, 230, 118, 0.2)',
                    'rgba(255, 255, 255, 0.1)', 'rgba(255, 255, 255, 0.1)',
                    'rgba(255, 145, 0, 0.2)', 'rgba(255, 145, 0, 0.4)', 'rgba(255, 145, 0, 0.7)',
                    'rgba(255, 0, 85, 0.6)', 'rgba(255, 0, 85, 0.9)'
                ],
                borderColor: [
                    '#00e676', '#00e676', '#00e676',
                    'rgba(255,255,255,0.2)', 'rgba(255,255,255,0.2)',
                    '#ff9100', '#ff9100', '#ff9100',
                    '#ff0055', '#ff0055'
                ],
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.raw} Transactions`;
                        }
                    }
                }
            },
            scales: {
                y: { 
                    title: { display: true, text: 'Transaction Volume', color: '#94a3b8' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' },
                    beginAtZero: true
                },
                x: { 
                    title: { display: true, text: 'Fraud Probability Bucket', color: '#94a3b8' },
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    loadDashboardStats();
});

async function processBatch() {
    const fileInput = document.getElementById('csv-file');
    if (!fileInput.files[0]) return;
    
    const btn = document.getElementById('batch-btn');
    btn.innerText = "Ingesting Telemetry Pipeline...";
    btn.disabled = true;
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    
    try {
        const response = await fetch('/api/batch-predict', {
            method: 'POST',
            body: formData
        });
        
        let res;
        try {
            res = await response.json();
        } catch (err) {
            throw new Error(`Server returned status ${response.status}: Failed to parse JSON response. Ensure python-multipart is installed.`);
        }
        
        if (response.status === 422) {
            throw new Error("Validation Error (422): FastAPI requires 'python-multipart' to process file uploads. Please run: pip install python-multipart");
        }
        
        if (res.error || res.detail) throw new Error(res.error || JSON.stringify(res.detail));
        
        document.getElementById('batch-total').innerText = res.totalProcessed.toLocaleString();
        document.getElementById('batch-fraud').innerText = res.fraudDetected.toLocaleString();
        document.getElementById('batch-saved').innerText = '₹' + res.capitalSaved.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        const thead = document.getElementById('batch-table-header');
        if (thead && thead.children.length === 4) {
            for(let i=1; i<=28; i++) {
                const th = document.createElement('th');
                th.innerText = `V${i}`;
                th.style.color = '#94a3b8';
                thead.appendChild(th);
            }
        }

        const tbody = document.getElementById('batch-table-body');
        tbody.innerHTML = '';
        
        res.flaggedTransactions.forEach(tx => {
            const tr = document.createElement('tr');
            const probPct = (tx.probability * 100).toFixed(5);
            const risk = tx.probability > 0.8 ? 'CRITICAL' : (tx.probability > 0.5 ? 'HIGH' : 'SAFE');
            const color = risk === 'CRITICAL' ? '#ff0055' : (risk === 'HIGH' ? '#ff9100' : '#00e676');
            
            let html = `
                <td style="color: #94a3b8; font-family: 'JetBrains Mono'; position: sticky; left: 0; background: #0f172a; z-index: 1;">${tx.time}</td>
                <td style="font-family: 'JetBrains Mono'; position: sticky; left: 140px; background: #0f172a; z-index: 1;">₹${tx.amount.toFixed(2)}</td>
                <td style="font-family: 'JetBrains Mono'; position: sticky; left: 260px; background: #0f172a; z-index: 1;">${probPct}%</td>
                <td style="position: sticky; left: 390px; background: #0f172a; z-index: 1; box-shadow: 4px 0 8px rgba(0,0,0,0.4);"><span class="badge" style="background: ${color}22; color: ${color}; box-shadow: 0 0 8px ${color}44;">${risk}</span></td>
            `;
            
            for(let i=1; i<=28; i++) {
                const val = tx.features && tx.features[`V${i}`] !== undefined ? tx.features[`V${i}`].toFixed(4) : '0.0000';
                html += `<td style="font-family: 'JetBrains Mono'; color: #64748b;">${val}</td>`;
            }
            tr.innerHTML = html;
            tbody.appendChild(tr);
        });
        
        document.getElementById('batch-results').style.display = 'block';
        
    } catch (e) {
        console.error(e);
        alert("Batch Processing Failed:\\n" + e.message);
    } finally {
        btn.innerText = "Select CSV File";
        btn.disabled = false;
        fileInput.value = '';
    }
}
