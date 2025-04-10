import streamlit as st
import pandas as pd
import requests
import re
from serpapi import GoogleSearch
from email.utils import parseaddr

#konfigurasi awal halaman
st.set_page_config(page_title="Lead Generator", layout="wide")

#API SerpAPI
API_KEY = "ab22ffc76aacbae08873ae17748f44b37d6b497d226a76fbfc7b3bc719d3ac4c"

#pilihan bahasa
lang = st.sidebar.selectbox("🌐 Language / Bahasa", ["English", "Bahasa Indonesia"])

#dictionary terjemahan UI
translations = {
    "title": {
        "English": "💼 Lead Generator - Email Scraper",
        "Bahasa Indonesia": "💼 Lead Generator - Pencari Email"
    },
    "description": {
        "English": "Search for leads + extract emails from Google search results.",
        "Bahasa Indonesia": "Cari prospek + ekstrak email dari hasil pencarian Google."
    },
    "search_query": {
        "English": "🔍 Search Query",
        "Bahasa Indonesia": "🔍 Kata Kunci"
    },
    "location": {
        "English": "🌍 Location",
        "Bahasa Indonesia": "🌍 Lokasi"
    },
    "num_results": {
        "English": "🔢 Number of Results",
        "Bahasa Indonesia": "🔢 Jumlah Hasil"
    },
    "filter_option": {
        "English": "📎 Show leads:",
        "Bahasa Indonesia": "📎 Tampilkan lead:"
    },
    "all": {
        "English": "All",
        "Bahasa Indonesia": "Semua"
    },
    "with_email": {
        "English": "Only with valid email",
        "Bahasa Indonesia": "Hanya yang punya email valid"
    },
    "without_email": {
        "English": "Without valid email",
        "Bahasa Indonesia": "Tanpa email valid"
    },
    "start_button": {
        "English": "🚀 Start Scraping",
        "Bahasa Indonesia": "🚀 Mulai Scrape"
    },
    "loading": {
        "English": "🔄 Scraping and validating emails...",
        "Bahasa Indonesia": "🔄 Sedang mencari dan memvalidasi email..."
    },
    "results_found": {
        "English": "✅ Found {count} leads based on filter.",
        "Bahasa Indonesia": "✅ Ditemukan {count} lead berdasarkan filter."
    },
    "download": {
        "English": "⬇️ Download CSV",
        "Bahasa Indonesia": "⬇️ Unduh CSV"
    },
    "email": {
        "English": "✉️ Email:",
        "Bahasa Indonesia": "✉️ Email:"
    },
    "footer": {
        "English": "Built with ❤️ by Putri",
        "Bahasa Indonesia": "Dibuat dengan ❤️ oleh Putri"
    },
    "warning_query": {
        "English": "❗ Please enter a search query first.",
        "Bahasa Indonesia": "❗ Masukkan kata kunci terlebih dahulu."
    }
}

#fungsi ambil teks sesuai bahasa
def t(key):
    return translations.get(key, {}).get(lang, key)

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

#---------- UI ----------
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
st.markdown(f"<div class='title-style'>{t('title')}</div>", unsafe_allow_html=True)
st.markdown(f"<p class='desc-style'>{t('description')}</p>", unsafe_allow_html=True)

# Sidebar
query = st.sidebar.text_input(t("search_query"))
location = st.sidebar.text_input(t("location"), "Indonesia")
num_results = st.sidebar.slider(t("num_results"), 5, 100, 10)
filter_option = st.sidebar.radio(t("filter_option"), [t("all"), t("with_email"), t("without_email")])

#tombol utama
if st.sidebar.button(t("start_button")):
    if not query:
        st.warning(t("warning_query"))
    else:
        with st.spinner(t("loading")):
            df = search_leads(query, location, num_results, mode)
            df["email"] = df["link"].apply(extract_email_from_website)
            df["valid_email"] = df["email"].apply(is_valid_email)

            # Filter
            if filter_option == t("with_email"):
                df = df[df["valid_email"] == True]
            elif filter_option == t("without_email"):
                df = df[df["valid_email"] == False]

            st.success(t("results_found").format(count=len(df)))

            #tampilkan hasil
            for i, row in df.iterrows():
                with st.container():
                    st.markdown(f"### 🔗 [{row['title']}]({row['link']})")
                    st.write(row["snippet"])
                    st.markdown(f"🌐 `{row['domain']}`")
                    email_status = f"<span class='email-valid'>{row['email']}</span>" if "@" in row['email'] else f"<span class='email-invalid'>{row['email']}</span>"
                    st.markdown(f"{t('email')} {email_status}", unsafe_allow_html=True)
                    st.markdown("---")

        #tombol download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(t("download"), csv, "filtered_leads.csv", "text/csv")

        #footer
    st.markdown("""
        <hr>
        <p style='text-align: center; font-size: 0.9em;'>Build with ❤️ by Putri</p>
    """, unsafe_allow_html=True)

    ##semua emoji copy dari web emojipedia.org
