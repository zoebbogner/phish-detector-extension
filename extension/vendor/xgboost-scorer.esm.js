function getDefaultExportFromCjs (x) {
	return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, 'default') ? x['default'] : x;
}

var dist = {};

var hasRequiredDist;

function requireDist () {
	if (hasRequiredDist) return dist;
	hasRequiredDist = 1;
	var __awaiter = (dist && dist.__awaiter) || function (thisArg, _arguments, P, generator) {
	    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
	    return new (P || (P = Promise))(function (resolve, reject) {
	        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
	        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
	        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
	        step((generator = generator.apply(thisArg, _arguments || [])).next());
	    });
	};
	var __generator = (dist && dist.__generator) || function (thisArg, body) {
	    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
	    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
	    function verb(n) { return function (v) { return step([n, v]); }; }
	    function step(op) {
	        if (f) throw new TypeError("Generator is already executing.");
	        while (_) try {
	            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
	            if (y = 0, t) op = [op[0] & 2, t.value];
	            switch (op[0]) {
	                case 0: case 1: t = op; break;
	                case 4: _.label++; return { value: op[1], done: false };
	                case 5: _.label++; y = op[1]; op = [0]; continue;
	                case 7: op = _.ops.pop(); _.trys.pop(); continue;
	                default:
	                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
	                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
	                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
	                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
	                    if (t[2]) _.ops.pop();
	                    _.trys.pop(); continue;
	            }
	            op = body.call(thisArg, _);
	        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
	        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
	    }
	};
	var __asyncValues = (dist && dist.__asyncValues) || function (o) {
	    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
	    var m = o[Symbol.asyncIterator], i;
	    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
	    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
	    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
	};
	Object.defineProperty(dist, "__esModule", { value: true });
	function loadJson(file) {
	    return __awaiter(this, void 0, void 0, function () {
	        var fs, buffer;
	        return __generator(this, function (_a) {
	            switch (_a.label) {
	                case 0: return [4 /*yield*/, Promise.resolve().then(function () { return require("fs"); })];
	                case 1:
	                    fs = _a.sent();
	                    return [4 /*yield*/, fs.promises.readFile(file)];
	                case 2:
	                    buffer = _a.sent();
	                    return [2 /*return*/, JSON.parse(buffer.toString())];
	            }
	        });
	    });
	}
	function sigmoid(x) {
	    return 1 / (1 + Math.pow(Math.E, -x));
	}
	function isLeaf(node) {
	    return node.leaf !== undefined;
	}
	var Scorer = /** @class */ (function () {
	    function Scorer() {
	    }
	    Scorer.create = function (model, featureIndex) {
	        return __awaiter(this, void 0, void 0, function () {
	            var scorer, _a, _b, loadedFeatureIndex_1, _c;
	            return __generator(this, function (_d) {
	                switch (_d.label) {
	                    case 0:
	                        scorer = new Scorer;
	                        _a = scorer;
	                        if (!(typeof model === "string")) return [3 /*break*/, 2];
	                        return [4 /*yield*/, loadJson(model)];
	                    case 1:
	                        _b = _d.sent();
	                        return [3 /*break*/, 3];
	                    case 2:
	                        _b = model;
	                        _d.label = 3;
	                    case 3:
	                        _a.model = _b;
	                        if (!featureIndex) return [3 /*break*/, 7];
	                        if (!(typeof featureIndex === "string")) return [3 /*break*/, 5];
	                        return [4 /*yield*/, loadJson(featureIndex)];
	                    case 4:
	                        _c = _d.sent();
	                        return [3 /*break*/, 6];
	                    case 5:
	                        _c = featureIndex;
	                        _d.label = 6;
	                    case 6:
	                        loadedFeatureIndex_1 = _c;
	                        scorer.reverseFeatureIndex =
	                            Object.keys(loadedFeatureIndex_1)
	                                .reduce(function (acc, fName) {
	                                var fIdx = loadedFeatureIndex_1[fName];
	                                acc["" + fIdx] = fName;
	                                return acc;
	                            }, {});
	                        _d.label = 7;
	                    case 7: return [2 /*return*/, scorer];
	                }
	            });
	        });
	    };
	    Scorer.prototype.scoreSingleInstance = function (features) {
	        if (!this.model) {
	            throw new Error("Scorer not initialized, create a scorer using Scorer.create() only");
	        }
	        var totalScore = this.model
	            .map(function (booster) {
	            var currNode = booster;
	            var _loop_1 = function () {
	                var splitFeature = currNode.split;
	                var nextNodeId;
	                if (features[splitFeature] !== undefined) {
	                    var conditionResult = features[splitFeature] < currNode.split_condition;
	                    nextNodeId = conditionResult ? currNode.yes : currNode.no;
	                }
	                else {
	                    // Missing feature
	                    nextNodeId = currNode.missing;
	                }
	                var nextNode = currNode.children.find(function (child) { return child.nodeid === nextNodeId; });
	                if (nextNode === undefined) {
	                    throw new Error("Invalid model JSON, missing node ID: " + nextNodeId);
	                }
	                currNode = nextNode;
	            };
	            while (!isLeaf(currNode)) {
	                _loop_1();
	            }
	            return currNode.leaf;
	        })
	            .reduce(function (score, boosterScore) { return score + boosterScore; }, 0.0);
	        return sigmoid(totalScore);
	    };
	    Scorer.prototype.score = function (input) {
	        var e_1, _a;
	        return __awaiter(this, void 0, void 0, function () {
	            var fs, readline, inputStream, rl, scores, rl_1, rl_1_1, line, features, score, e_1_1;
	            var _this = this;
	            return __generator(this, function (_b) {
	                switch (_b.label) {
	                    case 0:
	                        if (typeof input !== "string" && typeof input !== "object") {
	                            throw new Error("Invalid input to score method: " + input + ", expected string or object, was " + typeof input);
	                        }
	                        // Scoring a single instance or array of instances
	                        if (typeof input === "object") {
	                            if (Array.isArray(input)) {
	                                return [2 /*return*/, input.map(function (en) { return _this.scoreSingleInstance(en); })];
	                            }
	                            else {
	                                return [2 /*return*/, this.scoreSingleInstance(input)];
	                            }
	                        }
	                        if (!this.reverseFeatureIndex) {
	                            throw new Error("Cannot score LibSVM input without a feature index, please specify one while creating a scorer.");
	                        }
	                        return [4 /*yield*/, Promise.resolve().then(function () { return require("fs"); })];
	                    case 1:
	                        fs = _b.sent();
	                        return [4 /*yield*/, Promise.resolve().then(function () { return require("readline"); })];
	                    case 2:
	                        readline = _b.sent();
	                        inputStream = fs.createReadStream(input);
	                        rl = readline.createInterface({
	                            input: inputStream,
	                            crlfDelay: Infinity
	                        });
	                        scores = [];
	                        _b.label = 3;
	                    case 3:
	                        _b.trys.push([3, 8, 9, 14]);
	                        rl_1 = __asyncValues(rl);
	                        _b.label = 4;
	                    case 4: return [4 /*yield*/, rl_1.next()];
	                    case 5:
	                        if (!(rl_1_1 = _b.sent(), !rl_1_1.done)) return [3 /*break*/, 7];
	                        line = rl_1_1.value;
	                        features = line
	                            .split(" ")
	                            .slice(1)
	                            .map(function (p) { return p.split(":"); })
	                            .map(function (_a) {
	                            var featureId = _a[0], value = _a[1];
	                            return [_this.reverseFeatureIndex[featureId], value];
	                        })
	                            .reduce(function (featureMap, entry) {
	                            var featureName = entry[0], featureValue = entry[1];
	                            featureMap[featureName] = parseFloat(featureValue);
	                            return featureMap;
	                        }, {});
	                        score = this.scoreSingleInstance(features);
	                        scores.push(score);
	                        _b.label = 6;
	                    case 6: return [3 /*break*/, 4];
	                    case 7: return [3 /*break*/, 14];
	                    case 8:
	                        e_1_1 = _b.sent();
	                        e_1 = { error: e_1_1 };
	                        return [3 /*break*/, 14];
	                    case 9:
	                        _b.trys.push([9, , 12, 13]);
	                        if (!(rl_1_1 && !rl_1_1.done && (_a = rl_1.return))) return [3 /*break*/, 11];
	                        return [4 /*yield*/, _a.call(rl_1)];
	                    case 10:
	                        _b.sent();
	                        _b.label = 11;
	                    case 11: return [3 /*break*/, 13];
	                    case 12:
	                        if (e_1) throw e_1.error;
	                        return [7 /*endfinally*/];
	                    case 13: return [7 /*endfinally*/];
	                    case 14: return [2 /*return*/, scores];
	                }
	            });
	        });
	    };
	    return Scorer;
	}());
	dist.default = Scorer;
	return dist;
}

var distExports = requireDist();
var index = /*@__PURE__*/getDefaultExportFromCjs(distExports);

export { index as default };
