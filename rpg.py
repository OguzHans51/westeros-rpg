import streamlit as st
from openai import OpenAI
import time
import random
import json

# ==========================================
# AYARLAR
# ==========================================
try:
    DEFAULT_DEEPSEEK_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    DEFAULT_DEEPSEEK_KEY = ""

st.set_page_config(page_title="Westeros RPG", page_icon="🛡️", layout="wide")

# --- DEEPSEEK BAĞLANTISI ---
try:
    client = OpenAI(
        api_key=DEFAULT_DEEPSEEK_KEY, 
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    st.error(f"Anahtar Hatası: {e}. Lütfen Streamlit Secrets ayarını kontrol et.")
    st.stop()

# --- HAFIZA ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dead_list" not in st.session_state:
    st.session_state.dead_list = []

# ==========================================
# EKRAN 1: KARAKTER VE ZAMAN YARATMA
# ==========================================
if not st.session_state.game_started:
    st.title("🛡️ Westeros RPG: Taktiksel Savaş")
    st.caption("Dönem Seçimi | Detaylı Statlar | Kayıt Sistemi")

    # --- BAŞLANGIÇTA YÜKLEME ---
    st.markdown("---")
    st.markdown("### 📂 Kayıtlı Oyunun Var mı?")
    uploaded_file_start = st.file_uploader("Varsa .json dosyanı buraya bırak", type=["json"], key="start_loader")
    
    if uploaded_file_start is not None:
        if st.button("Oyunu Yükle ve Başlat", type="primary"):
            try:
                loaded_data = json.load(uploaded_file_start)
                st.session_state.char_info = loaded_data["char_info"]
                st.session_state.messages = loaded_data["messages"]
                st.session_state.dead_list = loaded_data.get("dead_list", [])
                st.session_state.game_started = True
                st.success("Oyun bulundu! Başlatılıyor...")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error("Dosya bozuk veya hatalı.")
    # --------------------------------------------------

    with st.expander("📚 OYUN REHBERİ (Tıkla)", expanded=False):
        st.markdown("""
        ### 🎭️ Karakter Yaratma
        * **Karakter Adı:** Karakteriniz adı ve lakabı. *(Örneğin Ulf Kancaburun)*
        * **Sınıfı:** Rütbesi veya Mesleği. *(Örneğin Kral Muhafızı veya Tüccar)*
        * **Hanesi:** Bulunduğu hane bölgesi ve hanedeki konumu. *(Örneğin House Lannister(Soylu) veya House Mooton(Köylü))*
        * **Canon Karakter:** Eğer gerçek bir karakterseniz bu kutucuğu işaretleyin. *(İsim ve hane kitapla tutsun)*
        * **İstatistikler:** Karakterinizin yapacağı hamlelere avantaj veya dezavantaj sağlar.

        ### ⌛️ Zaman Ayarlama
        * **Açıklama:** Oynamak istediğiniz zaman aralığı için geçmiş hikayesinde zamanı ekstra belirtin. *(AC 299 dolu dolu bir yıl mesela tam olarak hangi olay öncesi net lazım)*
        * **Geçmiş Hikayesi:** Karakterinizin kısa hikayesi. Ayrıca hikayenin başlamasını istediğiniz spesifik bir durumla ilgili bilgi. *(Örneğin,Trident Savaşındaydım)*

        ### 🎮 Hamle Türleri *(Hikaye İçi)*
        * **⚔️ Eylem:** Saldırı, tırmanma, kaçma, kovalama vb. *(Ortalama: Fizik + Çeviklik)*
        * **👁️ Gözlem:** Etrafı inceleme, tuzakları fark etme, insanları değerlendirme vb. *(Bonus: Algı)*
        * **💬 İkna:** Yalan söyleme, pazarlık, korkutma, aşk itirafı :P vb. *(Ortalama: Zeka + Karizma)*
        * **🗣️ Diyalog:** Sadece sohbet etme. Hikaye ilerlemez, zaman akmaz.
        """)

    st.markdown("---")
    st.markdown("### 🆕 Yeni Karakter Yarat")
    
    col1, col2 = st.columns(2)
    with col1:
        char_name = st.text_input("Karakter Adı", placeholder="Örn: Daemon Targaryen")
        char_house = st.text_input("Hanesi", placeholder="Targaryen")
        
        st.subheader("⏳ Zaman Ayarı")
        era_select = st.selectbox("Hangi Dönem?", [
            "Game of Thrones (Ana Seri - 298 AC)",
            "Robert'ın İsyanı (282 AC)",
            "Blackfyre İsyanı (196 AC)",
            "Ejderhaların Dansı (129 AC)",
            "Aegon'un Fethi (2 BC)",
            "Diğer / Özel Tarih"
        ])
        custom_year = st.text_input("Tam Yıl (İsteğe Bağlı)", placeholder="Örn: 300 AC")
        
    with col2:
        char_class = st.text_input("Sınıfı", placeholder="Ejderha Süvarisi")
        gender = st.radio("Cinsiyet", ["Erkek", "Kadın"], horizontal=True)
        is_canon = st.checkbox("Canon Karakter (Kitap/Dizi)")

    st.markdown("---")
    st.subheader("📊 Karakter İstatistikleri (1-10 Arası)")
    
    # YENİ STAT SİSTEMİ
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        stat_fizik = st.slider("💪 Fizik (Güç)", 1, 10, 5)
        stat_ceviklik = st.slider("🏃 Çeviklik (Hız)", 1, 10, 5)
    with s_col2:
        stat_zeka = st.slider("🧠 Zeka (Bilgi)", 1, 10, 5)
        stat_algi = st.slider("👁️ Algı (Dikkat)", 1, 10, 5)
    with s_col3:
        stat_karizma = st.slider("👑 Karizma (Liderlik)", 1, 10, 5)

    char_bg = st.text_area("Geçmiş Hikayesi", placeholder="Karakterin kimdir? Amacı nedir?")
    
    if st.button("TARİHİ BAŞLAT ⚔️", use_container_width=True):
        if not char_name:
            st.warning("İsim girmeden tarih yazılamaz!")
        else:
            final_time = f"{era_select}"
            if custom_year:
                final_time += f" (Yıl: {custom_year})"

            st.session_state.char_info = {
                "name": char_name, "house": char_house, 
                "class": char_class, "gender": gender,
                # YENİ STATLAR KAYDEDİLİYOR
                "fizik": stat_fizik, "ceviklik": stat_ceviklik,
                "zeka": stat_zeka, "algi": stat_algi,
                "karizma": stat_karizma,
                "era": final_time,
                "is_canon": is_canon
            }
            
            canon_note = "Bu bir CANON karakterdir, o tarihteki durumuna sadık kal." if is_canon else "Bu orijinal bir karakterdir."

            system_prompt = f"""
            Sen Westeros'ta acımasız ve tarihine sadık bir GM'sin.
            
            OYUN BİLGİLERİ:
            - DÖNEM/YIL: {final_time}
            - OYUNCU: {char_name} ({gender}, {char_house}, {char_class})
            - STATLAR: Fizik {stat_fizik}, Çeviklik {stat_ceviklik}, Zeka {stat_zeka}, Algı {stat_algi}, Karizma {stat_karizma}
            - DURUM: {canon_note}
            - GEÇMİŞ: {char_bg}
            
            KURALLAR:
            1. **DİL:** Kusursuz Türkçe kullan.
            2. **HİTAP:** Oyuncunun cinsiyetine ({gender}) uygun hitap et.
            3. **TARİHSEL TUTARLILIK:** Seçilen yılda kim kral ise ondan bahset.
            4. **ZAR SİSTEMİ:** Oyuncu bir eylem yaptığında sana [TOPLAM SKOR: X] bilgisini verecek.
               - Düşük skor (10 altı): Başarısızlık.
               - Yüksek skor (16+): Başarı.
               - Eğer oyuncu "Diyalog" modundaysa zar atılmaz, sadece sohbet et.
            5. Giriş sahnesini seçilen yıla uygun olarak yaz ve "Ne yapıyorsun?" diye bitir.
            """
            
            st.session_state.messages.append({"role": "system", "content": system_prompt})
            
            with st.spinner("Hikayen başlıyor..."):
                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=st.session_state.messages,
                        stream=False
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
                    st.session_state.game_started = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Hata: {e}")

# ==========================================
# EKRAN 2: OYUN ALANI
# ==========================================
else:
    info = st.session_state.char_info
    # Eski save dosyaları bozulmasın diye default değerler (get metodu ile)
    s_fizik = info.get('fizik', 5)
    s_ceviklik = info.get('ceviklik', 5)
    s_zeka = info.get('zeka', 5)
    s_algi = info.get('algi', 5)
    s_karizma = info.get('karizma', 5)

    gender_icon = "♂️" if info.get('gender') == "Erkek" else "♀️"
    
    st.title(f"🛡️ {info['name']} {gender_icon}")
    # Statları gösterge panelinde göster
    st.caption(f"📅 {info.get('era')} | 💪 {s_fizik} | 🏃 {s_ceviklik} | 🧠 {s_zeka} | 👁️ {s_algi} | 👑 {s_karizma}")
    
    # --- YENİ SIDEBAR (KAYDET & YÜKLE & YENİ OYUN) ---
    with st.sidebar:
        st.header("💾 Oyun Menüsü")
        
        # --- 1. KAYDETME KISMI ---
        current_dead = st.session_state.get("dead_list", [])
        save_data = {
            "char_info": st.session_state.char_info,
            "messages": st.session_state.messages,
            "dead_list": current_dead
        }
        json_data = json.dumps(save_data)
        
        st.download_button(
            label="📥 Oyunu Kaydet (İndir)",
            data=json_data,
            file_name=f"{info['name']}_save.json",
            mime="application/json"
        )

        st.markdown("---")
        
        # --- 2. ÖLÜM DEFTERİ KISMI ---
        st.subheader("💀 Ölüm Defteri")
        dead_input = st.text_input("Ölen Karakter/Yaratık:", placeholder="Örn: Caraxes")
        if st.button("Öldü İşaretle"):
            if "dead_list" not in st.session_state:
                st.session_state.dead_list = []
            if dead_input and dead_input not in st.session_state.dead_list:
                st.session_state.dead_list.append(dead_input)
                st.success(f"{dead_input} eklendi.")
        
        if "dead_list" in st.session_state and st.session_state.dead_list:
            st.markdown("Rehmetliler:")
            for dead in st.session_state.dead_list:
                st.caption(f"⚰️ {dead}")
            
            if st.button("Listeyi Temizle"):
                st.session_state.dead_list = []
                st.rerun()

        st.markdown("---")

        # --- 3. YÜKLEME KISMI ---
        st.subheader("📂 Oyun Yükle")
        uploaded_file = st.file_uploader("Dosyayı Seç", type=["json"], key="sidebar_loader")
        if uploaded_file is not None:
            if st.button("🔄 OYUNU YÜKLE", type="primary"):
                try:
                    loaded_data = json.load(uploaded_file)
                    st.session_state.char_info = loaded_data["char_info"]
                    st.session_state.messages = loaded_data["messages"]
                    st.session_state.dead_list = loaded_data.get("dead_list", [])
                    st.session_state.game_started = True
                    st.success("Başarıyla Yüklendi!")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Dosya hatası: {e}")

        st.markdown("---")
        if st.button("🗑️ Yeni Oyun (Sıfırla)", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- MESAJLAR ---
    for message in st.session_state.messages:
        if message["role"] == "system": continue
        
        avatar = "🐉" if message["role"] == "assistant" else "🗡️"
        
        # İçeriği alıyoruz
        raw_content = message["content"]
        
        # EĞER BU BİR OYUNCU MESAJIYSA VE İÇİNDE GİZLİ SİSTEM BİLGİSİ VARSA GİZLE
        if "[SİSTEM BİLGİSİ:" in raw_content:
            # Sadece [SİSTEM BİLGİSİ: yazan yere kadar olan kısmı al (yani senin yazdığın)
            display_content = raw_content.split("[SİSTEM BİLGİSİ:")[0].strip()
        else:
            display_content = raw_content
            
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(display_content)

    # --- INPUT VE BUTONLAR ---
    
    # Yeni Buton Sistemi (Yatay Seçim)
    st.markdown("---")
    action_mode = st.radio(
        "Hamle Modu:", 
        ["⚔️ Eylem (Fizik+Çeviklik)", "👁️ Gözlem (Algı)", "💬 İkna (Zeka+Karizma)", "🗣️ Diyalog (Sohbet)"],
        horizontal=True,
        label_visibility="collapsed" # Başlığı gizle, sadece butonlar görünsün
    )
    
    if prompt := st.chat_input("Hamleni yap..."):
        
        # STAT HESAPLAMALARI
        bonus = 0
        mode_text = ""
        hidden_instruction = ""
        dice_roll = random.randint(1, 20)
        
        if "Eylem" in action_mode:
            # Fizik ve Çeviklik Ortalaması
            bonus = (s_fizik + s_ceviklik) // 2
            mode_text = "[EYLEM]"
            
        elif "Gözlem" in action_mode:
            # Sadece Algı
            bonus = s_algi
            mode_text = "[GÖZLEM]"
            hidden_instruction = "Oyuncu çevreyi inceliyor. Gördüklerini, saklananları veya detayları anlat."
            
        elif "İkna" in action_mode:
            # Zeka ve Karizma Ortalaması
            bonus = (s_zeka + s_karizma) // 2
            mode_text = "[İKNA/SOSYAL]"
            
        elif "Diyalog" in action_mode:
            # Zar atılmaz, bonus yok.
            dice_roll = 0
            bonus = 0
            mode_text = "[SADECE DİYALOG]"
            hidden_instruction = "HİKAYEYİ İLERLETME. Sadece karşılıklı konuşma olsun. Zaman akmasın, sahne değişmesin."

        # Zar Sonucu (Diyalog değilse)
        total_score = dice_roll + bonus
        if "Diyalog" in action_mode:
            score_display = "Zar Yok (Sohbet)"
        else:
            score_display = total_score

        # Kritik Durumlar
        special_note = ""
        if dice_roll == 1 and "Diyalog" not in action_mode:
            special_note = " (KRİTİK HATA! ZAR 1 GELDİ. Felaket!)"
            total_score = 0
        elif dice_roll == 20 and "Diyalog" not in action_mode:
            special_note = " (KRİTİK BAŞARI! ZAR 20 GELDİ. Efsane!)"
            total_score = 30
            
        # Kullanıcıya Mesajı Göster
        st.chat_message("user", avatar="🗡️").markdown(f"**{mode_text}** {prompt}")
        
        # Zar Bilgisi (Expandable) - Diyalog ise gösterme
        if "Diyalog" not in action_mode:
            outcome_color = "blue"
            if total_score < 10: outcome_color = "red"
            elif total_score > 20: outcome_color = "green"
            
            with st.expander(f"🎲 Zar Sonucu: {total_score} (Tıkla)"):
                st.markdown(f"""
                * **Mod:** {action_mode}
                * **Saf Zar:** {dice_roll}
                * **Bonus:** +{bonus}
                * **SONUÇ:** :{outcome_color}[**{total_score}**]
                """)

        # Ölüleri metne çevir
        dead_str = ", ".join(st.session_state.dead_list) if st.session_state.dead_list else "Yok"

        # Yapay Zekaya Giden Gizli Mesaj
        full_msg = f"""{prompt}
        
        [SİSTEM BİLGİSİ:
        - OYUNCU: {info['name']}
        - HAMLE TÜRÜ: {mode_text}
        - SKOR: {total_score} (Zar {dice_roll} + Bonus {bonus}) {special_note}
        - EK TALİMAT: {hidden_instruction}
        - DÖNEM: {info.get('era')}
        - [DIKKAT] OLULER LISTESI (Bunlar kesinlikle oludur, geri gelemez): {dead_str}]"""
        
        st.session_state.messages.append({"role": "user", "content": full_msg})

        with st.spinner("GM düşünüyor..."):
            try:
                history = [st.session_state.messages[0]] + st.session_state.messages[-12:]
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=history,
                    stream=False
                )
                msg = response.choices[0].message.content
                st.chat_message("assistant", avatar="🐉").markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                st.error(f"Hata: {e}")

