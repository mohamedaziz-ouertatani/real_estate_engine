import pandas as pd


def extract_feature_importance(pipeline, top_n=20):
    """
    Extract feature importance from a trained sklearn Pipeline
    with ColumnTransformer + tree-based model.
    """

    if "preprocessor" not in pipeline.named_steps:
        raise ValueError("Pipeline missing preprocessor step")

    if "model" not in pipeline.named_steps:
        raise ValueError("Pipeline missing model step")

    model = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]

    if not hasattr(model, "feature_importances_"):
        raise ValueError("Model does not support feature importance")

    # ----------------------------------
    # Collect transformed feature names
    # ----------------------------------
    feature_names = []

    for name, transformer, columns in preprocessor.transformers_:
        if transformer == "drop":
            continue

        if name == "cat":
            encoder = transformer.named_steps["onehot"]
            encoded = encoder.get_feature_names_out(columns)
            feature_names.extend(encoded.tolist())
        else:
            feature_names.extend(columns)

    importances = model.feature_importances_

    df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    })

    df = df.sort_values("importance", ascending=False)
    return df.head(top_n)


def aggregate_by_prefix(df):
    """
    Groups one-hot encoded features by prefix.
    Example: locality_Sahloul → locality
    """

    grouped = {}
    for _, row in df.iterrows():
        prefix = row["feature"].split("_")[0]
        grouped[prefix] = grouped.get(prefix, 0) + row["importance"]

    return (
        pd.DataFrame(grouped.items(), columns=["feature_group", "importance"])
        .sort_values("importance", ascending=False)
    )
