"""
ForensiX CDR Analyzer — Forensic Analysis Tools
8 analysis tools that the AI agent can call via tool-calling.
Each tool takes a pandas DataFrame and returns a dict with 'summary', 'data', and optional 'chart'.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import json


def detect_high_frequency_callers(df: pd.DataFrame, threshold_percentile: float = 95) -> dict:
    """Detect phone numbers with abnormally high total call counts (potential stalking/obsessive patterns)."""
    df = df.copy()
    df["Total_Calls"] = df["Day Calls"] + df["Eve Calls"] + df["Night Calls"] + df["Intl Calls"]
    threshold = np.percentile(df["Total_Calls"], threshold_percentile)
    suspects = df[df["Total_Calls"] >= threshold].sort_values("Total_Calls", ascending=False).head(20)

    fig = px.bar(
        suspects, x="Phone Number", y="Total_Calls",
        color="Total_Calls", color_continuous_scale="Reds",
        title="🔴 High-Frequency Callers (Potential Stalking Pattern)",
        labels={"Total_Calls": "Total Calls", "Phone Number": "Suspect Number"},
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f")

    return {
        "summary": f"Found {len(df[df['Total_Calls'] >= threshold])} numbers above {threshold_percentile}th percentile ({threshold:.0f} calls). "
                   f"Top suspect: {suspects.iloc[0]['Phone Number']} with {suspects.iloc[0]['Total_Calls']:.0f} total calls.",
        "data": suspects[["Phone Number", "Total_Calls", "Day Calls", "Eve Calls", "Night Calls", "Intl Calls"]].to_dict(orient="records"),
        "chart": fig,
    }


def analyze_time_distribution(df: pd.DataFrame) -> dict:
    """Analyze call distribution across day/evening/night periods to find unusual timing patterns."""
    df = df.copy()
    df["Total_Calls"] = df["Day Calls"] + df["Eve Calls"] + df["Night Calls"]
    df["Night_Ratio"] = df["Night Calls"] / df["Total_Calls"].replace(0, 1)
    df["Eve_Ratio"] = df["Eve Calls"] / df["Total_Calls"].replace(0, 1)

    # Flag those with >50% night activity
    night_suspects = df[df["Night_Ratio"] > 0.45].sort_values("Night_Ratio", ascending=False).head(20)

    fig = go.Figure()
    for period, col, color in [("Day", "Day Calls", "#ffd700"), ("Evening", "Eve Calls", "#ff6b35"), ("Night", "Night Calls", "#dc143c")]:
        fig.add_trace(go.Box(y=df[col], name=period, marker_color=color))
    fig.update_layout(
        title="📊 Call Distribution by Time Period", template="plotly_dark",
        paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f", yaxis_title="Number of Calls",
    )

    return {
        "summary": f"Found {len(night_suspects)} numbers with >45% night-time call ratio. "
                   f"Average night ratio across dataset: {df['Night_Ratio'].mean():.2%}. "
                   f"Most nocturnal: {night_suspects.iloc[0]['Phone Number'] if len(night_suspects) > 0 else 'N/A'}.",
        "data": night_suspects[["Phone Number", "Night Calls", "Night_Ratio", "Day Calls", "Eve Calls"]].to_dict(orient="records"),
        "chart": fig,
    }


def detect_anomalous_charges(df: pd.DataFrame, z_threshold: float = 2.5) -> dict:
    """Detect statistically anomalous call charges using z-score analysis (potential fraud indicators)."""
    charge_cols = ["Day Charge", "Eve Charge", "Night Charge", "Intl Charge"]
    df = df.copy()
    df["Total_Charge"] = df[charge_cols].sum(axis=1)

    mean_charge = df["Total_Charge"].mean()
    std_charge = df["Total_Charge"].std()
    df["Z_Score"] = (df["Total_Charge"] - mean_charge) / std_charge
    anomalies = df[df["Z_Score"].abs() > z_threshold].sort_values("Z_Score", ascending=False).head(20)

    fig = px.histogram(
        df, x="Total_Charge", nbins=80, color_discrete_sequence=["#4a90d9"],
        title="💰 Charge Distribution with Anomaly Threshold",
    )
    threshold_val = mean_charge + z_threshold * std_charge
    fig.add_vline(x=threshold_val, line_dash="dash", line_color="red", annotation_text=f"Anomaly Threshold (z={z_threshold})")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f")

    return {
        "summary": f"Found {len(anomalies)} anomalous charge records (z-score > {z_threshold}). "
                   f"Mean charge: ${mean_charge:.2f}, Threshold: ${threshold_val:.2f}. "
                   f"Highest anomaly: {anomalies.iloc[0]['Phone Number'] if len(anomalies) > 0 else 'N/A'} at ${anomalies.iloc[0]['Total_Charge']:.2f}.",
        "data": anomalies[["Phone Number", "Total_Charge", "Z_Score"] + charge_cols].to_dict(orient="records"),
        "chart": fig,
    }


def find_suspicious_international(df: pd.DataFrame, intl_call_threshold: int = 8) -> dict:
    """Flag numbers with unusually high international call activity (potential cross-border criminal comms)."""
    df = df.copy()
    suspects = df[df["Intl Calls"] >= intl_call_threshold].sort_values("Intl Calls", ascending=False).head(20)

    fig = px.scatter(
        df, x="Intl Calls", y="Intl Charge", hover_data=["Phone Number"],
        color="Intl Calls", color_continuous_scale="YlOrRd",
        title="🌍 International Call Activity (Flagged Above Threshold)",
    )
    fig.add_vline(x=intl_call_threshold, line_dash="dash", line_color="red", annotation_text="Suspicious Threshold")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f")

    return {
        "summary": f"Found {len(df[df['Intl Calls'] >= intl_call_threshold])} numbers with {intl_call_threshold}+ international calls. "
                   f"Average intl calls: {df['Intl Calls'].mean():.1f}. "
                   f"Top suspect: {suspects.iloc[0]['Phone Number'] if len(suspects) > 0 else 'N/A'} with {suspects.iloc[0]['Intl Calls']} intl calls.",
        "data": suspects[["Phone Number", "Intl Calls", "Intl Mins", "Intl Charge"]].to_dict(orient="records"),
        "chart": fig,
    }


def cluster_behavior_patterns(df: pd.DataFrame, n_clusters: int = 5) -> dict:
    """Use K-Means clustering to group phone numbers by behavioral patterns and identify suspicious clusters."""
    features = ["Day Mins", "Eve Mins", "Night Mins", "Intl Mins", "Day Calls", "Eve Calls", "Night Calls", "Intl Calls"]
    df = df.copy()
    X = df[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["Cluster"] = kmeans.fit_predict(X_scaled)

    cluster_stats = df.groupby("Cluster")[features].mean().round(1)
    cluster_sizes = df["Cluster"].value_counts().sort_index()

    fig = px.scatter(
        df.sample(min(2000, len(df)), random_state=42),
        x="Day Mins", y="Night Mins", color="Cluster",
        hover_data=["Phone Number", "Intl Calls"],
        title="🧩 Behavioral Clusters (Day vs Night Activity)",
        color_continuous_scale="Viridis",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f")

    smallest_cluster = cluster_sizes.idxmin()
    return {
        "summary": f"Identified {n_clusters} behavioral clusters. Smallest cluster ({smallest_cluster}) has {cluster_sizes[smallest_cluster]} members — "
                   f"potential outlier group. Cluster sizes: {cluster_sizes.to_dict()}.",
        "data": {"cluster_stats": cluster_stats.to_dict(orient="index"), "cluster_sizes": cluster_sizes.to_dict()},
        "chart": fig,
    }


def detect_burner_phones(df: pd.DataFrame, max_account_length: int = 40) -> dict:
    """Detect potential burner phones: short account life + high activity (classic criminal communication)."""
    df = df.copy()
    df["Total_Calls"] = df["Day Calls"] + df["Eve Calls"] + df["Night Calls"] + df["Intl Calls"]
    df["Calls_Per_Day"] = df["Total_Calls"] / df["Account Length"].replace(0, 1)

    burners = df[df["Account Length"] <= max_account_length].sort_values("Calls_Per_Day", ascending=False).head(20)

    fig = px.scatter(
        df, x="Account Length", y="Total_Calls", hover_data=["Phone Number"],
        color="Calls_Per_Day", color_continuous_scale="Hot",
        title="🔥 Burner Phone Detection (Short Life + High Activity)",
    )
    fig.add_vrect(x0=0, x1=max_account_length, fillcolor="red", opacity=0.1, annotation_text="Burner Zone")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f")

    return {
        "summary": f"Found {len(df[df['Account Length'] <= max_account_length])} accounts under {max_account_length} days. "
                   f"Highest activity rate: {burners.iloc[0]['Phone Number'] if len(burners) > 0 else 'N/A'} "
                   f"with {burners.iloc[0]['Calls_Per_Day']:.1f} calls/day.",
        "data": burners[["Phone Number", "Account Length", "Total_Calls", "Calls_Per_Day"]].to_dict(orient="records"),
        "chart": fig,
    }


def correlation_analysis(df: pd.DataFrame) -> dict:
    """Analyze correlations between call features to find hidden relationships in the evidence."""
    numeric_cols = ["Account Length", "VMail Message", "Day Mins", "Day Calls", "Eve Mins",
                    "Eve Calls", "Night Mins", "Night Calls", "Intl Mins", "Intl Calls", "CustServ Calls"]
    corr_matrix = df[numeric_cols].corr().round(3)

    fig = px.imshow(
        corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r",
        title="🔗 Feature Correlation Matrix (Hidden Relationships)",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f", width=800, height=700)

    strong_corrs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            val = corr_matrix.iloc[i, j]
            if abs(val) > 0.5:
                strong_corrs.append({"Feature 1": corr_matrix.columns[i], "Feature 2": corr_matrix.columns[j], "Correlation": val})

    return {
        "summary": f"Found {len(strong_corrs)} strong correlations (|r| > 0.5). "
                   + (f"Strongest: {strong_corrs[0]['Feature 1']} ↔ {strong_corrs[0]['Feature 2']} (r={strong_corrs[0]['Correlation']:.3f})." if strong_corrs else "No strong cross-feature correlations found."),
        "data": strong_corrs,
        "chart": fig,
    }


def generate_suspect_timeline(df: pd.DataFrame, phone_number: str = None) -> dict:
    """Generate a detailed activity profile for a specific suspect phone number."""
    df = df.copy()
    if phone_number is None or phone_number not in df["Phone Number"].values:
        df["Total_Calls"] = df["Day Calls"] + df["Eve Calls"] + df["Night Calls"] + df["Intl Calls"]
        phone_number = df.sort_values("Total_Calls", ascending=False).iloc[0]["Phone Number"]

    suspect = df[df["Phone Number"] == phone_number].iloc[0]

    categories = ["Day Calls", "Eve Calls", "Night Calls", "Intl Calls"]
    values = [suspect[c] for c in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]],
                                   fill="toself", fillcolor="rgba(220, 20, 60, 0.3)", line_color="#dc143c", name="Activity"))
    fig.update_layout(
        title=f"🎯 Suspect Profile: {phone_number}",
        polar=dict(bgcolor="#0a0a0f", radialaxis=dict(gridcolor="#1a1a2e")),
        template="plotly_dark", paper_bgcolor="#0a0a0f",
    )

    churn_status = suspect.get("Churn", "UNKNOWN")
    return {
        "summary": f"Suspect {phone_number}: Account age {suspect['Account Length']} days, "
                   f"Day={suspect['Day Calls']} calls, Eve={suspect['Eve Calls']}, Night={suspect['Night Calls']}, "
                   f"Intl={suspect['Intl Calls']}, CustServ={suspect['CustServ Calls']}x, Churn={churn_status}.",
        "data": suspect.to_dict(),
        "chart": fig,
    }


# Registry of all tools with their metadata for the agent
TOOL_REGISTRY = {
    "detect_high_frequency_callers": {
        "fn": detect_high_frequency_callers,
        "description": "Detect phone numbers with abnormally high total call counts. Identifies potential stalking or obsessive calling patterns.",
        "icon": "🔴",
    },
    "analyze_time_distribution": {
        "fn": analyze_time_distribution,
        "description": "Analyze call distribution across day/evening/night. Flags numbers with unusually high night-time activity.",
        "icon": "🌙",
    },
    "detect_anomalous_charges": {
        "fn": detect_anomalous_charges,
        "description": "Find statistically anomalous call charges using z-score analysis. Detects potential fraud or premium-rate abuse.",
        "icon": "💰",
    },
    "find_suspicious_international": {
        "fn": find_suspicious_international,
        "description": "Flag numbers with unusually high international call activity. Detects potential cross-border criminal communications.",
        "icon": "🌍",
    },
    "cluster_behavior_patterns": {
        "fn": cluster_behavior_patterns,
        "description": "Group phone numbers into behavioral clusters using K-Means. Identifies outlier groups with suspicious behavior.",
        "icon": "🧩",
    },
    "detect_burner_phones": {
        "fn": detect_burner_phones,
        "description": "Detect short-lived accounts with high call activity — classic burner phone pattern used by criminals.",
        "icon": "🔥",
    },
    "correlation_analysis": {
        "fn": correlation_analysis,
        "description": "Analyze correlations between all call features to discover hidden relationships in the evidence.",
        "icon": "🔗",
    },
    "generate_suspect_timeline": {
        "fn": generate_suspect_timeline,
        "description": "Generate a detailed activity profile and radar chart for a specific suspect phone number.",
        "icon": "🎯",
    },
}
