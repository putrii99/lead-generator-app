import streamlit as st
import pandas as pd
import requests
import re
from serpapi import GoogleSearch
import time

# Konfigurasi API SerpAPI
API_KEY = "ab22ffc76aacbae08873ae17748f44b37d6b497d226a76fbfc7b3bc719d3ac4c"

#fungsi pencarian leads
def search_leads(query, location="Indonesia", num_results=10):
    params = {
        "engine": "google",
        "q": query,
        "location": location,
        "num": num_results,
        "api_key": API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    leads = []

    for result in results.get("organic_results", []):
        leads.append({
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet"),
            "domain": result.get("displayed_link")
        })

    return pd.DataFrame(leads)

# Fungsi ekstraksi email dari website
def extract_email_from_website(url):
    try:
        response = requests.get(url, timeout=5)
        html = response.text
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)
        if emails:
            return emails[0]
        return "Not found"
    except Exception as e:
        return f"Error: {str(e)}"

# Konfigurasi halaman
st.set_page_config(page_title="Lead Finder 🔎", layout="wide")
st.title("🔎 Lead Generator - Email Scraper")
st.markdown("Cari lead + ambil email dari hasil pencarian Google.")

# Animasi / header
st.markdown("""
    <h1 style='text-align: center; color: #4B8BBE;'>🔎 Lead Finder - Email Scraper</h1>
    <p style='text-align: center;'>Cari dan ekstrak email dari hasil pencarian Google menggunakan SerpAPI.</p>
    <hr>
""", unsafe_allow_html=True)

# Form input
with st.form("lead_form"):
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        query = st.text_input("🔍 Kata kunci pencarian", "marketing agency jakarta") #copy emoji dari web emojipedia.org
    with col2:
        location = st.text_input("📍 Lokasi", "Indonesia")
    with col3:
        num_results = st.slider("📄 Jumlah hasil", 5, 20, 10)
    
    submitted = st.form_submit_button("Mulai Scrape 🚀")

# Eksekusi
if submitted:
    with st.spinner("Sedang mencari dan mengekstrak email..."):
        df = search_leads(query, location, num_results)
        df["email"] = df["link"].apply(extract_email_from_website)
        st.session_state["scraped_data"] = df

    # Filter valid email
    df_filtered = df[
        df["email"].notnull() &
        ~df["email"].str.contains("Not found|Error|core-js|\\.js|\\.css", case=False, na=False)
    ]
#Tampilkan data jika sudah tersedia
if "scraped_data" in st.session_state:
    df = st.session_state["scraped_data"]
    
    # Sidebar filter
    st.sidebar.header("🔍 Filter Hasil")
    filter_option = st.sidebar.radio("Tampilkan:", ["Semua", "Hanya yang punya email", "Tanpa email"])

    if filter_option == "Hanya yang punya email":
        df_filtered = df[df["email"].str.contains("@", na=False)]
    elif filter_option == "Tanpa email":
        df_filtered = df[~df["email"].str.contains("@", na=False)]
    else:
        df_filtered = df

    # Tampilkan hasil
    st.subheader("📋 Hasil Pencarian:")
    st.dataframe(df_filtered, use_container_width=True)

    # Unduh hasil
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "filtered_leads.csv", "text/csv")

    st.success(f"Total lead yang ditampilkan: {len(df_filtered)}")

    # Footer
    st.markdown("""
        <hr>
        <p style='text-align: center; font-size: 0.9em;'>Build with ❤️ by Putri & ChatGPT</p>
    """, unsafe_allow_html=True)
