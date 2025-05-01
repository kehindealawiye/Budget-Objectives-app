import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(layout="wide")
st.title("📊 Manual KPI Chart Generator")

# Chart title input
chart_title = st.text_input("Enter chart title:", value="Modern Infrastructure KPI Performance")

# Legend style toggle
legend_style = st.radio("Legend Style:", ["Separate (default)", "Unified (bottom combined legend)"])

# Score line style toggle
score_line_style = st.radio("Score Line Style:", ["Black line", "Colored dots by score"])

# Data input
st.markdown("### Paste your data below for each column (one item per line):")
kpi_text = st.text_area("KPI")
avg_score_text = st.text_area("Average Score (%)")
green_text = st.text_area("Count of Green")
amber_text = st.text_area("Count of Amber")
red_text = st.text_area("Count of Red")

# Helper: score-based color
def score_color(score):
    if score < 60:
        return "red"
    elif score < 80:
        return "orange"
    else:
        return "green"

if st.button("Generate Chart"):
    try:
        # Parse input
        kpis = [x.strip() for x in kpi_text.strip().split('\n') if x.strip()]
        avg_scores = [float(x.strip().replace('%', '')) for x in avg_score_text.strip().split('\n') if x.strip()]
        greens = [int(x.strip()) for x in green_text.strip().split('\n') if x.strip()]
        ambers = [int(x.strip()) for x in amber_text.strip().split('\n') if x.strip()]
        reds = [int(x.strip()) for x in red_text.strip().split('\n') if x.strip()]

        if not all(len(lst) == len(kpis) for lst in [avg_scores, greens, ambers, reds]):
            st.error("All columns must have the same number of entries.")
        else:
            # Build DataFrame
            df = pd.DataFrame({
                "KPI": kpis,
                "Average Score": avg_scores,
                "Green": greens,
                "Amber": ambers,
                "Red": reds
            })
            df["Total"] = df["Green"] + df["Amber"] + df["Red"]

            fig, ax1 = plt.subplots(figsize=(14, 7))

            # Bar chart
            ax1.bar(df["KPI"], df["Green"], label="Green", color="green")
            ax1.bar(df["KPI"], df["Amber"], bottom=df["Green"], label="Amber", color="orange")
            ax1.bar(df["KPI"], df["Red"], bottom=df["Green"] + df["Amber"], label="Red", color="red")
            ax1.set_ylabel("Count of Status")
            ax1.tick_params(axis='x', rotation=90)

            # Score line
            ax2 = ax1.twinx()
            ax2.set_ylabel("Average Score (%)")
            ax2.set_ylim(0, 100)

            if score_line_style == "Black line":
                ax2.plot(df["KPI"], df["Average Score"], color="black", marker="o", label="Average Score (%)")
            else:
                colors = [score_color(score) for score in df["Average Score"]]
                for i, (x, y, c) in enumerate(zip(df["KPI"], df["Average Score"], colors)):
                    ax2.plot(i, y, 'o', color=c, markersize=8)
                # Fake handles for colored dot legend
                from matplotlib.lines import Line2D
                custom_dots = [
                    Line2D([0], [0], marker='o', color='w', label='Avg Score 0–59%', markerfacecolor='red', markersize=8),
                    Line2D([0], [0], marker='o', color='w', label='Avg Score 60–79%', markerfacecolor='orange', markersize=8),
                    Line2D([0], [0], marker='o', color='w', label='Avg Score 80–100%', markerfacecolor='green', markersize=8),
                ]

            # Title
            ax1.set_title(chart_title.strip() or "KPI Chart")

            # Legend
            if legend_style == "Separate (default)":
                ax1.legend(loc="upper left")
                if score_line_style == "Black line":
                    ax2.legend(loc="upper right")
                else:
                    ax1.legend(handles=custom_dots, loc="upper right")
            else:
                bars_legend, bars_labels = ax1.get_legend_handles_labels()
                if score_line_style == "Black line":
                    line_legend, line_labels = ax2.get_legend_handles_labels()
                else:
                    line_legend = custom_dots
                    line_labels = [h.get_label() for h in custom_dots]

                ax1.legend(
                    bars_legend + line_legend,
                    bars_labels + line_labels,
                    loc="lower center",
                    bbox_to_anchor=(0.5, -0.3),
                    ncol=4,
                    frameon=False
                )
                fig.subplots_adjust(bottom=0.35)

            st.pyplot(fig)

            # Download
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            st.download_button(
                label="📥 Download Chart as PNG",
                data=buf.getvalue(),
                file_name="kpi_chart.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
