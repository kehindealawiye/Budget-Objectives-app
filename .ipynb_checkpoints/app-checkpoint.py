import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(layout="wide")
st.title("📊 Manual KPI Chart Generator")

# Chart title input
chart_title = st.text_input("Enter chart title:", value="Modern Infrastructure KPI Performance")

# Legend style toggle
legend_style = st.radio(
    "Legend Style:",
    ["Separate (default)", "Unified (bottom combined legend)"]
)

# Data input
st.markdown("### Paste your data below for each column (one item per line):")

kpi_text = st.text_area("KPI")
avg_score_text = st.text_area("Average Score (%)")
green_text = st.text_area("Number of Projects in the Green legend")
amber_text = st.text_area("Number of Projects in the Amber legend")
red_text = st.text_area("Number of Projects in the Red legend")

if st.button("Generate Chart"):
    try:
        # Parse inputs
        kpis = [x.strip() for x in kpi_text.strip().split('\n') if x.strip()]
        avg_scores = [float(x.strip().replace('%', '')) for x in avg_score_text.strip().split('\n') if x.strip()]
        greens = [int(x.strip()) for x in green_text.strip().split('\n') if x.strip()]
        ambers = [int(x.strip()) for x in amber_text.strip().split('\n') if x.strip()]
        reds = [int(x.strip()) for x in red_text.strip().split('\n') if x.strip()]

        # Validate lengths
        if not all(len(lst) == len(kpis) for lst in [avg_scores, greens, ambers, reds]):
            st.error("All columns must have the same number of entries.")
        else:
            # Create DataFrame
            df = pd.DataFrame({
                "KPI": kpis,
                "Average Score": avg_scores,
                "Green": greens,
                "Amber": ambers,
                "Red": reds
            })
            df["Total"] = df["Green"] + df["Amber"] + df["Red"]

            # Plot
            fig, ax1 = plt.subplots(figsize=(14, 7))
            ax1.bar(df["KPI"], df["Green"], label="Green", color="green")
            ax1.bar(df["KPI"], df["Amber"], bottom=df["Green"], label="Amber", color="orange")
            ax1.bar(df["KPI"], df["Red"], bottom=df["Green"] + df["Amber"], label="Red", color="red")
            ax1.set_ylabel("Count of Status")
            ax1.tick_params(axis='x', rotation=90)

            ax2 = ax1.twinx()
            line = ax2.plot(df["KPI"], df["Average Score"], color="black", marker="o", label="Average Score (%)")
            ax2.set_ylabel("Average Score (%)")
            ax2.set_ylim(0, 100)

            # Title
            ax1.set_title(chart_title.strip() or "KPI Chart")

            # Legend logic
            if legend_style == "Separate (default)":
                ax1.legend(loc="upper left")
                ax2.legend(loc="upper right")
            else:
                bars_legend, bars_labels = ax1.get_legend_handles_labels()
                line_legend, line_labels = ax2.get_legend_handles_labels()
                ax1.legend(
                    bars_legend + line_legend,
                    bars_labels + line_labels,
                    loc="upper center",
                    bbox_to_anchor=(0.5, -0.15),
                    ncol=4
                )

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
