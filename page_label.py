import streamlit as st
from sqlalchemy import create_engine, text 
import pandas as pd 
import os

DB_URL = "postgresql+pg8000://postgres:abraham@localhost:5432/postgres"
engine = create_engine(DB_URL) 

def anomaly_labeling():
    with engine.connect() as conn:
        query = text("""
            SELECT path_gambar
            FROM production_anomaly
            WHERE created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jakarta'
                BETWEEN DATE_TRUNC('week', NOW() AT TIME ZONE 'Asia/Jakarta') + INTERVAL '1 day'
                    AND DATE_TRUNC('week', NOW() AT TIME ZONE 'Asia/Jakarta') + INTERVAL '7 days'
            ORDER BY created_at;
        """)
        
        result = conn.execute(query).fetchall()
    df = pd.DataFrame(result, columns=["path_gambar"]) 
    df = df.drop_duplicates()
    col1, col2 = st.columns([2,1])

    with col2: 
        nama_gambar_list = df['path_gambar'].apply(lambda x: os.path.basename(x).replace('.jpg', ''))
        gambar_pilihan = st.radio("Pilih gambar", nama_gambar_list)
        
    with col1: 
        gambar_path = df[df['path_gambar'].str.contains(gambar_pilihan)].iloc[0]['path_gambar']
        st.image(gambar_path) 
    with engine.connect() as conn :
        query = text("""
                        SELECT x0, y0, x1, y1, defect_name
                        FROM production_anomaly
                        JOIN class_defect USING (class_id) 
                        WHERE path_gambar = :path_gambar
                    """)
        result = conn.execute(query, {"path_gambar": gambar_path}).fetchall()
    result = pd.DataFrame(result)
    # Header
    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5])
    col1.write("**x0**")
    col2.write("**y0**")
    col3.write("**x1**")
    col4.write("**y1**")
    col5.write("**Defect**")
    col6.write("**Edit**")
    col7.write("**Save**") 
    for idx, row in result.iterrows(): 
        
        col1.write(row["x0"])
        col2.write(row["y0"])
        col3.write(row["x1"])
        col4.write(row["y1"])
        col5.write(row["defect_name"])
        col6.button("Edit", key=f"edit_{idx}")
        col7.button("Save", key=f"save_{idx}")


def defect_labeling():
    st.subheader("Defect Labeling")

def main():
    st.header('Labeling Page')
    menu_option = st.sidebar.selectbox("Labeling", ("Anomaly", "Defect"))
    if menu_option == "Anomaly":
        anomaly_labeling()
    elif menu_option == "Defect":
        defect_labeling()

if __name__ == "__main__":
    main()
