import streamlit as st
from openai import OpenAI
import time
import random
import json

# ==========================================
# AYARLAR
# ==========================================
# Buraya API anahtarını yapıştır
try:
    DEFAULT_DEEPSEEK_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    DEFAULT_DEEPSEEK_KEY = ""

st.set_page_config(page_title="Westeros RPG (V24)", page_icon="🛡️", layout="wide")

# --- DEEPSEEK BAĞLANTISI ---
try:
    client = OpenAI(
        api_key=DEFAULT_DEEPSEEK_KEY, 
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    st.error(f"Anahtar Hatası: {e}. Lütfen kodu açıp API Key'i yapıştır.")
    st.stop()

# --- HAFIZA ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dead_list" not in st.session_state:
    st.session_state.dead_list = []    

# ==========================================
# EKRAN 1: KARAKTER YARATMA
# ==========================================
if not st.session_state.game_started:
    st.title("🛡️ Westeros RPG: Tam Sürüm")
    st.caption("Stat Sistemi | Cinsiyet | Canon Karakter | Acımasız Zar")

    st.markdown("---")
    st.markdown("### 📂 Kayıtlı Oyunun Var mı?")
    uploaded_file_start = st.file_uploader("Varsa .json dosyanı buraya bırak", type=["json"], key="start_loader")
    
    if uploaded_file_start is not None:
        if st.button("Oyunu Yükle ve Başlat", type="primary"):
            try:
                loaded_data = json.load(uploaded_file_start)
                # Verileri yükle
                st.session_state.char_info = loaded_data["char_info"]
                st.session_state.messages = loaded_data["messages"]
                st.session_state.dead_list = loaded_data.get("dead_list", []) # Ölüleri de al
                
                st.session_state.game_started = True
                st.success("Oyun bulundu! Başlatılıyor...")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error("Dosya bozuk veya hatalı.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        char_name = st.text_input("Karakter Adı", placeholder="Örn: Brienne of Tarth")
        char_house = st.text_input("Hanesi", placeholder="Tarth")
        st.markdown("---")
        st.subheader("⏳ Zaman Ayarı")
        era_select = st.selectbox("Hangi Dönem?", [
            "Game of Thrones (Ana Seri - 298 AC)",
            "Robert'ın İsyanı (282 AC)",
            "Ejderhaların Dansı (129 AC)",
            "Aegon'un Fethi (2 BC)",
            "Blackfyre İsyanı (196 AC)",
            "Diğer / Özel Tarih"
        ])
        custom_year = st.text_input("Tam Yıl (İsteğe Bağlı)", placeholder="Örn: 300 AC")

        st.markdown("---")
        st.subheader("⚔️ Savaş Bonusu")
        combat_stat = st.slider("Savaş Yeteneği", 0, 10, 5, key="stat_combat", help="0: Köylü, 5: Asker, 10: Arthur Dayne")
        
    with col2:
        char_class = st.text_input("Sınıfı", placeholder="Şövalye")
        # --- EKLENEN KISIMLAR ---
        gender = st.radio("Cinsiyet", ["Erkek", "Kadın"], horizontal=True)
        is_canon = st.checkbox("Canon Karakter (Kitap/Dizi)")
        
        st.markdown("---")
        st.subheader("🧠 Zeka Bonusu")
        intellect_stat = st.slider("Zeka/İkna Yeteneği", 0, 10, 2, key="stat_intellect", help="0: Normal Zeka, 5: Üstat, 10: Baelish")

    char_bg = st.text_area("Geçmiş", placeholder="Kısa özet...")
    
    if st.button("MACERAYA BAŞLA ⚔️", use_container_width=True):
        if not char_name or "BURAYA" in DEFAULT_DEEPSEEK_KEY:
            st.warning("Eksik bilgi veya API Key!")
        else:
            final_time = f"{era_select}"
            if custom_year:
                final_time += f" (Yıl: {custom_year})"
            st.session_state.char_info = {
                "name": char_name, "house": char_house,
                "class": char_class, "gender": gender,
                "combat": combat_stat, "intellect": intellect_stat,
                "is_canon": is_canon, 
                "era": final_time
            }
            
            canon_note = "Bu bir CANON karakterdir, tarihine sadık kal." if is_canon else "Bu orijinal bir karakterdir."

            system_prompt = f"""
            Sen Westeros'ta acımasız ve tarihine sadık bir GM'sin.
            
            DÖNEM/YIL: {final_time} (ÇOK ÖNEMLİ: Hikayeyi, kralları ve olayları bu yıla göre kur.)
            OYUNCU: {char_name} ({gender}, {char_house}, {char_class})
            YETENEKLER: Savaş +{combat_stat} | Zeka +{intellect_stat}
            DURUM: {canon_note}
            GEÇMİŞ: {char_bg}

            KURALLAR:
            1. **DİL:** Kusursuz Türkçe kullan.
            2. **HİTAP:** Oyuncunun cinsiyetine ({gender}) uygun hitap et (Lord/Lady, Ser/Dame, Prens/Prenses).
            3. **MATEMATİKSEL KARAR:** Sana [TOPLAM SKOR: X] gelecek.
               - Skor < 10: Başarısızlık.
               - Skor 10-15: Ortalama başarı.
               - Skor 16-24: Büyük başarı.
               - Skor 25+: Efsanevi başarı.
               - Hedefin gücüne göre bu skoru yorumla.
            4. **TARİHSEL TUTARLILIK:** Seçilen yılda kim kral ise ondan bahset. Örneğin Ejderhaların Dansı ise ejderhalar vardır, Robert'ın İsyanı ise ejderha yoktur.
            5. Lore terimlerini (Winterfell, King's Landing) İngilizce bırak.
            6. Giriş sahnesini seçilen yıla uygun olarak yaz ve "Ne yapacaksın?" diye bitir.
            """
            
            st.session_state.messages.append({"role": "system", "content": system_prompt})
            
            with st.spinner("Karakter yaratılıyor..."):
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
    # Başlıkta Cinsiyet İkonu
    gender_icon = "♂️" if info.get('gender') == "Erkek" else "♀️"
    st.title(f"🛡️ {info['name']} {gender_icon}")
    st.caption(f"📅 {info.get('era')} | Savaş: +{info['combat']} | Zeka: +{info['intellect']} | {info['house']}")
    
    # --- YENİ SIDEBAR (KAYDET & YÜKLE & YENİ OYUN) ---
    with st.sidebar:
        st.header("💾 Oyun Menüsü")
        
        # --- 1. KAYDETME KISMI ---
        # Önce mevcut ölü listesini garantiye alalım
        current_dead = st.session_state.get("dead_list", [])
        
        save_data = {
            "char_info": st.session_state.char_info,
            "messages": st.session_state.messages,
            "dead_list": current_dead  # Ölüleri de kaydediyoruz
        }
        json_data = json.dumps(save_data)
        
        st.download_button(
            label="📥 Oyunu Kaydet (İndir)",
            data=json_data,
            file_name=f"{info['name']}_save.json",
            mime="application/json",
            help="Bu dosyayı indirip sakla. Sonra yükleyerek devam edersin."
        )

        st.markdown("---")
        
        # --- 2. ÖLÜM DEFTERİ KISMI ---
        st.subheader("💀 Ölüm Defteri")
        dead_input = st.text_input("Ölen Karakter/Yaratık:", placeholder="Örn: Caraxes")
        if st.button("Öldü İşaretle"):
            # Listeyi ilk kez oluşturuyorsak hata vermesin
            if "dead_list" not in st.session_state:
                st.session_state.dead_list = []
                
            if dead_input and dead_input not in st.session_state.dead_list:
                st.session_state.dead_list.append(dead_input)
                st.success(f"{dead_input} eklendi.")
        
        # Listeyi Göster
        if "dead_list" in st.session_state and st.session_state.dead_list:
            st.markdown("Rehmetliler:")
            for dead in st.session_state.dead_list:
                st.caption(f"⚰️ {dead}")
            
            if st.button("Listeyi Temizle"):
                st.session_state.dead_list = []
                st.rerun()

        st.markdown("---")

        # --- 3. YÜKLEME KISMI (BUTONLU ÇÖZÜM) ---
        st.subheader("📂 Oyun Yükle")
        uploaded_file = st.file_uploader("Dosyayı Seç", type=["json"], key="sidebar_loader")
        
        # BURASI ÖNEMLİ: Dosya seçilince hemen yüklemiyoruz, buton bekliyoruz.
        if uploaded_file is not None:
            if st.button("🔄 OYUNU YÜKLE", type="primary"):
                try:
                    loaded_data = json.load(uploaded_file)
                    
                    # Hafızayı güncelle
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
        # YENİ OYUN BUTONU
        if st.button("🗑️ Yeni Oyun (Sıfırla)", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Mesajları Göster
    for message in st.session_state.messages:
        if message["role"] == "system": continue
        avatar = "🐉" if message["role"] == "assistant" else "🗡️"
        
        # Sistem notlarını temizle
        content = message["content"].split("[SİSTEM:")[0].strip()
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(content)

    # --- INPUT ---
    action_type = st.radio("Hamle Türü:", ["⚔️ Fiziksel Saldırı / Güç", "🧠 İkna / Zeka / Sinsilik"], horizontal=True, label_visibility="collapsed")
    
    if prompt := st.chat_input("Hamleni yap..."):
        dice_roll = random.randint(1, 20)
        
        # Stat Hesabı
        if "Fiziksel" in action_type:
            bonus = info['combat']
        else:
            bonus = info['intellect']
            
        total_score = dice_roll + bonus
        
        # Kritik Kontrolü
        special_note = ""
        if dice_roll == 1:
            special_note = " (KRİTİK HATA! ZAR 1 GELDİ. Bonus geçersiz, felaket olmalı.)"
            total_score = 0 
        elif dice_roll == 20:
            special_note = " (KRİTİK BAŞARI! ZAR 20 GELDİ. Bonus geçersiz, efsane olmalı.)"
            total_score = 30 
            
        st.chat_message("user", avatar="🗡️").markdown(prompt)
        
        # Renkli Skor
        outcome_color = "blue"
        if total_score < 10: outcome_color = "red"
        elif total_score > 20: outcome_color = "green"
        
        with st.expander(f"🎲 Zar Sonucu: {total_score} (Tıkla)"):
            st.markdown(f"""
            * **Saf Zar:** {dice_roll}
            * **Bonus:** +{bonus}
            * **SONUÇ:** :{outcome_color}[**{total_score}**]
            """)

        dead_str = ", ".join(st.session_state.dead_list) if st.session_state.dead_list else "Yok"

        full_msg = f"""{prompt}
        
        [SİSTEM:
        - OYUNCU: {info['name']}
        - TOPLAM SKOR: {total_score} (Zar {dice_roll} + Bonus {bonus}) {special_note}
        - Lütfen bu skoru hedefin gücüne göre değerlendir.
        - Dili Türkçe, terimleri İngilizce tut.]
        - [DIKKAT] OLULER LISTESI (Bunlar kesinlikle oludur, geri gelemez): {dead_str}]"""
        
        st.session_state.messages.append({"role": "user", "content": full_msg})

        with st.spinner("GM Hesaplıyor..."):
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






