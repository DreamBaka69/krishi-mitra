// frontend/app.js
// Depends on config.js which must define window.KRISHI_MITRA_CONFIG.BACKEND_URL
(function () {
  // Read backend URL from config.js (fallback to localhost)
  const CONFIG = window.KRISHI_MITRA_CONFIG || {};
  const BACKEND_URL = CONFIG.BACKEND_URL || 'http://localhost:5000';

  // DOM references
  const imageInput = document.getElementById('imageInput');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const imagePreview = document.getElementById('imagePreview');
  const resultSection = document.getElementById('resultSection');
  const diseaseResult = document.getElementById('diseaseResult');
  const treatmentAdvice = document.getElementById('treatmentAdvice');
  const loadingEl = document.getElementById('loading');
  const classesListEl = document.getElementById('classesList');

  let selectedFile = null;
  let diseaseDB = null;

  function setLoading(isLoading, msg) {
    loadingEl.style.display = isLoading ? 'block' : 'none';
    loadingEl.innerText = msg || 'Loading...';
  }

  async function fetchClasses() {
    try {
      setLoading(true, 'Fetching supported classes...');
      const resp = await fetch(`${BACKEND_URL}/classes`);
      if (!resp.ok) {
        throw new Error(`Status ${resp.status}`);
      }
      const data = await resp.json();
      diseaseDB = data;
      populateClasses(data);
      setLoading(false);
    } catch (err) {
      console.warn('Could not fetch classes from backend:', err);
      setLoading(false);
      classesListEl.innerText = 'Could not fetch classes from backend. Make sure BACKEND_URL is set in config.js and backend is running.';
    }
  }

  function populateClasses(data) {
    try {
      const byPlant = data.by_plant || {};
      classesListEl.innerHTML = '';
      for (const plant of Object.keys(byPlant)) {
        const ul = document.createElement('ul');
        ul.className = 'plant-list';
        const header = document.createElement('li');
        header.innerText = plant;
        header.className = 'plant-header';
        ul.appendChild(header);
        byPlant[plant].forEach(cls => {
          const li = document.createElement('li');
          li.innerText = cls;
          ul.appendChild(li);
        });
        classesListEl.appendChild(ul);
      }
    } catch (e) {
      classesListEl.innerText = 'No classes info available';
    }
  }

  // Preview selected image
  imageInput.addEventListener('change', (ev) => {
    const file = ev.target.files[0];
    if (!file) return;
    selectedFile = file;
    const url = URL.createObjectURL(file);
    imagePreview.src = url;
    imagePreview.style.display = 'block';
    resultSection.style.display = 'none';
  });

  analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) {
      alert('Please choose an image first.');
      return;
    }
    try {
      setLoading(true, 'Analyzing image...');
      const form = new FormData();
      form.append('image', selectedFile);
      const resp = await fetch(`${BACKEND_URL}/analyze`, {
        method: 'POST',
        body: form
      });
      setLoading(false);
      if (!resp.ok) {
        const err = await resp.json().catch(()=>({error:'unknown'}));
        alert('Server error: ' + (err.error || resp.status));
        return;
      }
      const r = await resp.json();
      showResult(r);
    } catch (err) {
      setLoading(false);
      console.error(err);
      alert('Failed to contact server. Check backend URL and server status.');
    }
  });

  function showResult(payload) {
    resultSection.style.display = 'block';
    const conf = (payload.confidence || 0);
    const confPct = Math.round(conf * 100);
    diseaseResult.innerHTML = `
      <strong>Plant:</strong> ${escapeHtml(payload.plant)} <br/>
      <strong>Disease (internal):</strong> ${escapeHtml(payload.detailed_class)} <br/>
      <strong>Detected (slug):</strong> ${escapeHtml(payload.disease)} <br/>
      <strong>Confidence:</strong> ${confPct}%
      <div style="margin-top:.5rem"><em>Model:</em> ${escapeHtml(payload.model_used || 'unknown')}</div>
    `;

    // Show treatment if returned
    const advice = payload.advice || {};
    if (advice && (advice.treatment || advice.prevention || advice.friendly_name)) {
      treatmentAdvice.innerHTML = `
        <h4>${escapeHtml(advice.friendly_name || payload.disease)}</h4>
        <strong>Treatment:</strong>
        <p>${escapeHtml(advice.treatment || 'No treatment info')}</p>
        <strong>Prevention:</strong>
        <p>${escapeHtml(advice.prevention || 'No prevention info')}</p>
      `;
    } else {
      treatmentAdvice.innerHTML = '<p>No additional advice returned.</p>';
    }
    // scroll into view
    resultSection.scrollIntoView({behavior:'smooth'});
  }

  // small helper to avoid XSS
  function escapeHtml(s) {
    if (!s && s !== 0) return '';
    return String(s)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  // Kick off
  fetchClasses();

  // Debug: expose BACKEND_URL to console
  console.log('Krishi Mitra frontend will use backend at:', BACKEND_URL);
})();