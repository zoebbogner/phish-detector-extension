// content.js

// Immediately run as soon as DOM is ready
(function () {
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

// Listen to the background message:
