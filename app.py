"""
Portofolio Data Analyst - Angga Herviona Ikhwanudin
Artikel data storytelling: penjualan DQLab Store Juli-Desember 2019
Jalankan lokal:  streamlit run app.py
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Belanja Akhir Tahun DQLab Store",
    page_icon="🛒",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "data" / "retail_raw_reduced.csv"
BULAN = {
    "2019-07": "Jul", "2019-08": "Agu", "2019-09": "Sep",
    "2019-10": "Okt", "2019-11": "Nov", "2019-12": "Des",
}
FOKUS = "DKI Jakarta"


def rp_miliar(x: float) -> str:
    return f"Rp{x / 1e9:,.2f} miliar".replace(",", "X").replace(".", ",").replace("X", ".")


def angka(x: int) -> str:
    return f"{x:,}".replace(",", ".")


def persen(x: float, desimal: int = 1) -> str:
    return f"{x * 100:.{desimal}f}%".replace(".", ",")


@st.cache_data
def muat_data():
    mentah = pd.read_csv(DATA_PATH)
    jumlah_duplikat = int(mentah.duplicated().sum())
    df = mentah.drop_duplicates().copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["bulan"] = df["order_month"].map(BULAN)
    df["kuartal"] = df["order_month"].apply(lambda m: "Q3" if m < "2019-10" else "Q4")
    df["gmv"] = df["item_price"] * df["quantity"]
    return mentah, df, jumlah_duplikat


mentah, df, jumlah_duplikat = muat_data()
urutan_bulan = list(BULAN.values())

# ---------------------------------------------------------------- SIDEBAR
with st.sidebar:
    mode_warna = st.selectbox(
        "Mode warna grafik",
        ["Semua Provinsi", f"Sorot {FOKUS}"],
    )

    st.info(
        "**Dataset**\n\n"
        "Data transaksi DQLab Store yang digunakan dalam artikel ini bersumber dari "
        "dataset pelatihan DQLab:\n\n"
        "1. [retail_raw_reduced.csv](https://dqlabcdn.xeratic.com/dqlab-dataset/retail_raw_reduced.csv)\n"
        "2. [DQLab Academy](https://academy.dqlab.id/)"
    )

    st.info(
        "**Catatan metodologi**\n\n"
        f"Dataset mentah berisi {angka(len(mentah))} baris transaksi. "
        f"Sebanyak {jumlah_duplikat} baris duplikat persis dihapus sebelum analisis, "
        f"sehingga tersisa {angka(len(df))} baris.\n\n"
        "**GMV** (Gross Merchandise Value) dihitung sebagai harga per unit × jumlah unit. "
        "Transaksi dengan jumlah unit sangat besar tetap dipertahankan karena diduga "
        "pembelian grosir, bukan salah input."
    )

    st.success(
        "**Angga Herviona Ikhwanudin**\n\n"
        "Pranata Laboratorium Pendidikan di Laboratorium Teknologi Rekayasa Pangan, "
        "Politeknik Negeri Jember, sekaligus mahasiswa magister yang meneliti sistem "
        "pengering pintar berbasis IoT dan machine learning. Terbiasa mengolah data sensor "
        "di laboratorium, Angga memperluas kemampuannya ke analisis data bisnis melalui "
        "pelatihan Python, SQL, dan visualisasi data di DQLab."
    )


def skala_warna(field: str = "province"):
    """Warna sesuai mode di sidebar."""
    if mode_warna == "Semua Provinsi":
        return alt.Color(f"{field}:N", title="Provinsi", scale=alt.Scale(scheme="tableau10"))
    return alt.condition(
        alt.datum[field] == FOKUS,
        alt.value("#1f77b4"),
        alt.value("#c7c7c7"),
    )


# ---------------------------------------------------------------- ANGKA KUNCI
bulanan = (
    df.groupby(["order_month", "bulan"])
    .agg(gmv=("gmv", "sum"), order=("order_id", "nunique"), customer=("customer_id", "nunique"))
    .reset_index()
)
bulanan["aov"] = bulanan["gmv"] / bulanan["order"]
gmv_jul = bulanan.loc[bulanan["bulan"] == "Jul", "gmv"].item()
gmv_sep = bulanan.loc[bulanan["bulan"] == "Sep", "gmv"].item()
gmv_okt = bulanan.loc[bulanan["bulan"] == "Okt", "gmv"].item()
gmv_des = bulanan.loc[bulanan["bulan"] == "Des", "gmv"].item()
total_gmv = df["gmv"].sum()
gmv_q3 = df.loc[df["kuartal"] == "Q3", "gmv"].sum()
gmv_q4 = df.loc[df["kuartal"] == "Q4", "gmv"].sum()

prov = df.pivot_table(index="province", columns="kuartal", values="gmv", aggfunc="sum").reset_index()
prov["pertumbuhan"] = prov["Q4"] / prov["Q3"] - 1
prov["total"] = prov["Q3"] + prov["Q4"]
prov["porsi"] = prov["total"] / total_gmv
prov = prov.sort_values("total", ascending=False)
porsi_dki = prov.loc[prov["province"] == FOKUS, "porsi"].item()
tumbuh_terbesar = prov.sort_values("pertumbuhan", ascending=False).iloc[0]

order_per_cust = df.groupby("customer_id")["order_id"].nunique()
porsi_sekali = (order_per_cust == 1).mean()

# ---------------------------------------------------------------- ARTIKEL
st.title("Belanja Akhir Tahun: Ke Mana Larinya Uang Pelanggan DQLab Store?")
st.markdown("Penulis : **Angga Herviona Ikhwanudin**")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total GMV Jul-Des 2019", rp_miliar(total_gmv))
k2.metric("Jumlah order", angka(df["order_id"].nunique()))
k3.metric("Customer unik", angka(df["customer_id"].nunique()))
k4.metric("Pertumbuhan Q4 vs Q3", f"+{persen(gmv_q4 / gmv_q3 - 1)}")

st.write(
    "Bagi sebuah toko online, akhir tahun bukan sekadar pergantian kalender. Ada musim promo, "
    "gajian akhir tahun, dan libur panjang yang mendorong orang berbelanja lebih banyak. "
    "Pertanyaannya: apakah lonjakan belanja itu benar-benar terjadi, dari mana datangnya, "
    "dan apakah pelanggan yang datang di musim ramai akan kembali lagi?"
)
st.write(
    "Artikel ini menelusuri 5.000 baris transaksi DQLab Store selama Juli-Desember 2019 untuk "
    "menjawab tiga hal: kapan penjualan naik, wilayah mana yang paling berkontribusi, dan "
    "seperti apa perilaku pelanggannya."
)

# --- Bagian 1
st.header("Lonjakan yang Dimulai Bulan Oktober")
st.subheader("Gambar 1. GMV Bulanan DQLab Store Juli-Desember 2019")

garis = (
    alt.Chart(bulanan)
    .transform_calculate(gmv_m="datum.gmv / 1e9")
    .mark_line(point=True, strokeWidth=3)
    .encode(
        x=alt.X("bulan:N", sort=urutan_bulan, title="Bulan (2019)", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("gmv_m:Q", title="GMV (Rp miliar)"),
        tooltip=[
            alt.Tooltip("bulan:N", title="Bulan"),
            alt.Tooltip("gmv:Q", title="GMV (Rp)", format=",.0f"),
            alt.Tooltip("order:Q", title="Jumlah order"),
        ],
    )
    .properties(height=360)
)
st.altair_chart(garis, width="stretch")

st.write(
    f"GMV bergerak datar di kuartal ketiga, sekitar Rp3,5-4,5 miliar per bulan. Lalu terjadi "
    f"lompatan di Oktober: dari {rp_miliar(gmv_sep)} di September menjadi {rp_miliar(gmv_okt)}, "
    f"naik {persen(gmv_okt / gmv_sep - 1, 0)} dalam sebulan. Puncaknya terjadi di Desember dengan "
    f"{rp_miliar(gmv_des)}, atau {str(round(gmv_des / gmv_jul, 1)).replace('.', ',')} kali GMV Juli."
)
st.write(
    "Asumsi utama di balik lonjakan ini adalah musim promo akhir tahun seperti 10.10, 11.11, dan "
    "12.12. Dataset ini hanya mencakup satu semester, sehingga asumsi tersebut belum bisa diuji "
    "dengan membandingkan periode yang sama di tahun sebelumnya."
)

# --- Bagian 2
st.header("Jakarta Masih Jadi Pusat, Tapi Bukan yang Tumbuh Paling Cepat")
st.subheader("Gambar 2. GMV Bulanan per Provinsi")

per_prov_bulan = df.groupby(["order_month", "bulan", "province"])["gmv"].sum().reset_index()
garis_prov = (
    alt.Chart(per_prov_bulan)
    .transform_calculate(gmv_m="datum.gmv / 1e9")
    .mark_line(point=True)
    .encode(
        x=alt.X("bulan:N", sort=urutan_bulan, title="Bulan (2019)", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("gmv_m:Q", title="GMV (Rp miliar)"),
        color=skala_warna(),
        detail="province:N",
        tooltip=[
            alt.Tooltip("province:N", title="Provinsi"),
            alt.Tooltip("bulan:N", title="Bulan"),
            alt.Tooltip("gmv:Q", title="GMV (Rp)", format=",.0f"),
        ],
    )
    .properties(height=380)
)
st.altair_chart(garis_prov, width="stretch")

st.subheader("Gambar 3. GMV per Provinsi pada Bulan Tertentu")
bulan_pilih = st.select_slider("Pilih bulan", options=urutan_bulan, value="Des")
satu_bulan = per_prov_bulan[per_prov_bulan["bulan"] == bulan_pilih]
batang = (
    alt.Chart(satu_bulan)
    .transform_calculate(gmv_m="datum.gmv / 1e9")
    .mark_bar()
    .encode(
        x=alt.X("gmv_m:Q", title="GMV (Rp miliar)"),
        y=alt.Y("province:N", sort="-x", title="Provinsi"),
        color=skala_warna(),
        tooltip=[
            alt.Tooltip("province:N", title="Provinsi"),
            alt.Tooltip("gmv:Q", title="GMV (Rp)", format=",.0f"),
        ],
    )
    .properties(height=300)
)
st.altair_chart(batang, width="stretch")

st.write(
    f"{FOKUS} menyumbang {persen(porsi_dki)} dari seluruh GMV, jauh di atas provinsi lain. "
    "Di setiap bulan, posisinya tidak pernah tergeser dari urutan pertama. Jawa Barat menyusul "
    "di urutan kedua, lalu Jawa Tengah dan Yogyakarta."
)
st.write(
    "Namun, ukuran besar tidak selalu berarti tumbuh paling cepat. Gambar 4 membandingkan "
    "pertumbuhan GMV dari kuartal ketiga ke kuartal keempat di setiap provinsi."
)

st.subheader("Gambar 4. Pertumbuhan GMV Q4 dibanding Q3 per Provinsi")
batang_tumbuh = (
    alt.Chart(prov)
    .mark_bar()
    .encode(
        x=alt.X("pertumbuhan:Q", title="Pertumbuhan GMV Q4 vs Q3", axis=alt.Axis(format="%")),
        y=alt.Y("province:N", sort="-x", title="Provinsi"),
        color=skala_warna(),
        tooltip=[
            alt.Tooltip("province:N", title="Provinsi"),
            alt.Tooltip("Q3:Q", title="GMV Q3 (Rp)", format=",.0f"),
            alt.Tooltip("Q4:Q", title="GMV Q4 (Rp)", format=",.0f"),
            alt.Tooltip("pertumbuhan:Q", title="Pertumbuhan", format=".1%"),
        ],
    )
    .properties(height=300)
)
st.altair_chart(batang_tumbuh, width="stretch")

st.write(
    f"{tumbuh_terbesar['province']} justru mencatat pertumbuhan tertinggi, yaitu "
    f"{persen(tumbuh_terbesar['pertumbuhan'], 0)}. GMV-nya lebih dari dua kali lipat di kuartal "
    f"keempat. Jawa Barat juga tumbuh hampir dua kali lipat. Sementara itu {FOKUS} tumbuh "
    f"{persen(prov.loc[prov['province'] == FOKUS, 'pertumbuhan'].item(), 0)}, masih kuat, "
    "tetapi di bawah rata-rata."
)
st.write(
    "Artinya, ruang pertumbuhan berikutnya ada di luar Jakarta. Jawa Barat, dengan basis GMV "
    "terbesar kedua dan pertumbuhan yang tinggi, layak menjadi prioritas ekspansi."
)

# --- Bagian 3
st.header("Banyak yang Datang, Sedikit yang Kembali")
st.subheader("Gambar 5. Jumlah Customer Berdasarkan Banyaknya Order")

dist = order_per_cust.clip(upper=6).value_counts().sort_index().reset_index()
dist.columns = ["jumlah_order", "customer"]
dist["label"] = dist["jumlah_order"].astype(str).replace({"6": "6+"})
batang_dist = (
    alt.Chart(dist)
    .mark_bar(color="#1f77b4")
    .encode(
        x=alt.X("label:N", sort=None, title="Jumlah order per customer (Jul-Des 2019)", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("customer:Q", title="Jumlah customer"),
        tooltip=[
            alt.Tooltip("label:N", title="Jumlah order"),
            alt.Tooltip("customer:Q", title="Jumlah customer"),
        ],
    )
    .properties(height=320)
)
st.altair_chart(batang_dist, width="stretch")

st.write(
    f"Dari {angka(order_per_cust.size)} customer, {persen(porsi_sekali, 0)} hanya bertransaksi satu kali "
    "dalam enam bulan. Hanya sebagian kecil yang menjadi pelanggan setia dengan lima order atau lebih."
)

st.subheader("Gambar 6. Customer Unik dan Rata-rata Nilai Order per Bulan")
dasar = alt.Chart(bulanan).encode(x=alt.X("bulan:N", sort=urutan_bulan, title="Bulan (2019)", axis=alt.Axis(labelAngle=0)))
cust_bar = dasar.mark_bar(color="#9ecae1").encode(
    y=alt.Y("customer:Q", title="Customer unik"),
    tooltip=[alt.Tooltip("bulan:N", title="Bulan"), alt.Tooltip("customer:Q", title="Customer unik")],
)
aov_line = dasar.transform_calculate(aov_jt="datum.aov / 1e6").mark_line(point=True, color="#d62728", strokeWidth=3).encode(
    y=alt.Y("aov_jt:Q", title="Rata-rata nilai order (Rp juta)"),
    tooltip=[alt.Tooltip("bulan:N", title="Bulan"), alt.Tooltip("aov:Q", title="Rata-rata nilai order (Rp)", format=",.0f")],
)
st.altair_chart(
    alt.layer(cust_bar, aov_line).resolve_scale(y="independent").properties(height=340),
    width="stretch",
)

cust_jul = bulanan.loc[bulanan["bulan"] == "Jul", "customer"].item()
cust_des = bulanan.loc[bulanan["bulan"] == "Des", "customer"].item()
st.write(
    f"Lonjakan GMV di akhir tahun lebih banyak didorong oleh bertambahnya jumlah pembeli "
    f"(dari {cust_jul} customer di Juli menjadi {cust_des} di Desember), bukan oleh nilai belanja "
    "per order. Rata-rata nilai order justru sedikit turun di November dan Desember, pola yang "
    "wajar ketika promo menarik banyak pembeli dengan keranjang lebih kecil."
)
st.write(
    "Tantangannya: jika sebagian besar pembeli musim promo tidak kembali, lonjakan ini hanya "
    "bersifat sementara. Program retensi seperti voucher pembelian kedua atau membership bisa "
    "mengubah pembeli musiman menjadi pelanggan tetap."
)

# --- Bagian 4
st.header("Bukan yang Termurah, Tapi yang Paling Pas")
st.subheader("Gambar 7. Kontribusi per Rentang Harga")

df["rentang_harga"] = pd.cut(
    df["item_price"],
    [0, 250_000, 500_000, 1_000_000, 2_000_000, float("inf")],
    labels=["< 250 rb", "250-500 rb", "500 rb-1 jt", "1-2 jt", "> 2 jt"],
)
harga = df.groupby("rentang_harga", observed=True).agg(unit=("quantity", "sum"), gmv=("gmv", "sum")).reset_index()
harga["Porsi unit terjual"] = harga["unit"] / harga["unit"].sum()
harga["Porsi GMV"] = harga["gmv"] / harga["gmv"].sum()
harga_long = harga.melt(
    id_vars="rentang_harga", value_vars=["Porsi unit terjual", "Porsi GMV"],
    var_name="ukuran", value_name="porsi",
)
batang_harga = (
    alt.Chart(harga_long)
    .mark_bar()
    .encode(
        x=alt.X("rentang_harga:N", sort=None, title="Rentang harga per unit", axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("ukuran:N", sort=["Porsi unit terjual", "Porsi GMV"]),
        y=alt.Y("porsi:Q", title="Porsi", axis=alt.Axis(format="%")),
        color=alt.Color("ukuran:N", title="Ukuran", scale=alt.Scale(domain=["Porsi unit terjual", "Porsi GMV"], range=["#9ecae1", "#1f77b4"])),
        tooltip=[
            alt.Tooltip("rentang_harga:N", title="Rentang harga"),
            alt.Tooltip("ukuran:N", title="Ukuran"),
            alt.Tooltip("porsi:Q", title="Porsi", format=".1%"),
        ],
    )
    .properties(height=340)
)
st.altair_chart(batang_harga, width="stretch")

porsi_murah = harga.loc[harga["rentang_harga"] == "< 250 rb", "Porsi unit terjual"].item()
gmv_murah = harga.loc[harga["rentang_harga"] == "< 250 rb", "Porsi GMV"].item()
gmv_tengah = harga.loc[harga["rentang_harga"] == "500 rb-1 jt", "Porsi GMV"].item()
st.write(
    f"Produk di bawah Rp250 ribu laku paling banyak secara unit ({persen(porsi_murah, 0)} unit terjual), "
    f"tetapi hanya menyumbang {persen(gmv_murah, 0)} GMV. Sumber pendapatan terbesar justru produk "
    f"kelas menengah Rp500 ribu-1 juta, yang menyumbang {persen(gmv_tengah, 0)} GMV."
)
st.write(
    "Bagi tim merchandising, ini berarti promo diskon besar-besaran pada produk murah tidak banyak "
    "menggerakkan pendapatan. Menjaga stok dan visibilitas produk kelas menengah lebih berdampak."
)

# --- Penutup interaktif
st.header("Jelajahi Sendiri")
st.subheader("Gambar 8. GMV Bulanan per Brand")

brand_total = df.groupby("brand")["gmv"].sum().sort_values(ascending=False)
brand_pilih = st.multiselect(
    "Brand yang dipilih:",
    options=list(brand_total.index),
    default=list(brand_total.index[:3]),
)
prov_pilih = st.multiselect(
    "Provinsi:",
    options=list(prov["province"]),
    default=list(prov["province"]),
)
saring = df[df["brand"].isin(brand_pilih) & df["province"].isin(prov_pilih)]
if saring.empty:
    st.warning("Pilih minimal satu brand dan satu provinsi.")
else:
    per_brand = saring.groupby(["order_month", "bulan", "brand"])["gmv"].sum().reset_index()
    st.altair_chart(
        alt.Chart(per_brand)
        .transform_calculate(gmv_m="datum.gmv / 1e9")
        .mark_line(point=True)
        .encode(
            x=alt.X("bulan:N", sort=urutan_bulan, title="Bulan (2019)", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("gmv_m:Q", title="GMV (Rp miliar)"),
            color=alt.Color("brand:N", title="Brand"),
            tooltip=[
                alt.Tooltip("brand:N", title="Brand"),
                alt.Tooltip("bulan:N", title="Bulan"),
                alt.Tooltip("gmv:Q", title="GMV (Rp)", format=",.0f"),
            ],
        )
        .properties(height=360),
        width="stretch",
    )

st.header("Kesimpulan")
st.markdown(
    f"""
1. **Akhir tahun adalah musim panen.** GMV Q4 naik {persen(gmv_q4 / gmv_q3 - 1, 0)} dibanding Q3, dengan puncak di Desember.
2. **Jakarta dominan, Jawa Timur dan Jawa Barat tumbuh paling cepat.** Ekspansi berikutnya sebaiknya diarahkan ke luar Jakarta.
3. **Pelanggan belum loyal.** {persen(porsi_sekali, 0)} customer hanya belanja sekali; retensi adalah pekerjaan rumah terbesar.
4. **Produk kelas menengah adalah mesin pendapatan.** Rentang Rp500 ribu-1 juta menyumbang porsi GMV terbesar.

Analisis ini terbatas pada data enam bulan. Data minimal dua tahun diperlukan untuk memastikan
bahwa lonjakan akhir tahun benar-benar pola musiman.
"""
)
