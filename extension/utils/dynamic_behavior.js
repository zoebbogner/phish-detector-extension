// dynamic_behavior.js

/**
 * enableDynamicBehaviorChecks:
 *   Installs all runtime hooks (MutationObserver, fetch/XHR wrappers, form‐submit listeners).
 *   Call this function once static checks have deemed the page “safe.”
 */
window.enableDynamicBehaviorChecks = (function () {
    // We wrap everything in an IIFE so that local helper variables/functions do not 
    // pollute the global scope. Only enableDynamicBehaviorChecks attaches itself to window.

    // --- Internal state & placeholders ---
    let dynamicEnabled = false;
    let originalFetch = null;
    let originalXHR = null;
    let mutationObserver = null;

    // Utility to compare hostnames
    function isSameDomain(hostname) {
        return hostname === window.location.hostname;
    }

    // Called when any dynamic‐hook “flag” trips (cross‐domain request, injected iframe, etc.)
    function onDynamicSuspiciousDetected(detail) {
        console.warn('[Dynamic] Suspicious behavior detected:', detail);
        showPhishWarning(detail);
        cleanupDynamicHooks();
    }

    // 1) Wrap XMLHttpRequest to catch runtime cross‐domain requests
    function wrapXMLHttpRequest() {
        originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function () {
            const xhr = new originalXHR();
            const origOpen = xhr.open;
            xhr.open = function (method, url) {
                try {
                    const targetHostname = new URL(url, window.location.href).hostname;
                    if (!isSameDomain(targetHostname)) {
                        onDynamicSuspiciousDetected(`XHR to external domain: ${targetHostname}`);
                    }
                } catch (e) {
                    // URL parsing failed; ignore
                }
                return origOpen.apply(this, arguments);
            };
            return xhr;
        };
    }

    // 2) Wrap fetch() to catch runtime cross‐domain fetch calls
    function wrapFetch() {
        originalFetch = window.fetch;
        window.fetch = function (resource, init) {
            try {
                const requestURL = new URL(
                    typeof resource === 'string' ? resource : resource.url,
                    window.location.href
                );
                if (!isSameDomain(requestURL.hostname)) {
                    onDynamicSuspiciousDetected(`fetch() to external domain: ${requestURL.hostname}`);
                }
            } catch (e) {
                // ignore parsing errors
            }
            return originalFetch.apply(this, arguments);
        };
    }

    // 3) Hook all <form> submissions (capture phase) to catch changed action attributes
    function hookFormSubmissions() {
        document.body.addEventListener(
            'submit',
            (event) => {
                const form = event.target;
                if (!(form instanceof HTMLFormElement)) return;

                const actionURL = form.getAttribute('action') || '';
                if (actionURL) {
                    try {
                        const host = new URL(actionURL, window.location.href).hostname;
                        if (!isSameDomain(host)) {
                            event.preventDefault();
                            onDynamicSuspiciousDetected(`Form attempts to submit to ${actionURL}`);
                        }
                    } catch (e) {
                        // ignore invalid URL
                    }
                }
            },
            true // use capture phase so even dynamically added forms are caught
        );
    }

    // 4) Start a MutationObserver to watch for injected iframes, forms, or suspicious scripts
    function enableMutationObserver() {
        const config = { childList: true, subtree: true };
        mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (!(node instanceof HTMLElement)) return;

                    // a) New <iframe>
                    if (node.tagName === 'IFRAME' && node.src) {
                        try {
                            const iframeHost = new URL(node.src, window.location.href).hostname;
                            if (!isSameDomain(iframeHost)) {
                                onDynamicSuspiciousDetected(`Injected iframe pointing to ${iframeHost}`);
                            }
                        } catch (e) {
                            // ignore parse errors
                        }
                    }

                    // b) New <form>
                    if (node.tagName === 'FORM') {
                        const formAction = node.getAttribute('action') || '';
                        if (formAction) {
                            try {
                                const host = new URL(formAction, window.location.href).hostname;
                                if (!isSameDomain(host)) {
                                    onDynamicSuspiciousDetected(`Dynamic form action to ${formAction}`);
                                }
                            } catch (e) {
                                // ignore parse errors
                            }
                        }
                    }

                    // c) New <script> with suspicious inline code
                    if (node.tagName === 'SCRIPT' && node.textContent) {
                        const txt = node.textContent;
                        if (/eval\(|document\.write\(|window\.location\s*=.*http/.test(txt)) {
                            onDynamicSuspiciousDetected('Inline script with suspicious eval/redirect');
                        }
                    }
                });
            });
        });

        mutationObserver.observe(document.documentElement, config);
    }

    // 5) Cleanup: disconnect observer & restore originals
    function cleanupDynamicHooks() {
        if (mutationObserver) {
            mutationObserver.disconnect();
            mutationObserver = null;
        }
        if (originalFetch) {
            window.fetch = originalFetch;
            originalFetch = null;
        }
        if (originalXHR) {
            window.XMLHttpRequest = originalXHR;
            originalXHR = null;
        }
        document.body.removeEventListener('submit', hookFormSubmissions, true);
        dynamicEnabled = false;
    }

    // The function we expose:  
    //    - Installs all dynamic hooks, but only once
    function enableDynamicBehaviorChecks() {
        if (dynamicEnabled) return;
        dynamicEnabled = true;

        console.log('[Dynamic] Activating dynamic behavior checks');
        wrapXMLHttpRequest();
        wrapFetch();
        hookFormSubmissions();
        enableMutationObserver();

        // Optionally, inform background that dynamic hooks are active (e.g. if you want to monitor redirects there):
        chrome.runtime.sendMessage({ type: 'DYNAMIC_HOOKS_ACTIVE' });
    }

    // Return the “public” function; everything else stays private
    return enableDynamicBehaviorChecks;
})();