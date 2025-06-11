import pandas as pd
import matplotlib.pyplot as plt
import time
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc

def plot_class_balance(df, label_col='label', title='Class Balance (Label 0 = Benign, Label 1 = Phishing)'):
    """
    Plot the class balance of a DataFrame, showing both ratio and raw counts per label.

    Parameters:
    - df: pandas DataFrame containing the data.
    - label_col: name of the column containing class labels (default 'label').
    - title: Title for the plot.
    """
    counts = df[label_col].value_counts()
    ratios = counts / counts.sum()
    balance_df = pd.DataFrame({'count': counts, 'ratio': ratios})
    balance_df.index.name = label_col
    balance_df = balance_df.reset_index()

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(
        balance_df[label_col].astype(str),
        balance_df['ratio'],
        color=['#4C72B0', '#55A868'],
        edgecolor='black',
        alpha=0.8
    )

    # Annotate bar tops with percentage and count
    for i, row in balance_df.iterrows():
        pct = row['ratio'] * 100
        cnt = row['count']
        ax.text(
            i,
            row['ratio'] + 0.01,
            f"{pct:.1f}%\n({cnt:,})",
            ha='center',
            va='bottom',
            fontsize=10
        )

    ax.set_xlabel('Label', fontsize=12)
    ax.set_ylabel('Proportion of Total', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_ylim(0, 1.05)
    unique_labels = balance_df[label_col].astype(int).unique()
    xticks = list(map(str, unique_labels))
    ax.set_xticks(range(len(xticks)))
    # Provide human-readable labels if only 0/1
    if set(unique_labels) == {0, 1}:
        ax.set_xticklabels(['0 (Benign)', '1 (Phishing)'], fontsize=11)
    else:
        ax.set_xticklabels(xticks, fontsize=11)

    # Show y-axis as percentages
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()


def split_data(df, feature_cols, label_col='label', test_size=0.2, random_state=None):
    """
    Split the DataFrame into train and test sets based on specified feature columns and label column.

    Parameters:
    - df: pandas DataFrame containing the data.
    - feature_cols: list of column names to use as features.
    - label_col: name of the column containing class labels (default 'label').
    - test_size: proportion of the data to include in the test split (default 0.2).
    - random_state: random seed for reproducibility.

    Returns:
    - X_train, X_test, y_train, y_test
    """
    X = df[feature_cols]
    y = df[label_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )
    print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    return X_train, X_test, y_train, y_test


def cross_validate_models(model_name, model, X_train, y_train, cv_splits=5, random_state=None, scoring='f1'):
    """
    Perform cross-validation for a single model and return results as a DataFrame.

    Parameters:
    - model_name: name of the model.
    - model: model instance.
    - X_train: training features.
    - y_train: training labels.
    - cv_splits: number of folds for StratifiedKFold (default 5).
    - random_state: random seed for StratifiedKFold shuffling.
    - scoring: scoring metric for cross-validation (default 'f1').

    Returns:
    - pandas DataFrame with columns ['F1 Mean', 'F1 Std', 'Elapsed (s)'] indexed by model names.
    """
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=random_state)
    results_list = []

    start = time.perf_counter()
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=scoring)
    end = time.perf_counter()

    mean_score = scores.mean()
    std_score = scores.std()
    elapsed = end - start

    results_list.append({
        "Model": model_name,
        "F1 Mean": f"{mean_score:.4f}",
        "F1 Std": f"{std_score:.4f}",
        "Elapsed (s)": f"{elapsed:.2f}"
    })

    results_df = pd.DataFrame(results_list).set_index("Model")
    print("\nCross‐Validation Results:\n")
    print(results_df)
    return results_df


def train_and_evaluate_models(model_name, model, X_train, y_train, X_test, y_test):
    """
    Train a model on the training set, then evaluate on test set. Prints classification reports,
    plots confusion matrices, and plots ROC curves.

    Parameters:
    - model_name: name of the model.
    - model: model instance.
    - X_train, y_train: training data.
    - X_test, y_test: test data.

    Returns:
    - results: dict mapping model names to a sub-dict with keys 'model', 'y_pred', 'y_proba'.
    """
    results = {}
    plt.figure(figsize=(6, 4))
    
    # Train
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)
    if hasattr(model, 'predict_proba'):
        y_proba = model.predict_proba(X_test)[:, 1]
        
    else:
        y_proba = None

    results[model_name] = {
        'model': model_name,
        'y_pred': y_pred,
        'y_proba': y_proba
    }

    # Classification report
    print(f"\n=== {model_name} ===")
    print(classification_report(y_test, y_pred))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.title(f"{model_name} Confusion Matrix")
    plt.show()

    # ROC curve (if probabilities available)
    if y_proba is not None:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{model_name} (AUC = {roc_auc:.5f})")

    if results[model_name]['y_proba'] is not None:
        plt.plot([0, 1], [0, 1], 'k--', linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves')
        plt.legend(loc='lower right')
        plt.grid(True)
        plt.show()

    return results