import base64
import io
import json
import os
import pandas as pd
import requests
import streamlit as st
from PIL import Image

# إعداد الصفحة وتصميم واجهة احترافي
st.set_page_config(
    page_title="VoltEstimate AI - محلل المخططات المجاني",
    page_icon="⚡",
    layout="centered",
)

st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; }
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #0f172a; text-align: center; }
    .metric-card { background: white; padding: 15px; border-radius: 14px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; text-align: center; margin-bottom: 12px; }
    .stButton>button { width: 100%; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; font-weight: 600; padding: 0.75rem 1rem; border-radius: 12px; border: none; }
    [data-testid="stSidebar"] { background-color: #0f172a; color: white; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] .stMarkdown { color: #f1f5f9 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1>⚡ VoltEstimate AI (مجاني)</h1>", unsafe_allow_html=True)
st.markdown(
    "<p"
    " style='text-align: center; color: #64748b; font-size: 1rem;'>حصر كميات"
    " المخططات الكهربائية باستخدام الذكاء الاصطناعي المجاني</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# الشريط الجانبي للإعدادات والأسعار
st.sidebar.markdown("### ⚙️ إعدادات النظام المجاني")
st.sidebar.markdown(
    "احصل على مفتاح مجاني من [Groq"
    " Console](https://console.groq.com/keys) بدون أي رسوم."
)
api_key = st.sidebar.text_input(
    "أدخل مفتاح Groq API Key المجاني", type="password", placeholder="gsk_..."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ أسعار الوحدات (دج)")
default_prices = {
    "Single Switch (مفتاح مفرد)": 450,
    "Double Switch (مفتاح مزدوج)": 650,
    "Socket 16A (بريزة قوة)": 500,
    "LED Light Point (نقطة إضاءة)": 300,
    "Distribution Board - DB (لوحة توزيع)": 12000,
}

prices = {}
for item, default_price in default_prices.items():
  prices[item] = st.sidebar.number_input(item, value=default_price, step=50)

# رفع المخطط
st.markdown("### 📂 ارفع المخطط الكهربائي")
uploaded_file = st.file_uploader(
    "صورة المخطط (PNG, JPG)",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
  image = Image.open(uploaded_file)
  st.image(image, caption="معاينة المخطط", use_container_width=True)

  if not api_key:
    st.warning("⚠️ يرجى إدخال مفتاح Groq API المجاني في الشريط الجانبي للمتابعة.")
  else:
    if st.button("🚀 تحليل المخطط مجاناً"):
      with st.spinner("🔍 جاري فحص المخطط واستخراج الكميات عبر Groq..."):
        try:
          # تحويل الصورة إلى Base64
          buffered = io.BytesIO()
          image.save(buffered, format="JPEG")
          base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

          # إرسال الطلب إلى واجهة Groq المجانية للرؤية الحاسوبية
          headers = {
              "Authorization": f"Bearer {api_key}",
              "Content-Type": "application/json",
          }

          payload = {
              "model": "llama-3.2-11b-vision-preview",
              "messages": [{
                  "role": "user",
                  "content": [
                      {
                          "type": "text",
                          "text": (
                              "قم بتحليل هذا المخطط الكهربائي وعد جميع العناصر"
                              " الظاهرة (مثل المفاتيح، المآخذ، الإضاءة، لوحات"
                              " التوزيع). أجب فقط بصيغة JSON صحيح يحتوي على مفتاح"
                              " 'items' وتحته قائمة بكل عنصر له 'Item_Name' و"
                              " 'Quantity'."
                          ),
                      },
                      {
                          "type": "image_url",
                          "image_url": {
                              "url": f"data:image/jpeg;base64,{base64_image}"
                          },
                      },
                  ],
              }],
              "response_format": {"type": "json_object"},
          }

          response = requests.post(
              "https://api.groq.com/openai/v1/chat/completions",
              headers=headers,
              json=payload,
          )
          result_data = response.json()

          if "choices" in result_data:
            content_str = result_data["choices"][0]["message"]["content"]
            result_json = json.loads(content_str)
            items_list = (
                result_json.get("items")
                or result_json.get("elements")
                or list(result_json.values())[0]
            )

            processed_data = []
            total_cost = 0
            total_items_count = 0

            for row in items_list:
              name = (
                  row.get("Item_Name") or row.get("name") or "عنصر غير معروف"
              )
              qty = int(row.get("Quantity") or row.get("quantity") or 1)
              total_items_count += qty

              unit_price = prices.get(name, 400)
              subtotal = qty * unit_price
              total_cost += subtotal

              processed_data.append({
                  "العنصر الكهربائي": name,
                  "الكمية": qty,
                  "سعر الوحدة (دج)": unit_price,
                  "المجموع الفرعي (دج)": subtotal,
              })

            df = pd.DataFrame(processed_data)

            st.success("✨ تم التحليل بنجاح وبدون أي تكلفة!")

            col1, col2 = st.columns(2)
            with col1:
              st.markdown(
                  f"""
                  <div class="metric-card">
                      <p style="color: #64748b; margin: 0; font-size: 0.85rem;">إجمالي القطع</p>
                      <h3 style="color: #2563eb; margin: 5px 0 0 0;">{total_items_count}</h3>
                  </div>
                  """,
                  unsafe_allow_html=True,
              )
            with col2:
              st.markdown(
                  f"""
                  <div class="metric-card">
                      <p style="color: #64748b; margin: 0; font-size: 0.85rem;">التكلفة الإجمالية</p>
                      <h3 style="color: #16a34a; margin: 5px 0 0 0;">{total_cost:,.0f} دج</h3>
                  </div>
                  """,
                  unsafe_allow_html=True,
              )

            st.markdown("### 📋 جدول الكميات (BOQ)")
            st.dataframe(df, use_container_width=True)

            # زر تصدير Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
              df.to_excel(writer, index=False, sheet_name="Electrical_BOQ")
            excel_data = output.getvalue()

            st.download_button(
                label="📥 تحميل الجدول كملف Excel",
                data=excel_data,
                file_name="Electrical_BOQ.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )
          else:
            st.error(f"خطأ من الخادم: {result_data}")

        except Exception as e:
          st.error(f"حدث خطأ أثناء المعالجة: {e}")
