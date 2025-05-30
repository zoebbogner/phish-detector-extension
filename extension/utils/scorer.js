// scorer.js
// XGBoost scorer for models exported with Booster.save_model (JSON, per-tree parallel-array format)
// Supports binary classification with numerical splits (no categorical splits)
// This version loads model and feature index from file paths using fetch (browser/extension environment).
// For Node.js, adapt file loading as needed.

class XGBoostScorer {
  /**
   * @param {string} modelPath - Path to the XGBoost model JSON file
   * @param {string} featureIndexPath - Path to the feature index JSON file
   */
  constructor(modelPath, featureIndexPath) {
    this.modelPath = modelPath;
    this.featureIndexPath = featureIndexPath;
    this.modelReady = false;
    this.treeMeta = [];
    this.featureIndex = {};
    this.indexToName = [];
    this.base_score = 0.5;
    this.baseMargin = 0;
  }

  async init() {
    try {
      // 1. Load model JSON from file path
      const modelResp = await fetch(
        typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.getURL
          ? chrome.runtime.getURL(this.modelPath)
          : this.modelPath
      );
      const fullModel = await modelResp.json();
      const learner = fullModel.learner;
      const modelParam = learner.learner_model_param;
      const raw = learner.gradient_booster.model;
      const trees = raw.trees;
      if (!Array.isArray(trees) || trees.length === 0) {
        throw new Error('Model trees array missing or empty');
      }
      console.log('[XGBoostScorer:init] Loaded model with', trees.length, 'trees');

      // 2. Load feature index JSON from file path
      const idxResp = await fetch(
        typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.getURL
          ? chrome.runtime.getURL(this.featureIndexPath)
          : this.featureIndexPath
      );
      this.featureIndex = await idxResp.json();
      console.log('[XGBoostScorer:init] Loaded feature index');

      // 3. Prepare index→name array
      this.indexToName = [];
      for (const [name, idx] of Object.entries(this.featureIndex)) {
        this.indexToName[idx] = name;
      }

      // 4. Extract and cache hyperparameters
      this.base_score = Number(modelParam.base_score);
      this.baseMargin = Math.log(this.base_score / (1 - this.base_score));

      // 5. Build treeMeta from per-tree arrays
      this.treeMeta = [];
      for (let t = 0; t < trees.length; t++) {
        const tree = trees[t];
        const nodeCount = tree.split_indices.length;
        if (
          !(
            tree.split_conditions.length === nodeCount &&
            tree.default_left.length === nodeCount &&
            tree.left_children.length === nodeCount &&
            tree.right_children.length === nodeCount &&
            tree.base_weights.length === nodeCount
          )
        ) {
          throw new Error(`Tree ${t} arrays have inconsistent node counts`);
        }
        this.treeMeta[t] = {
          split_indices: tree.split_indices,
          split_conditions: tree.split_conditions,
          default_left: tree.default_left,
          left_children: tree.left_children,
          right_children: tree.right_children,
          base_weights: tree.base_weights
        };
      }

      this.modelReady = true;
    } catch (err) {
      this.modelReady = false;
      throw err;
    }
  }

  sigmoid(x) {
    return 1 / (1 + Math.exp(-x));
  }

  margin(features) {
    if (!this.modelReady) throw new Error('XGBoostScorer not initialized. Call init() first.');
    let sum = 0;
    for (let t = 0; t < this.treeMeta.length; t++) {
      const tree = this.treeMeta[t];
      let node = 0;
      const idxs = tree.split_indices;
      let steps = 0;
      while (idxs[node] >= 0) {
        const fidx = idxs[node];
        const cond = tree.split_conditions[node];
        const left = tree.default_left[node];
        const fv = features[this.indexToName[fidx]];
        const goLeft = (fv == null || isNaN(fv)) ? left : (fv < cond);
        const nextNode = goLeft ? tree.left_children[node] : tree.right_children[node];
        if (nextNode === -1) {
          break;
        }
        node = nextNode;
        steps++;
        if (steps > 1000) throw new Error(`[XGBoostScorer:margin] Infinite loop detected in tree ${t}`);
      }
      sum += tree.base_weights[node];
    }
    const margin = this.baseMargin + sum;
    return margin;
  }

  score(features) {
    const margin = this.margin(features);
    const prob = this.sigmoid(margin);
    return prob;
  }
}

export default XGBoostScorer; 