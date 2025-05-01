import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from matplotlib.lines import Line2D

st.set_page_config(layout="wide")
st.title("📊 Manual KPI Chart Generator")

# Inputs
chart_title = st.selectbox(
    "Select chart title:",
    [
        "Modern Infrastructure KPI Performance",
        "Thriving Economy KPI Performance",
        "Human Centric City KPI Performance",
        "Effective Governance KPI Performance"
    ]
)

legend_style = st.radio("Legend Style:", ["Separate (default)", "Unified (bottom combined legend)"])
score_line_style = st.radio("Score Line Style:", ["Black line", "Colored dots by score"])
stack_type = st.radio("Bar Height:", ["Raw counts (default)", "100% stacked (proportional)"])
label_option = st.radio("Chart Labels:", ["No labels", "Show total only", "Show all segment labels"])

# Data input areas
st.markdown("### Paste your data below for each column (one item per line):")
kpi_text = st.text_area("KPI")
avg_score_text = st.text_area("Average Score (%)")
green_text = st.text_area("Count of Green")
amber_text = st.text_area("Count of Amber")
red_text = st.text_area("Count of Red")

# Score color logic
def score_color(score):
    if score < 60:
        return "red"
    elif score < 80:
        return "orange"
    else:
        return "green"

# Chart rendering
if st.button("Generate Chart"):
    try:
        kpis = [x.strip() for x in kpi_text.strip().split('\n') if x.strip()]
        avg_scores = [float(x.strip().replace('%', '')) for x in avg_score_text.strip().split('\n') if x.strip()]
        greens = [int(x.strip()) for x in green_text.strip().split('\n') if x.strip()]
        ambers = [int(x.strip()) for x in amber_text.strip().split('\n') if x.strip()]
        reds = [int(x.strip()) for x in red_text.strip().split('\n') if x.strip()]

        if not all(len(lst) == len(kpis) for lst in [avg_scores, greens, ambers, reds]):
            st.error("All columns must have the same number of entries.")
        else:
            df = pd.DataFrame({
                "KPI": kpis,
                "Average Score": avg_scores,
                "Green": greens,
                "Amber": ambers,
                "Red": reds
            })

            fig, ax1 = plt.subplots(figsize=(14, 7))

            if stack_type == "100% stacked (proportional)":
                df["Total"] = df["Green"] + df["Amber"] + df["Red"]
                df["Green %"] = df["Green"] / df["Total"] * 100
                df["Amber %"] = df["Amber"] / df["Total"] * 100
                df["Red %"] = df["Red"] / df["Total"] * 100
                y1 = df["Green %"]
                y2 = df["Amber %"]
                y3 = df["Red %"]
                ax1.bar(df["KPI"], y1, label="Number of Projects in Green", color="green")
                ax1.bar(df["KPI"], y2, bottom=y1, label="Number of Projects in Amber", color="orange")
                ax1.bar(df["KPI"], y3, bottom=y1 + y2, label="Number of Projects in Red", color="red")
                ax1.set_ylabel("Proportion (%)")
                ax1.set_ylim(0, 100)
            else:
                y1 = df["Green"]
                y2 = df["Amber"]
                y3 = df["Red"]
                ax1.bar(df["KPI"], y1, label="Number of Projects in Green", color="green")
                ax1.bar(df["KPI"], y2, bottom=y1, label="Number of Projects in Amber", color="orange")
                ax1.bar(df["KPI"], y3, bottom=y1 + y2, label="Number of Projects in Red", color="red")
                ax1.set_ylabel("Number of Projects")

            ax1.tick_params(axis='x', rotation=90)

            # Add labels
            for i in range(len(df)):
                green_val = y1[i]
                amber_val = y2[i]
                red_val = y3[i]
                total_val = green_val + amber_val + red_val

                if label_option == "Show total only":
                    ax1.text(i, total_val + (2 if stack_type == "Raw counts (default)" else 1.5), 
                             f"{int(total_val)}", ha='center', va='bottom', fontsize=9, fontweight='bold')

                elif label_option == "Show all segment labels":
                    if green_val > 0:
                        ax1.text(i, green_val / 2, f"{int(green_val)}", ha='center', va='center', color='white', fontsize=8, fontweight='bold')
                    if amber_val > 0:
                        ax1.text(i, green_val + amber_val / 2, f"{int(amber_val)}", ha='center', va='center', color='black', fontsize=8, fontweight='bold')
                    if red_val > 0:
                        ax1.text(i, green_val + amber_val + red_val / 2, f"{int(red_val)}", ha='center', va='center', color='white', fontsize=8, fontweight='bold')

            # Score line
            ax2 = ax1.twinx()
            ax2.set_ylim(0, 100)
            ax2.set_ylabel("Average Score (%)")
            ax2.plot(df["KPI"], df["Average Score"], color="black", linewidth=1)

            if score_line_style == "Colored dots by score":
                colors = [score_color(score) for score in df["Average Score"]]
                for i, (x, y, c) in enumerate(zip(df["KPI"], df["Average Score"], colors)):
                    ax2.plot(i, y, 'o', color=c, markersize=8)
                dot_legend = [
                    Line2D([0], [0], marker='o', color='black', label='Avg Score 0–59%', markerfacecolor='red', markersize=8),
                    Line2D([0], [0], marker='o', color='black', label='Avg Score 60–79%', markerfacecolor='orange', markersize=8),
                    Line2D([0], [0], marker='o', color='black', label='Avg Score 80–100%', markerfacecolor='green', markersize=8),
                ]
            else:
                dot_legend = []

            ax1.set_title(chart_title.strip() or "KPI Chart", pad=20)

            # Legends
            bar_handles, bar_labels = ax1.get_legend_handles_labels()
            if legend_style == "Separate (default)":
                ax1.legend(bar_handles, bar_labels, loc="upper left")
                if score_line_style == "Colored dots by score":
                    ax1.legend(handles=bar_handles + dot_legend, loc="upper right")
                elif score_line_style == "Black line":
                    ax2.legend(["Average Score (%)"], loc="upper right")
                fig.subplots_adjust(top=0.85)
            else:
                all_handles = bar_handles + dot_legend
                all_labels = bar_labels + [h.get_label() for h in dot_legend]
                ax1.legend(all_handles, all_labels, loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=4, frameon=False)
                fig.subplots_adjust(bottom=0.4)

            st.pyplot(fig)

            # Download button
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
