// popup.js
document.addEventListener('DOMContentLoaded', () => {
    const statusEl = document.getElementById('status');

    function render(result) {
        if (!result) {
            statusEl.textContent = 'No phishing data yet';
            return;
        }
        const { score, decision } = result;
        statusEl.innerHTML = `
      <div>Confidence: <strong>${(1 - score.toFixed(4))*100}%</strong></div>
      <div>Verdict:
        <span class="${decision ? 'phish' : 'benign'}">
          ${decision ? 'PHISHING' : 'BENIGN'}
        </span>
      </div>
    `;
    }

    // 1) fetch current value once
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
        if (!tabs.length) {
            statusEl.textContent = 'No active tab';
            return;
        }
        const tabId = String(tabs[0].id);
        chrome.storage.session.get(tabId, items => {
            render(items[tabId]);
        });

        // 2) listen for future updates
        chrome.storage.onChanged.addListener((changes, area) => {
            if (area === 'session' && changes[tabId]) {
                render(changes[tabId].newValue);
            }
        });
    });
});