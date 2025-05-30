// background.js (MV3 module)
// This service worker loads the URL feature extractor and the XGBoost URL-model scorer
// and scores every navigation as soon as the URL is known.

import { extractUrlFeatures } from './utils/url_features.js';
import { putWithLimit } from './utils/cache.js';
import XGBoostScorer from './utils/scorer.js';

let urlScorer = null;
let contentScorer = null;
let metaScorer = null;
const readyTabs = new Set();

// Tab-scoped caches
const metaScores = new Map(); // tabId -> metaScore
const urlScores = new Map();  // tabId -> { score, features, url }
const contentScores = new Map(); // tabId -> { score, features }

(async () => {
    urlScorer = new XGBoostScorer(
        'production/url_model.json',
        'production/url_feature_index.json');
    await urlScorer.init();
    console.log('✅ Custom URL Scorer ready');
    
    contentScorer = new XGBoostScorer(
        'production/content_model.json',
        'production/content_feature_index.json');
    await contentScorer.init();
    console.log('✅ Custom Content Scorer ready');

    metaScorer = new XGBoostScorer(
        'production/meta_model.json',
        'production/meta_feature_index.json');
    await metaScorer.init();
    console.log('✅ Custom Meta Scorer ready');
})();

function maybeRunMetaModel(tabId) {
    if (!urlScores.has(tabId) || !contentScores.has(tabId) || !readyTabs.has(tabId)) return;
    const urlData = urlScores.get(tabId);
    const contentData = contentScores.get(tabId);
    // Use the exact keys your meta model expects
    const metaFeatures = {
        url_model_proba: urlData.score,
        content_model_proba: contentData.score
    };
    const metaScore = metaScorer.score(metaFeatures);
    putWithLimit(metaScores, tabId, metaScore);
    console.log(`Meta model phishing score for ${urlData.url}:`, metaScore);
    const isPhishing = metaScore > 0.5;
    console.log(`Meta model decision for ${urlData.url}:`, isPhishing ? 'PHISHING' : 'BENIGN');
    chrome.storage.session.set({
        [String(tabId)]: {
            score: metaScore,
            decision: isPhishing
        }
    });
    chrome.tabs.sendMessage(tabId, {
        type: 'META_MODEL_RESULT',
        score: metaScore,
        decision: isPhishing
    });
    
    if (!isPhishing) return;
    
    // 1) set the badge so you see a red “!” (optional)
    chrome.action.setBadgeText({ text: "!", tabId });
    chrome.action.setBadgeBackgroundColor({ color: "red", tabId });

    // 2) show a desktop notification
    chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/icon48.png",
        title: "⚠️ Phishing Detected!",
        message: `This page (${new URL(urlData.url).hostname}) looks malicious.`,
        priority: 2
    });
}

// Listen for committed navigations
chrome.webNavigation.onCommitted.addListener(({ url, frameId, tabId }) => {
    if (!urlScorer?.modelReady) return;
    if (frameId !== 0) return;
    if (!/^https?:/.test(url)) return;

    readyTabs.delete(tabId);

    const feats = extractUrlFeatures(url);
    if (!feats) return;

    try {
        const phishingScore = urlScorer.score(feats);
        putWithLimit(urlScores, tabId, { score: phishingScore, features: feats, url });
        console.log(`URL phishing score for ${url}:`, phishingScore);
        maybeRunMetaModel(tabId);
    } catch (err) {
        console.error('Scoring failed:', err);
    }

});

// Listen for content features
chrome.runtime.onMessage.addListener((request, sender) => {
    if (!urlScorer?.modelReady || !contentScorer?.modelReady || !metaScorer?.modelReady) return;
    if (request.type !== 'CONTENT_FEATURES') return;
    if (sender.frameId !== 0) return;
    if (!sender.tab || typeof sender.tab.id !== 'number') return;

    const tabId = sender.tab.id;
    const contentScore = contentScorer.score(request.data);
    putWithLimit(contentScores, tabId, { score: contentScore, features: request.data });
    maybeRunMetaModel(tabId);
});


chrome.runtime.onMessage.addListener((msg, { tab }) => {
    if (msg.type === 'CONTENT_READY' && tab?.id != null) {
        readyTabs.add(tab.id);
        maybeRunMetaModel(tab.id);
    }
});
