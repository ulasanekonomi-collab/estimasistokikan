import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimasi Stok Ikan via Satelit", layout="wide")
st.title("🛰️ Uji Coba Estimasi Stok Ikan Berbasis Data Satelit")
st.write("Simulasi integrasi data oseanografi (Suhu & Klorofil) untuk memprediksi fluktuasi biomassa.")

# --- 1. GENERATOR DATA SATELIT (SIMULASI) ---
# Kita buat data fluktuasi bulanan selama 1 tahun
np.random.seed(42)
bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des']
x = np.arange(12)

# Simulasi Suhu Permukaan Laut (SPL) - rata-rata 28-30 derajat Celcius (khas perairan tropis)
spl_data = 29 + np.sin(x/6 * np.pi) * 1.5 + np.random.normal(0, 0.3, 12)

# Simulasi Klorofil-a (mg/m3) - Meningkat saat ada upwelling (misal di bulan Juli-Agustus)
klorofil_data = 0.5 - np.cos(x/6 * np.pi) * 0.4 + np.random.normal(0, 0.1, 12)
klorofil_data = np.clip(klorofil_data, 0.1, 2.0) # Pastikan tidak ada nilai negatif

# Gabungkan ke DataFrame
df_satelit = pd.DataFrame({
    'Bulan': bulan,
    'Suhu_Laut_C': spl_data,
    'Klorofil_a': klorofil_data
})

# --- 2. PANEL INTERAKTIF ---
st.sidebar.header("Parameter Model Estimasi")
st.sidebar.write("Sesuaikan sensitivitas ikan terhadap lingkungan:")
suhu_optimal = st.sidebar.slider("Suhu Optimal Ikan (°C)", 27.0, 31.0, 28.5, step=0.1)
bobot_klorofil = st.sidebar.slider("Faktor Pengali Klorofil (α)", 1000, 5000, 3000, step=500)
penalti_suhu = st.sidebar.slider("Faktor Penalti Suhu (β)", 100, 1000, 500, step=100)

# --- 3. MODEL ESTIMASI STOK ---
# Rumus: Stok Dasar + (Klorofil * Bobot) - (Selisih Suhu dari Optimal * Penalti)
stok_dasar = 2000 
df_satelit['Estimasi_Stok'] = stok_dasar + (df_satelit['Klorofil_a'] * bobot_klorofil) - (np.abs(df_satelit['Suhu_Laut_C'] - suhu_optimal) * penalti_suhu)
df_satelit['Estimasi_Stok'] = np.clip(df_satelit['Estimasi_Stok'], 0, None) # Mencegah stok minus

# --- 4. VISUALISASI ---
st.subheader("Data Satelit vs Estimasi Stok Ikan")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Grafik Kondisi Oseanografi (Dari Satelit)**")
    fig_env, ax1 = plt.subplots(figsize=(6, 4))
    
    color = 'tab:red'
    ax1.set_xlabel('Bulan')
    ax1.set_ylabel('Suhu Laut (°C)', color=color)
    ax1.plot(df_satelit['Bulan'], df_satelit['Suhu_Laut_C'], color=color, marker='o', label="Suhu")
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  
    color = 'tab:green'
    ax2.set_ylabel('Klorofil-a (mg/m³)', color=color)  
    ax2.plot(df_satelit['Bulan'], df_satelit['Klorofil_a'], color=color, marker='s', linestyle='--', label="Klorofil")
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig_env.tight_layout()
    st.pyplot(fig_env)

with col2:
    st.markdown("**Grafik Prediksi Biomassa / Stok Ikan**")
    fig_stock, ax3 = plt.subplots(figsize=(6, 4))
    ax3.bar(df_satelit['Bulan'], df_satelit['Estimasi_Stok'], color='#1a5f7a', alpha=0.8)
    ax3.plot(df_satelit['Bulan'], df_satelit['Estimasi_Stok'], color='orange', marker='o', linewidth=2)
    ax3.set_ylabel("Estimasi Stok (Biomassa)")
    ax3.set_title("Fluktuasi Stok Berdasarkan Lingkungan")
    st.pyplot(fig_stock)

# Tampilkan Tabel
with st.expander("Lihat Detail Data Mentah"):
    st.dataframe(df_satelit.style.format({
        'Suhu_Laut_C': '{:.2f}',
        'Klorofil_a': '{:.2f}',
        'Estimasi_Stok': '{:.0f}'
    }))
