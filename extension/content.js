// content.js

// Listen to the background message:
chrome.runtime.onMessage.addListener((message, sender) => {
    // ignore messages not from *this* extension
    if (sender.id !== chrome.runtime.id) return;
    if (message.type === 'META_MODEL_RESULT') {
        const { score, decision } = message;
        console.log('🏷️ Meta score:', score, 'Phishing?', decision);
        if (decision) {
            showPhishWarning(score);
        }
    }
});

(function () {
    chrome.runtime.sendMessage({ type: 'CONTENT_READY' });
    try {
        const feats = window.extractContentFeatures(
            document.documentElement,
            window.location.href
        );
        console.log('🔍 Content features:', feats);
        chrome.runtime.sendMessage({ type: 'CONTENT_FEATURES', data: feats });
    } catch (err) {
        console.error('Content feature extraction failed:', err);
    }
})();


function showPhishWarning(score) {
    // 1. Don’t show it twice
    if (document.getElementById('__phish-warning-overlay')) return;

    // 2. Create the overlay container
    const overlay = document.createElement('div');
    overlay.id = '__phish-warning-overlay';
    Object.assign(overlay.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100vw',
        height: '100vh',
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: '999999',
    });

    // 3. Create the warning box
    const box = document.createElement('div');
    Object.assign(box.style, {
        background: 'white',
        color: '#a00',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
        textAlign: 'center',
        maxWidth: '90%',
        lineHeight: '1.4',
        fontFamily: 'sans-serif',
    });

    box.innerHTML = `
    <h1 style="margin-top:0; font-size:1.5em;">⚠️ Phishing Detected!</h1>
    <p>This page looks malicious.</p>
    <p><strong>Confidence:</strong> ${(score * 100).toFixed(1)}%</p>
    <button id="__phish-warning-close">Dismiss</button>
  `;

    // 4. Wire up the dismiss button
    box.querySelector('#__phish-warning-close')
        .addEventListener('click', () => overlay.remove());

    // 5. Assemble and insert into DOM
    overlay.appendChild(box);
    document.body.appendChild(overlay);
}