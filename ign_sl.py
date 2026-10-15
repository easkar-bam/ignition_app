#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
from ign_code import ignition

# --------------------------------------------------
# Seiteneinstellungen
# --------------------------------------------------

st.set_page_config(
    page_title="Ignition Analysis Tool",
    layout="wide"
)

st.title("🔥 Ignition Analysis Tool")

# --------------------------------------------------
# Session State
# --------------------------------------------------

if "ign" not in st.session_state:
    st.session_state.ign = None

if "slope_results" not in st.session_state:
    st.session_state.slope_results = None

if "plot_settings" not in st.session_state:
    st.session_state.plot_settings = None

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("CSV Import")

uploaded_file = st.sidebar.file_uploader(
    "CSV-Datei auswählen",
    type=["csv", "txt"]
)

separator = st.sidebar.text_input(
    "Separator (sep)",
    value=";"
)

decimal = st.sidebar.text_input(
    "Decimal Separator",
    value=","
)

header = st.sidebar.number_input(
    "Header Row",
    value=7,
    min_value=0
)

encoding = st.sidebar.selectbox(
    "Encoding",
    [
        "utf-8",
        "utf-8-sig",
        "latin1",
        "cp1252"
    ],
    index=0
)

if uploaded_file is not None:

    st.sidebar.markdown("---")

    if st.sidebar.button("Datei laden", use_container_width=True):

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".csv"
            ) as tmp:

                tmp.write(uploaded_file.getbuffer())
                filepath = tmp.name

            st.session_state.ign = ignition(
                datafile=filepath,
                sp=separator,
                dc=decimal,
                hd=int(header),
                ec=encoding
            )

            st.sidebar.success("Datei geladen")

        except Exception as e:
            st.sidebar.error(str(e))

# --------------------------------------------------
# Hauptbereich
# --------------------------------------------------

if st.session_state.ign is None:

    st.info(
        "Bitte links eine Datei auswählen und laden."
    )

else:

    ign = st.session_state.ign

    # --------------------------------------------------
    # Data Preview
    # --------------------------------------------------

    st.subheader("Datenvorschau")

    st.dataframe(
        ign.df.head(20),
        use_container_width=True
    )

    st.write(
        f"**Zeilen:** {len(ign.df)} | "
        f"**Spalten:** {len(ign.df.columns)}"
    )

    # --------------------------------------------------
    # Tabs
    # --------------------------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "Zeit hinzufügen",
            "Plot",
            "Steigungsanalyse"
        ]
    )

    # ==================================================
    # TAB 1
    # ==================================================

    with tab1:

        st.subheader("Zeitspalte erzeugen")

        fq = st.number_input(
            "Abtastfrequenz",
            value=1.0,
            min_value=0.0001
        )

        unit = st.selectbox(
            "Zeiteinheit",
            ["s", "ms", "min", "h", "d"]
        )

        if st.button("Zeit hinzufügen"):

            ign.addtime(
                fq=fq,
                unit=unit
            )

            st.success("Zeitspalte hinzugefügt")

            st.dataframe(
                ign.df.head(),
                use_container_width=True
            )

    # ==================================================
    # TAB 2
    # ==================================================

    with tab2:

        st.subheader("Daten plotten")

        columns = ign.df.columns.tolist()

        col1, col2 = st.columns(2)

        with col1:

            x_col_name = st.selectbox(
                "X-Achse",
                columns,
                index=0
            )

        with col2:

            y_col_name = st.selectbox(
                "Y-Achse",
                columns,
                index=min(1, len(columns)-1)
            )

        x_idx = ign.df.columns.get_loc(x_col_name)
        y_idx = ign.df.columns.get_loc(y_col_name)

        show_max = st.checkbox(
            "dp/dt-Maximum markieren",
            value=False
        )

        if st.button("Plot erstellen"):

            st.session_state.plot_settings = {
                "x_idx": x_idx,
                "y_idx": y_idx,
                "x_name": x_col_name,
                "y_name": y_col_name
            }

        if st.session_state.plot_settings is not None:

            settings = st.session_state.plot_settings

            fig, ax = plt.subplots(
                figsize=(10, 5)
            )

            ax.plot(
                ign.df.iloc[:, settings["x_idx"]],
                ign.df.iloc[:, settings["y_idx"]]
            )

            ax.set_xlabel(settings["x_name"])
            ax.set_ylabel(settings["y_name"])

            ax.grid(True)

            if (
                st.session_state.slope_results is not None
                and show_max
            ):

                target_x = st.session_state.slope_results["target_x"]

                idx = (
                    ign.df.iloc[:, settings["x_idx"]] - target_x
                ).abs().idxmin()

                ax.plot(
                    ign.df.iloc[idx, settings["x_idx"]],
                    ign.df.iloc[idx, settings["y_idx"]],
                    "ro",
                    markersize=8
                )

            st.pyplot(fig)


    # ==================================================
    # TAB 3
    # ==================================================

    with tab3:

        st.subheader("Savitzky-Golay Analyse")

        col1, col2, col3 = st.columns(3)

        with col1:

            na = st.number_input(
                "Min Window",
                value=10
            )

        with col2:

            ne = st.number_input(
                "Max Window",
                value=100
            )

        with col3:

            target = st.number_input(
                "Target Window",
                value=21
            )

        # ---------------------------------
        # Spaltenauswahl hinzufügen
        # ----------------------------------

        columns = ign.df.columns.tolist()

        x_col = st.selectbox(
            "Zeitspalte",
            columns,
            index=0,
            key="slope_x"
        )

        y_col = st.selectbox(
            "Signalspalte",
            columns,
            index=min(1, len(columns)-1),
            key="slope_y"
        )

        x_idx = ign.df.columns.get_loc(x_col)
        y_idx = ign.df.columns.get_loc(y_col)

        if st.button("Steigungen berechnen"):

            try:

                results_df, target_dpdt, target_x = ign.calcslopes(
                    na=int(na),
                    ne=int(ne),
                    xcol=x_idx,
                    ycol=y_idx,
                    target=int(target)
                )

                st.session_state.slope_results = {
                    "results_df": results_df,
                    "target_dpdt": target_dpdt,
                    "target_x": target_x,
                    "target": target
                }

            except Exception as e:

                st.error(str(e))

        if st.session_state.slope_results is not None:

            results_df = st.session_state.slope_results["results_df"]
            target_dpdt = st.session_state.slope_results["target_dpdt"]
            target_x = st.session_state.slope_results["target_x"]
            target = st.session_state.slope_results["target"]

            st.success("Analyse abgeschlossen")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "(dp/dt)max",
                    f"{target_dpdt:.2f}"
                )

            with col2:
                st.metric(
                    "Zeitpunkt",
                    f"{target_x:.4f}"
                )

            fig, ax = plt.subplots(figsize=(10, 5))

            ax.plot(
                results_df["window"],
                results_df["max_slope"],
                linewidth=2
            )

            ax.axvline(
                target,
                color="red",
                linestyle="--",
                label=f"Window = {target}"
            )

            ax.set_xlabel("Window Length")
            ax.set_ylabel("(dp/dt)max")
            ax.grid(True)
            ax.legend()

            st.pyplot(fig)

            st.subheader("Ergebnisse")

            st.dataframe(
                results_df,
                use_container_width=True
            )


# In[ ]:




