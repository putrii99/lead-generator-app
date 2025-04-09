import streamlit as st
import pandas as pd
import requests
import re
from serpapi import GoogleSearch
from email.utils import parseaddr

#konfigurasi awal halaman
st.set_page_config(page_title="Lead Generator", layout="wide")

#API SerpAPI
API_KEY = st.secrets["api_key"]

#fungsi pencarian leads
def search_leads(query, location="Indonesia", num_results=10, mode="Global"):
    if mode == "Lokal":
        google_domain = "google.co.id"
        hl = "id"
        gl = "id"
    
    else:
        google_domain = "google.com"
        hl = "en"
        gl = "us"

    params = {
        "engine": "google",
        "q": query,
        "location": location,
        "num": num_results,
        "api_key": API_KEY,
        "google_domain": google_domain,
        "hl": hl,
        "gl": gl,
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

#fungsi ekstraksi email dari website
def extract_email_from_website(url):
    try:
        response = requests.get(url, timeout=5)
        html = response.text
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)
        for email in emails:
            if is_valid_email(email):
                return email
        return "Not found"
    except Exception as e:
        return "Error"

#fungsi validasi email sederhana
def is_valid_email(email):
    name, addr = parseaddr(email)
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

# ---------- UI ----------
st.markdown("""
    <style>
        .title-style {
            font-size: 40px;
            font-weight: 700;
            color: #4A90E2;
        }
        .desc-style {
            font-size: 18px;
            color: gray;
        }
        .email-valid {
            background-color: #D4EDDA;
            color: #155724;
            border-radius: 5px;
            padding: 3px 8px;
            font-size: 14px;
        }
        .email-invalid {
            background-color: #F8D7DA;
            color: #721C24;
            border-radius: 5px;
            padding: 3px 8px;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

#sidebar input
mode = st.radio("🌍 Mode Bahasa", ["Global", "Lokal"], horizontal=True)
st.markdown("<div class='title-style'>💼Lead Generator - Email Scraper</div>", unsafe_allow_html=True)
st.markdown("<p class='desc-style'>Search for leads + extract emails from Google search results.</p>", unsafe_allow_html=True)
st.sidebar.header("🎯 Parameter Pencarian")
query = st.sidebar.text_input("🔍Kata kunci")
location = st.sidebar.text_input("🌍 Lokasi", "Indonesia")
num_results = st.sidebar.slider("🔢 Jumlah hasil", 5, 5000, 10)

#contoh kategoru bisnis
    #"Marketing Agency Jakarta",
    #"Tech Company Bandung",
    #"HR Consultant Indonesia",
    #"Plastic Supplier Indonesia",
    #"Klinik Kecantikan Yogyakarta",
    #"Restoran Vegan Jakarta",
    #"Kursus Online Python"

#sidebar filter
filter_option = st.sidebar.radio(
    "📎 Tampilkan lead:",
    ["Semua", "Hanya yang punya email valid", "Tanpa email valid"]
)

#tombol utama
if st.sidebar.button("🚀Mulai Scrape"):
    with st.spinner("🔄 Sedang mencari dan memvalidasi email..."):
        df = search_leads(query, location, num_results, mode)
        df["email"] = df["link"].apply(extract_email_from_website)
        df["valid_email"] = df["email"].apply(is_valid_email)
        
        #terapkan filter
        if filter_option == "Hanya yang punya email valid":
            df= df[df["valid_email"] == True]
        elif filter_option == "Tanpa email valid":
            df = df[df["valid_email"] == False]
        
        st.success(f"✅Ditemukan {len(df)} lead berdasarkan filter.")
        #st.dataframe(df, use_container_width=True)

        for i, row in df.iterrows():
            with st.container():
                st.markdown(f"### 🔗 [{row['title']}]({row['link']})")
                st.write(row["snippet"])
                st.markdown(f"🌐 `{row['domain']}`")
                email_status = f"<span class='email-valid'>{row['email']}</span>" if "@" in row['email'] else f"<span class='email-invalid'>{row['email']}</span>"
                st.markdown(f"✉️ Email: {email_status}", unsafe_allow_html=True)
                st.markdown("---")

        #tombol download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download CSV", csv, "filtered_leads.csv", "text/csv")

        #footer
    st.markdown("""
        <hr>
        <p style='text-align: center; font-size: 0.9em;'>Build with ❤️ by Putri</p>
    """, unsafe_allow_html=True)

    ##semua emoji copy dari web emojipedia.org
