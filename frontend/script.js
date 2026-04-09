/*
MediSimplify - Main JavaScript
Copyright (c) 2026 Sargam Chicholikar
*/

// Auto-detect API URL based on current page
const API = window.location.origin;let prescFile = null, labFile = null, xrayFile = null;
let currentAudio = null, audioUpdateInterval = null;
let selectedRating = 0, usedFeature = 'general';

// ==================== FILE SELECTION ====================

function fileSelected(input, nameId, boxId) {
    if (input.files[0]) {
        if(nameId === 'prescName') prescFile = input.files[0];
        if(nameId === 'labName') labFile = input.files[0];
        if(nameId === 'xrayName') xrayFile = input.files[0];
        
        document.getElementById(nameId).textContent = `✓ ${input.files[0].name}`;
        document.getElementById(nameId).style.display = 'inline-block';
        document.getElementById(boxId).classList.add('has-file');
    }
}

// ==================== ANALYZE REPORTS ====================

async function analyze() {
    const manualDrugs = document.getElementById('drugInput').value.trim();
    const language = document.getElementById('languageSelect').value;
    const output = document.getElementById('result');
    const btn = document.getElementById('btn');
    
    if (!prescFile && !manualDrugs && !labFile && !xrayFile) {
        alert('Please upload a report or type drug names'); 
        return;
    }
    
    closePlayer();
    document.getElementById('feedbackSection').style.display = 'none';
    
    output.style.display = 'block';
    output.innerHTML = `
        <div style="text-align: center; padding: 80px 20px;">
            <div class="spinner"></div>
            <h3 style="font-size: 1.5rem; margin-bottom: 8px;">Analyzing in ${language}...</h3>
            <p style="color: var(--text-light); font-size: 1rem;">AI processing (20-60 seconds)</p>
        </div>`;
    btn.disabled = true; 
    btn.innerHTML = '⏳ Processing...';
    
    try {
        let drugData = null, labData = null, xrayData = null;
        
        // Prescription
        if (prescFile) {
            console.log('Uploading prescription...');
            const fd = new FormData(); 
            fd.append('prescription', prescFile);
            const res = await fetch(`${API}/analyze-complete?language=${encodeURIComponent(language)}`, { 
                method: 'POST', 
                body: fd 
            });
            
            if (res.ok) {
                drugData = await res.json();
                console.log('Prescription data:', drugData);
            }
        } else if (manualDrugs) {
            console.log('Analyzing manual drugs...');
            const drugs = manualDrugs.split(',').map(d => d.trim()).filter(d => d);
            const res = await fetch(`${API}/analyze-drugs`, {
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ drug_names: drugs, language: language })
            });
            
            if (res.ok) {
                drugData = await res.json();
                console.log('Drug data:', drugData);
            }
        }
        
        // Lab Report
        if (labFile) {
            console.log('Uploading lab report...');
            const fd = new FormData(); 
            fd.append('file', labFile);
            const res = await fetch(`${API}/upload-lab-report?language=${encodeURIComponent(language)}`, { 
                method: 'POST', 
                body: fd 
            });
            
            if (res.ok) { 
                const json = await res.json();
                console.log('Lab data:', json);
                
                if(json.ai_analysis && json.ai_analysis.length > 0) {
                    labData = { lab_analysis: json.ai_analysis };
                }
            }
        }
        
        // X-Ray
        if (xrayFile) {
            console.log('Uploading X-ray...');
            const fd = new FormData(); 
            fd.append('file', xrayFile);
            const res = await fetch(`${API}/upload-xray?language=${encodeURIComponent(language)}`, { 
                method: 'POST', 
                body: fd 
            });
            
            if (res.ok) { 
                const json = await res.json();
                console.log('X-ray data:', json);
                
                if(json.xray_analysis) {
                    xrayData = json.xray_analysis;
                }
            }
        }
        
        console.log('Final data:', { drugData, labData, xrayData });
        displayResults(drugData, labData, xrayData, language);
        
    } catch (err) {
        console.error('Error:', err);
        output.innerHTML = `<div style="padding: 25px; background: #fee2e2; color: #ef4444; border-radius: 16px; text-align:center;"><strong>Error:</strong> ${err.message}</div>`;
    } finally {
        btn.disabled = false; 
        btn.innerHTML = '✨ Analyze Reports';
    }
}

// ==================== DISPLAY RESULTS ====================

function displayResults(drugData, labData, xrayData, language) {
    const output = document.getElementById('result');
    
    let html = `
        <div style="text-align: center;">
            <div class="result-success-badge">✅ Analysis Complete (${language})</div>
        </div>
        
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-val" style="color: var(--primary);">${drugData?.drugs?.length || 0}</div>
                <div class="stat-label">Medications</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color: var(--success);">${labData?.lab_analysis?.length || 0}</div>
                <div class="stat-label">Lab Tests</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color: var(--warning);">${drugData?.detected_conditions?.length || 0}</div>
                <div class="stat-label">Conditions</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color: var(--xray);">${xrayData ? 1 : 0}</div>
                <div class="stat-label">X-Rays</div>
            </div>
        </div>
    `;
    
    // Detected Conditions
    if (drugData?.detected_conditions?.length > 0) {
        html += `<div class="section-header"><h2 class="report-section-title">🏥 Conditions</h2></div><div class="results-grid">`;
        drugData.detected_conditions.forEach(c => {
            html += `
                <div class="result-card" style="--card-color: var(--warning);">
                    <div class="card-top-row">
                        <div class="icon-title-group">
                            <div class="icon-circle" style="background: var(--warning-light); color: var(--warning);">🩺</div>
                            <div class="card-title">${c.condition}</div>
                        </div>
                    </div>
                    <div class="info-block-text" style="padding: 0;">${c.explanation}</div>
                </div>`;
        });
        html += `</div>`;
    }
    
    // Medications
    if (drugData?.drugs?.length > 0) {
        let allDrugText = "";
        html += `
            <div class="section-header">
                <h2 class="report-section-title">💊 Medications</h2>
                <button onclick="triggerAudio('Medications', 'drugs', '${language}')" class="section-audio-btn">🔊 Listen</button>
            </div>
            <div class="results-grid">`;
        
        drugData.drugs.forEach(drug => {
            allDrugText += `${drug.name}. Treats: ${drug.treats}. ${drug.explanation}. Dosage: ${drug.dosage}. When: ${drug.frequency}. Warning: ${drug.warnings}. `;
            html += `
                <div class="result-card" style="--card-color: var(--primary);">
                    <div class="card-top-row">
                        <div class="icon-title-group">
                            <div class="icon-circle" style="background: var(--primary-light); color: var(--primary);">💊</div>
                            <div class="card-title">${drug.name}</div>
                        </div>
                        <div class="card-badge" style="background: var(--primary-light); color: var(--primary);">${drug.dosage}</div>
                    </div>
                    <div style="font-size: 1rem; font-weight: 600; margin-bottom: 15px;">🎯 ${drug.treats}</div>
                    <div class="info-block">
                        <div class="info-block-title">What it does</div>
                        <div class="info-block-text">${drug.explanation}</div>
                    </div>
                    <div class="action-block" style="background: #f8fafc; border: 1px solid #e2e8f0;">
                        <span>📅</span> <div>${drug.frequency}</div>
                    </div>
                    <div class="action-block" style="background: var(--danger-light); color: #be123c;">
                        <span>⚠️</span> <div>${drug.warnings}</div>
                    </div>
                </div>`;
        });
        html += `</div><div id="audio-text-drugs" style="display:none;">${allDrugText}</div>`;
    }
    
    // Lab Results
    if (labData?.lab_analysis?.length > 0) {
        let allLabText = "";
        html += `
            <div class="section-header">
                <h2 class="report-section-title">🧪 Lab Results</h2>
                <button onclick="triggerAudio('Lab Results', 'labs', '${language}')" class="section-audio-btn">🔊 Listen</button>
            </div>
            <div class="results-grid">`;
        
        labData.lab_analysis.forEach(lab => {
            const colorMap = { 'green': 'var(--success)', 'orange': 'var(--warning)', 'red': 'var(--danger)' };
            const cssColor = colorMap[lab.color] || 'var(--primary)';
            const bgBadge = lab.color === 'green' ? 'var(--success-light)' : 
                           lab.color === 'orange' ? 'var(--warning-light)' : 'var(--danger-light)';
            
            allLabText += `${lab.test}. Value: ${lab.value}. Status: ${lab.status}. ${lab.explanation}. ${lab.action}. `;
            
            html += `
                <div class="result-card" style="--card-color: ${cssColor};">
                    <div class="card-top-row">
                        <div class="icon-title-group">
                            <div class="icon-circle" style="background: ${bgBadge}; color: ${cssColor};">🩸</div>
                            <div class="card-title">${lab.test}</div>
                        </div>
                        <div class="card-badge" style="background: ${bgBadge}; color: ${cssColor};">${lab.status}</div>
                    </div>
                    <div class="lab-value" style="color: ${cssColor};">${lab.value}</div>
                    <div class="info-block">
                        <div class="info-block-title">Meaning</div>
                        <div class="info-block-text">${lab.explanation}</div>
                    </div>
                    <div class="action-block" style="background: #eff6ff; color: #1e40af;">
                        <span>💡</span> <div>${lab.action}</div>
                    </div>
                </div>`;
        });
        html += `</div><div id="audio-text-labs" style="display:none;">${allLabText}</div>`;
    }

    // X-Ray Results
    if (xrayData) {
        const colorMap = { 'green': 'var(--success)', 'red': 'var(--danger)', 'orange': 'var(--warning)' };
        const cssColor = colorMap[xrayData.color] || 'var(--warning)';
        const xrayText = `${xrayData.overall_result} ${xrayData.findings} ${xrayData.action}`;
        
        html += `
            <div class="section-header">
                <h2 class="report-section-title">🦴 X-Ray</h2>
                <button onclick="triggerAudio('X-Ray', 'xray', '${language}')" class="section-audio-btn">🔊 Listen</button>
            </div>`;
        
        html += `
            <div class="result-card" style="--card-color: ${cssColor}; max-width: 900px;">
                <div class="card-top-row">
                    <div class="icon-title-group">
                        <div class="icon-circle" style="background: var(--xray-light); color: var(--xray);">🔬</div>
                        <div class="card-title" style="font-size: 1.3rem;">${xrayData.xray_type}</div>
                    </div>
                </div>
                
                ${xrayData.has_fracture ? `
                    <div style="background: var(--danger-light); border: 2px solid var(--danger); padding: 20px; border-radius: var(--radius-md); margin: 15px 0;">
                        <h4 style="color: #9f1239; font-size: 1.2rem; margin-bottom: 15px;">⚠️ FRACTURE DETECTED</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: white; padding: 15px; border-radius: 10px;">
                            <div>
                                <div style="font-size: 0.75rem; color: var(--text-light); font-weight: 700; text-transform: uppercase; margin-bottom: 3px;">Location</div>
                                <div style="font-size: 0.95rem; font-weight: 600; margin-bottom: 10px;">${xrayData.body_part} - ${xrayData.fracture_location}</div>
                                <div style="font-size: 0.75rem; color: var(--text-light); font-weight: 700; text-transform: uppercase; margin-bottom: 3px;">Type</div>
                                <div style="font-size: 0.95rem; font-weight: 600;">${xrayData.fracture_type}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: var(--text-light); font-weight: 700; text-transform: uppercase; margin-bottom: 3px;">Recovery</div>
                                <div style="font-size: 1.1rem; font-weight: 800; color: #be123c; margin-bottom: 10px;">${xrayData.recovery_time}</div>
                                <div style="font-size: 0.75rem; color: var(--text-light); font-weight: 700; text-transform: uppercase; margin-bottom: 3px;">Cause</div>
                                <div style="font-size: 0.95rem;">${xrayData.likely_cause}</div>
                            </div>
                        </div>
                    </div>
                ` : `
                    <div style="background: var(--success-light); border: 2px solid var(--success); padding: 20px; border-radius: var(--radius-md); margin: 15px 0;">
                        <h4 style="color: #065f46; font-size: 1.2rem;">✅ NO FRACTURE</h4>
                        <p style="color: #047857; font-size: 1rem; margin-top: 5px;">Bones appear healthy</p>
                    </div>
                `}
                
                <div class="info-block">
                    <div class="info-block-title">Findings</div>
                    <div class="info-block-text" style="white-space: pre-line;">${xrayData.findings}</div>
                </div>
                <div class="action-block" style="background: #eff6ff; color: #1e40af; padding: 15px;">
                    <span>📋</span> <div><strong>Summary:</strong> ${xrayData.overall_result}</div>
                </div>
                <div class="action-block" style="background: var(--warning-light); color: #92400e; padding: 15px;">
                    <span>💡</span> <div><strong>Action:</strong> ${xrayData.action}</div>
                </div>
            </div>`;
        html += `<div id="audio-text-xray" style="display:none;">${xrayText}</div>`;
    }

    // Disclaimer
    html += `
        <div style="background: var(--warning-light); border: 2px solid var(--warning); padding: 18px; border-radius: var(--radius-lg); margin-top: 40px;">
            <h4 style="color: #92400e; margin-bottom: 8px; font-size: 1rem;">⚠️ Disclaimer</h4>
            <p style="color: #78350f; font-size: 0.9rem; line-height: 1.5;">
                Educational tool only. Always consult qualified medical professionals.
            </p>
        </div>`;
    
    output.innerHTML = html;
    output.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Track which feature was used
    if (xrayData) usedFeature = 'xray';
    else if (labData) usedFeature = 'lab';
    else if (drugData) usedFeature = 'prescription';
    
    // Show feedback form
    setTimeout(() => {
        document.getElementById('feedbackSection').style.display = 'block';
        setTimeout(() => {
            document.getElementById('feedbackSection').scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 500);
    }, 2000);
}

// ==================== AUDIO PLAYER ====================

async function triggerAudio(title, typeId, language) {
    const hiddenDiv = document.getElementById(`audio-text-${typeId}`);
    let text = hiddenDiv ? hiddenDiv.innerText : "";
    
    let cleanText = text.replace(/[✅⚠️❌🔍💊📊🔬💡📋🏥🦴💥⏱️📅🩸]/g, '')
                        .replace(/[*[\]{}]/g, '')
                        .replace(/\n+/g, '. ')
                        .trim();
    
    const player = document.getElementById('floatingPlayer');
    const titleEl = document.getElementById('playerTitle');
    const playBtn = document.getElementById('playPauseBtn');
    const progressContainer = document.querySelector('.progress-container');
    const timeDisplay = document.getElementById('playerTime');
    
    // Show generating state
    titleEl.textContent = "Generating...";
    player.classList.add('active');
    playBtn.innerHTML = '⏳';
    progressContainer.classList.add('generating');
    timeDisplay.textContent = 'Please wait...';
    
    try {
        if(currentAudio) stopAudio();
        
        const response = await fetch(`${API}/generate-audio?text=${encodeURIComponent(cleanText)}&language=${encodeURIComponent(language)}`, { 
            method: 'POST' 
        });
        
        if (!response.ok) throw new Error('Failed');
        
        const audioBlob = await response.blob();
        currentAudio = new Audio(URL.createObjectURL(audioBlob));
        
        // Remove generating state
        progressContainer.classList.remove('generating');
        titleEl.textContent = title;
        playBtn.innerHTML = '⏸';
        currentAudio.play();
        
        audioUpdateInterval = setInterval(updateProgress, 100);
        currentAudio.onended = () => { playBtn.innerHTML = '▶'; };
        
    } catch (err) {
        console.error(err);
        progressContainer.classList.remove('generating');
        titleEl.textContent = "Error";
        playBtn.innerHTML = '✖';
        setTimeout(closePlayer, 3000);
    }
}

function toggleAudio() {
    if (!currentAudio) return;
    const playBtn = document.getElementById('playPauseBtn');
    if (currentAudio.paused) {
        currentAudio.play();
        playBtn.innerHTML = '⏸';
    } else {
        currentAudio.pause();
        playBtn.innerHTML = '▶';
    }
}

function replayAudio() {
    if (currentAudio) {
        currentAudio.currentTime = 0;
        currentAudio.play();
        document.getElementById('playPauseBtn').innerHTML = '⏸';
    }
}

function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    if (audioUpdateInterval) {
        clearInterval(audioUpdateInterval);
        audioUpdateInterval = null;
    }
    const progressContainer = document.querySelector('.progress-container');
    if (progressContainer) progressContainer.classList.remove('generating');
    document.getElementById('audioProgress').style.width = '0%';
}

function closePlayer() {
    stopAudio();
    document.getElementById('floatingPlayer').classList.remove('active');
}

function updateProgress() {
    if (!currentAudio || isNaN(currentAudio.duration)) return;
    const progress = (currentAudio.currentTime / currentAudio.duration) * 100;
    document.getElementById('audioProgress').style.width = progress + '%';
    document.getElementById('playerTime').textContent = `${formatTime(currentAudio.currentTime)} / ${formatTime(currentAudio.duration)}`;
}

function seekAudio(e) {
    if (!currentAudio || isNaN(currentAudio.duration)) return;
    if (document.querySelector('.progress-container').classList.contains('generating')) return;
    
    const width = e.currentTarget.offsetWidth;
    currentAudio.currentTime = currentAudio.duration * (e.offsetX / width);
}

function formatTime(s) {
    if (isNaN(s)) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
}

// ==================== FEEDBACK SYSTEM ====================

function setRating(rating) {
    selectedRating = rating;
    
    for (let i = 1; i <= 5; i++) {
        const star = document.getElementById(`star${i}`);
        star.textContent = i <= rating ? '★' : '☆';
        star.style.color = i <= rating ? '#f59e0b' : '#cbd5e1';
    }
}

function hoverRating(rating) {
    for (let i = 1; i <= 5; i++) {
        const star = document.getElementById(`star${i}`);
        if (selectedRating === 0) {
            star.textContent = i <= rating ? '★' : '☆';
            star.style.color = i <= rating ? '#fbbf24' : '#cbd5e1';
        }
    }
}

function resetRating() {
    if (selectedRating > 0) {
        setRating(selectedRating);
    } else {
        for (let i = 1; i <= 5; i++) {
            document.getElementById(`star${i}`).textContent = '☆';
            document.getElementById(`star${i}`).style.color = '#cbd5e1';
        }
    }
}

async function submitFeedback() {
    const rating = selectedRating;
    const comments = document.getElementById('feedbackComments').value.trim();
    const feedbackType = document.getElementById('feedbackType').value;
    const email = document.getElementById('feedbackEmail').value.trim();
    const language = document.getElementById('languageSelect').value;
    
    if (rating === 0) {
        alert('⭐ Please select a star rating');
        return;
    }
    
    if (!comments) {
        alert('💬 Please add your feedback');
        return;
    }
    
    const btn = document.getElementById('feedbackBtn');
    const msg = document.getElementById('feedbackMessage');
    
    try {
        btn.disabled = true;
        btn.textContent = '📤 Sending...';
        btn.style.opacity = '0.7';
        
        const url = `${API}/submit-feedback?rating=${rating}&comments=${encodeURIComponent(comments)}&feature_used=${usedFeature}&language=${language}&email=${encodeURIComponent(email || 'anonymous')}&feedback_type=${feedbackType}`;
        
        const response = await fetch(url, { method: 'POST' });
        
        if (response.ok) {
            msg.style.display = 'block';
            msg.style.color = 'var(--success)';
            msg.style.background = 'var(--success-light)';
            msg.style.padding = '12px';
            msg.style.borderRadius = '10px';
            msg.textContent = '✅ Thank you! Your feedback helps improve MediSimplify!';
            
            // Clear form
            document.getElementById('feedbackComments').value = '';
            document.getElementById('feedbackEmail').value = '';
            document.getElementById('feedbackType').selectedIndex = 0;
            
            // Reset stars
            for (let i = 1; i <= 5; i++) {
                document.getElementById(`star${i}`).textContent = '☆';
                document.getElementById(`star${i}`).style.color = '#cbd5e1';
            }
            selectedRating = 0;
            
            // Hide form after 4 seconds
            setTimeout(() => {
                document.getElementById('feedbackSection').style.display = 'none';
            }, 4000);
            
        } else {
            throw new Error('Submission failed');
        }
        
    } catch (err) {
        console.error(err);
        msg.style.display = 'block';
        msg.style.color = 'var(--danger)';
        msg.style.background = 'var(--danger-light)';
        msg.style.padding = '12px';
        msg.style.borderRadius = '10px';
        msg.textContent = '❌ Error submitting. Please try again.';
    } finally {
        btn.disabled = false;
        btn.textContent = '📤 Submit Feedback';
        btn.style.opacity = '1';
    }
}