import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load data
def load_portfolio():
    with open("portfolio.json", "r") as f:
        return json.load(f)

portfolio = load_portfolio()
total_nilai = sum(item["nilai"] for item in portfolio)

# Auto-refresh setiap 1 menit (60000 ms)
from streamlit_autorefresh import st_autorefresh

auto_refresh = st.sidebar.checkbox("🔁 Aktifkan Auto-refresh", value=True)

if auto_refresh:
    st_autorefresh(interval=60 * 1000, key="auto-refresh")

st.title("📊 Dashboard Portfolio Keuangan Gana")
st.metric("Total Nilai Portfolio", f"Rp {total_nilai:,.0f}")

st.subheader("📄 Rincian Aset")

# Buat DataFrame & sort
df_tabel = pd.DataFrame(portfolio)
df_tabel = df_tabel.sort_values(by="nilai", ascending=False)

# Format nilai
df_tabel["nilai_format"] = df_tabel["nilai"].apply(lambda x: f"Rp {x:,.0f}")

# Tambahkan nomor urut setelah sorting
df_tabel.insert(0, "No", range(1, len(df_tabel) + 1))

# Tampilkan tabel
st.dataframe(
    df_tabel[["No", "nama", "jenis", "bucket", "nilai_format"]].rename(columns={
        "nama": "Nama Aset",
        "jenis": "Jenis",
        "bucket": "Bucket",
        "nilai_format": "Nilai"
    }),
    use_container_width=True,
    hide_index=True
)

# ======= Tambahkan bagian visualisasi di sini =======

df = df_tabel.copy() 

def format_rupiah_singkat(nominal):
    if nominal >= 1_000_000_000:
        return f"{nominal/1_000_000_000:.1f} M"
    elif nominal >= 1_000_000:
        return f"{nominal/1_000_000:.1f} jt"
    elif nominal >= 1_000:
        return f"{nominal/1_000:.1f} rb"
    else:
        return f"{nominal}"
    
st.subheader("📊 Visualisasi per Bucket (Interaktif)")

warna_bucket = {
    "Dana Darurat": "#003f5c",   # Biru Tua
    "Investasi": "#ffa600",      # Oranye
    "Cash": "#7fcdbb",           # Biru Muda
    "Dream Saving": "#8c6bb1",   # Ungu
    "Lainnya": "#2ca02c"         # Hijau
}

bucket_data = df.groupby("bucket")["nilai"].sum().reset_index()
bucket_data["label"] = bucket_data["nilai"].apply(format_rupiah_singkat)

fig_bucket = px.pie(
    bucket_data,
    names="bucket",
    values="nilai",
    hover_data=["label"],
    title="Distribusi Aset Berdasarkan Bucket",
    hole=0.4,
    color="bucket",
    color_discrete_map=warna_bucket
)

fig_bucket.update_traces(
    textinfo="label+percent",
    hovertemplate='%{label} (%{percent})<br>Total: Rp %{value:,}<extra></extra>'
)

st.plotly_chart(fig_bucket, use_container_width=True)


st.subheader("📊 Visualisasi per Jenis (Interaktif)")

jenis_data = df.groupby("jenis")["nilai"].sum().reset_index()
jenis_data["label"] = jenis_data["nilai"].apply(format_rupiah_singkat)

fig_jenis = px.pie(
    jenis_data,
    names="jenis",
    values="nilai",
    hover_data=["label"],
    title="Distribusi Aset Berdasarkan Jenis",
    hole=0.4
)

fig_jenis.update_traces(textinfo="label+percent", hovertemplate='%{label} (%{percent})<br>Total: Rp %{value:,}')

st.plotly_chart(fig_jenis, use_container_width=True)


# ======= Tambahkan sidebar kelola aset=======

# Form tambah aset

st.sidebar.header("📝 Tambah Aset Baru")

with st.sidebar.form("form_tambah_aset"):
    nama = st.text_input("Nama Aset")
    jenis = st.selectbox("Jenis Aset", ["Saham Indo", "Saham US", "Reksa Dana", "Tabungan", "Kripto", "Obligasi", "Deposito", "Tabungan Berjangka", "Emas", "Lainnya"])
    bucket = st.selectbox("Bucket", ["Dana Darurat", "Investasi", "Cash", "Dream Saving", "Lainnya"])
    nilai = st.number_input("Nilai (Rp)", min_value=0, step=100000)

    submit = st.form_submit_button("Tambah")

    if submit:
        if nama.strip() == "":
            st.sidebar.error("❌ Nama aset tidak boleh kosong!")
        else:
            # Tambahkan data baru ke list
            portfolio.append({
                "nama": nama,
                "jenis": jenis,
                "bucket": bucket,
                "nilai": nilai
            })

            # Simpan kembali ke file JSON
            with open("portfolio.json", "w") as f:
                json.dump(portfolio, f, indent=4)

            st.sidebar.success("✅ Aset berhasil ditambahkan!")
            st.experimental_rerun()


# Form hapus aset

st.sidebar.header("🛠️ Edit / Hapus Aset")

# Buat list pilihan aset
pilihan_aset = [f"{i+1}. {item['nama']} - Rp {item['nilai']:,.0f}" for i, item in enumerate(portfolio)]
index_terpilih = st.sidebar.selectbox("Pilih Aset", options=range(len(portfolio)), format_func=lambda x: pilihan_aset[x])

# Tampilkan detail aset terpilih
item = portfolio[index_terpilih]

st.sidebar.write(f"**Nama:** {item['nama']}")
st.sidebar.write(f"**Jenis:** {item['jenis']}")
st.sidebar.write(f"**Bucket:** {item['bucket']}")
st.sidebar.write(f"**Nilai:** Rp {item['nilai']:,.0f}")

# Form edit aset
with st.sidebar.form("form_edit"):
    nilai_baru = st.number_input("Ubah Nilai (Rp)", min_value=0, value=item["nilai"], step=100000)
    jenis_baru = st.selectbox("Ubah Jenis", ["Saham Indo", "Saham US", "Reksa Dana", "Tabungan", "Kripto", "Obligasi","Deposito","Tabungan Berjangka","Emas","Lainnya"], index=["Saham Indo", "Saham US", "Reksa Dana", "Tabungan", "Kripto", "Obligasi","Deposito","Tabungan Berjangka","Emas","Lainnya"].index(item["jenis"]))
    bucket_baru = st.selectbox("Ubah Bucket", ["Dana Darurat", "Investasi", "Cash","Dream Saving", "Lainnya"], index=["Dana Darurat", "Investasi", "Cash","Dream Saving", "Lainnya"].index(item["bucket"]))
    submit_edit = st.form_submit_button("💾 Simpan Perubahan")

    if submit_edit:
        item["nilai"] = nilai_baru
        item["jenis"] = jenis_baru
        item["bucket"] = bucket_baru
        with open("portfolio.json", "w") as f:
            json.dump(portfolio, f, indent=4)
        st.sidebar.success("✅ Data berhasil diupdate!")
        st.experimental_rerun()

# Tombol hapus
if st.sidebar.button("🗑️ Hapus Aset Ini"):
    del portfolio[index_terpilih]
    with open("portfolio.json", "w") as f:
        json.dump(portfolio, f, indent=4)
    st.sidebar.warning("⚠️ Aset telah dihapus!")
    st.experimental_rerun()
