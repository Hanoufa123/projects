import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import altair as alt
import io
from datetime import datetime, date
import os
import pytz
from dotenv import load_dotenv
load_dotenv()

# -------- Firebase إعداد --------
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("firebase-private-key"))
    firebase_admin.initialize_app(cred)

db = firestore.client()
collection_ref = db.collection("sentiments")

# -------- نموذج المشاعر --------
model_name = 'PRAli22/AraBert-Arabic-Sentiment-Analysis'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# -------- واجهة Streamlit --------
st.title("تحليل المشاعر + لوحة تحكم Firebase")
# إدخال النص
user_text = st.text_area(" اكتب النص هنا:")

riyadh_tz = pytz.timezone('Asia/Riyadh')

if st.button(" تحليل"):
    if user_text.strip():
        result = sentiment_pipeline(user_text)[0]
        print(result)
        label = result['label'].lower()
        if label == "positive":
            label = "إيجابي"
        elif label == "negative":
            label = "سلبي"
        elif label == "neutral":
            label = "محايد"
        score = round(result['score'] * 100, 2)

        st.success(f" النتيجة: **{label}** ({score}%)")

        # حفظ في Firestore
        doc = {
            "text": user_text,
            "label": label,
            "score": score,
            "timestamp": datetime.now(riyadh_tz)
        }
        collection_ref.add(doc)
        st.info("✅ تم حفظ النتيجة في Firebase")
    else:
        st.warning("⚠️ رجاءً اكتب نص أولاً")

st.divider()
# -------- Dashboard --------
st.header(" Dashboard")

# اختيار التاريخ
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(" اختر تاريخ البداية", value=date.today().replace(day=1))
with col2:
    end_date = st.date_input(" اختر تاريخ النهاية", value=date.today())

# فلتر بالكلمة المفتاحية
keyword = st.text_input(" فلترة بالنص (كلمة مفتاحية اختيارية):").strip().lower()

# جلب البيانات من Firebase
docs = collection_ref.stream()

data = []
for d in docs:
    doc_data = d.to_dict()
    ts = doc_data["timestamp"]

    # تحويل timestamp (Firestore) إلى datetime
    if isinstance(ts, datetime):
        ts_dt = ts
    # else:
    #     ts_dt = ts.to_pydatetime()

     # تحويل التوقيت إلى توقيت الرياض
    ts_dt = ts_dt.astimezone(riyadh_tz)
    # التصفية حسب التاريخ والكلمة
    if start_date <= ts_dt.date() <= end_date:
        text_lower = doc_data["text"].lower()
        if keyword == "" or keyword in text_lower:
            data.append({
                "text": doc_data["text"],
                "label": doc_data["label"],
                "score": doc_data["score"],
                "timestamp": ts_dt
            })

if not data:
    st.info("⚠️ لا توجد بيانات ضمن الفلاتر المحددة.")
else:
    df = pd.DataFrame(data)

    # جدول
    st.subheader(" السجل")
    st.dataframe(df[["timestamp", "text", "label", "score"]])

    # توزيع المشاعر
    st.subheader(" توزيع المشاعر")
    chart = alt.Chart(df).mark_bar().encode(
        x='label',
        y='count()',
        color='label'
    )
    st.altair_chart(chart, use_container_width=True)

    #  الاتجاه عبر الزمن
    st.subheader("📈 المشاعر عبر الزمن (Timeline)")
    df['date'] = df['timestamp'].dt.date
    timeline = df.groupby(['date', 'label']).size().reset_index(name='count')

    line_chart = alt.Chart(timeline).mark_line(point=True).encode(
        x='date:T',
        y='count:Q',
        color='label:N'
    ).properties(width=700, height=400)

    st.altair_chart(line_chart, use_container_width=True)

    # -------- تصدير --------
    st.subheader("⬇️ تصدير النتائج")
    csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    # towrite = io.BytesIO()
    # with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
    #     df.to_excel(writer, index=False, sheet_name="Sentiments")
    # towrite.seek(0)
    # xlsx = towrite.read()
    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            label=" تنزيل CSV",
            data=csv,
            file_name=f"sentiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    # with col_b:
    #     st.download_button(
    #         label=" تنزيل Excel",
    #         data=xlsx,
    #         file_name=f"sentiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
