import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score,
    recall_score, roc_auc_score, classification_report
)
from utils.data.content_feature_extractor import ContentFeatureExtractor
from config import (
    CONTENT_RAW_DATA_PATH,
    CONTENT_TFIDF_VECT_PATH,
    CONTENT_MODEL_PATH,
    TEST_SIZE,
    RANDOM_STATE,
    CONTENT_TFIDF_PARAMS,
    CONTENT_MODEL_DIR,
)
from utils.ml_helpers import save_classification_report, print_confusion_matrix

def main():
    # 1) Load labeled URLs + labels
    df = pd.read_csv(CONTENT_RAW_DATA_PATH)
    urls, y = df["url"].tolist(), df["label"].values

    # 2) Load TF-IDF vectorizer & transform texts
    cfe = ContentFeatureExtractor(tfidf_params=CONTENT_TFIDF_PARAMS)
    cfe.load_vectorizer(CONTENT_TFIDF_VECT_PATH)
    texts = [cfe.fetch_and_clean(u) for u in urls]
    X = cfe.transform_tfidf(texts)

    # 3) Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE
    )

    # 4) Load trained model & predict
    model = joblib.load(CONTENT_MODEL_PATH)
    y_pred = model.predict(X_test)
    try:
        y_proba = model.predict_proba(X_test)[:, 1]
    except AttributeError:
        y_proba = None

    # 5) Print & save metrics
    print("[INFO] Classification Report:\n", classification_report(y_test, y_pred))
    save_classification_report(classification_report(y_test, y_pred, output_dict=False),
                               f"{CONTENT_MODEL_DIR}/content_classification_report.txt")
    print_confusion_matrix(y_test, y_pred)

    # 6) Optional: feature-importance plot (for XGBoost)
    if hasattr(model, "feature_importances_"):
        from utils.ml_helpers import plot_feature_importance
        plot_feature_importance(model, f"{CONTENT_MODEL_DIR}/content_feature_importance.png")

if __name__ == "__main__":
    main()
