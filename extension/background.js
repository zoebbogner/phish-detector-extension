// background.js (MV3 module)
// This service worker loads the URL feature extractor and the XGBoost URL-model scorer
// and scores every navigation as soon as the URL is known.

import { extractUrlFeatures } from './utils/url_features.js';
import { putWithLimit } from './utils/cache.js';
import XGBoostScorer from './utils/scorer.js';

let urlScorer = null;
let contentScorer = null;
let metaScorer = null;

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
    if (!urlScores.has(tabId) || !contentScores.has(tabId)) return;
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
    
}

// Listen for committed navigations
chrome.webNavigation.onCommitted.addListener(({ url, frameId, tabId }) => {
    if (!urlScorer?.modelReady) return;
    if (frameId !== 0) return;
    if (!/^https?:/.test(url)) return;

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

