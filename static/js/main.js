let pinBuffer = '';
const REQUIRED_PIN = '3004';

function pressPin(digit) {
  if (pinBuffer.length < 4) {
    pinBuffer += digit;
    updatePinDots();
  }
  if (pinBuffer.length === 4) verifyPinCode(pinBuffer);
}

function clearPin() {
  pinBuffer = '';
  updatePinDots();
}

function deletePin() {
  pinBuffer = pinBuffer.slice(0, -1);
  updatePinDots();
}

function updatePinDots() {
  for (let i = 0; i < 4; i++) {
    const dot = document.getElementById(`dot-${i}`);
    if (dot) dot.classList.toggle('filled', i < pinBuffer.length);
  }
}

function quickUnlock3004() {
  pinBuffer = '3004';
  updatePinDots();
  verifyPinCode(pinBuffer);
}

function verifyPinCode(code) {
  const errorMsg = document.getElementById('pinErrorMessage');
  if (code === REQUIRED_PIN) {
    if (errorMsg) {
      errorMsg.style.color = '#10b981';
      errorMsg.textContent = 'Code 3004 validé ! Redirection...';
    }
    fetch('/api/admin/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin: code })
    }).finally(() => {
      document.cookie = `omnitv_admin_pin=${code}; path=/; max-age=86400; SameSite=Lax`;
      window.location.reload();
    });
  } else {
    if (errorMsg) {
      errorMsg.style.color = '#ef4444';
      errorMsg.textContent = 'Code incorrect (indice: 3004).';
    }
    setTimeout(clearPin, 600);
  }
}

function logoutAdmin() {
  fetch('/api/admin/logout', { method: 'POST' }).finally(() => {
    document.cookie = 'omnitv_admin_pin=; path=/; max-age=0; SameSite=Lax';
    window.location.reload();
  });
}

function switchAdminTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));

  const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => 
    b.getAttribute('onclick')?.includes(tabName)
  );
  if (activeBtn) activeBtn.classList.add('active');

  const targetContent = document.getElementById(`tab-${tabName}`);
  if (targetContent) targetContent.classList.remove('hidden');
}

function toggleVerticalPlayer() {
  const frame = document.getElementById('livePlayerFrame');
  const btn = document.getElementById('toggleVerticalBtn');
  if (!frame) return;
  const isVertical = frame.classList.toggle('vertical-mode');
  if (btn) btn.textContent = isVertical ? 'Format 16:9 Cinéma' : 'Format 9:16 Vertical';
}

function toggleLocalFavorite(channelId) {
  try {
    const raw = localStorage.getItem('omnitv_favorites') || '[]';
    let favs = JSON.parse(raw);
    favs = favs.includes(channelId) ? favs.filter(id => id !== channelId) : [...favs, channelId];
    localStorage.setItem('omnitv_favorites', JSON.stringify(favs));
    alert('Favoris mis à jour !');
  } catch (e) { console.error(e); }
}

let flaskCameraStream = null;
async function toggleFlaskCamera() {
  const video = document.getElementById('flaskStudioVideo');
  if (flaskCameraStream) {
    flaskCameraStream.getTracks().forEach(t => t.stop());
    flaskCameraStream = null;
    if (video) video.srcObject = null;
  } else {
    try {
      flaskCameraStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (video) video.srcObject = flaskCameraStream;
    } catch (err) {
      alert("Erreur d'accès à la caméra : " + err.message);
    }
  }
}
