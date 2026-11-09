import base64
import io
import json
import pandas as pd
import streamlit as st
from openai import OpenAI
from PIL import Image

# إعداد الصفحة وتصميم واجهة احترافي
st.set_page_config(
    page_title="VoltEstimate AI - محلل المخططات الكهربائية",
    page_icon="⚡",
    layout="centered",
)

# حقن أكواد CSS مخصصة لتجميل الواجهة وإعطاء لمسة إبداعية احترافية
st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #0f172a;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        text-align: center;
        margin-bottom: 15px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: white;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] .stMarkdown {
        color: #f1f5f9 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# الهيدر الإبداعي
st.markdown(
    "<h1 style='text-align: center; color: #1e293b;'>⚡ VoltEstimate AI</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 1.1rem;'>المنصة"
    " الذكية لحصر كميات المخططات الكهربائية وحساب التكاليف بالذكاء"
    " الاصطناعي</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# الشريط الجانبي (الإعدادات والأسعار)
st.sidebar.markdown(
    "### ⚙️ إعدادات النظام", help="أدخل مفتاح الـ API وحدد أسعار العتاد"
)
api_key = st.sidebar.text_input(
    "مفتاح OpenAI API Key", type="password", placeholder="sk-..."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ جدول أسعار الوحدات (دج)")

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

# مساحة رفع الملفات بتصميم جذاب
st.markdown("### 📂 ارفع المخطط الكهربائي")
uploaded_file = st.file_uploader(
    "اختر صورة المخطط (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
  col1, col2, col3 = st.columns([1, 6, 1])
  with col2:
    image = Image.open(uploaded_file)
    st.image(
        image,
        caption="معاينة المخطط الكهربائي",
        use_container_width=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)

  if not api_key:
    st.warning(
        "⚠️ يرجى إدخال مفتاح OpenAI API Key في الشريط الجانبي لمتابعة التحليل."
    )
  else:
    if st.button("🚀 تحليل المخطط وحساب التكلفة الإجمالية"):
      with st.spinner("🔍 جاري فحص الرموز هندسياً وحساب الكميات..."):
        try:
          client = OpenAI(api_key=api_key)

          # تجهيز الصورة للإرسال
          buffered = io.BytesIO()
          image.save(buffered, format="JPEG")
          base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

          response = client.chat.completions.create(
              model="gpt-4o",
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "أنت مهندس كهرباء خبير في حصر الكميات وقراءة المخططات"
                          " الهندسية. قم بفحص الصورة المرفقة بعناية، وعدّ جميع"
                          " العناصر الكهربائية الظاهرة (مثل المفاتيح، المآخذ،"
                          " نقاط الإضاءة، لوحات التوزيع). أجب بصيغة جدول بيانات"
                          " JSON يحتوي على قائمة بالعناصر وكل عنصر له 'Item_Name'"
                          " و 'Quantity'."
                      ),
                  },
                  {
                      "role": "user",
                      "content": [
                          {
                              "type": "text",
                              "text": (
                                  "استخرج جدول الكميات (BOQ) من هذا المخطط"
                                  " الكهربائي بدقة."
                              ),
                          },
                          {
                              "type": "image_url",
                              "image_url": {
                                  "url": (
                                      f"data:image/jpeg;base64,{base64_image}"
                                  )
                              },
                          },
                      ],
                  },
              ],
              response_format={"type": "json_object"},
          )

          result_json = json.loads(response.choices[0].message.content)
          items_list = (
              result_json.get("items")
              or result_json.get("elements")
              or list(result_json.values())[0]
          )

          processed_data = []
          total_cost = 0
          total_items_count = 0

          for row in items_list:
            name = row.get("Item_Name") or row.get("name") or "عنصر غير معروف"
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

          st.success("✨ تم تحليل المخطط بنجاح استناداً إلى الرموز المرئية!")

          # عرض ملخص إبداعي في بطاقات (Metrics Cards)
          mcol1, mcol2 = st.columns(2)
          with mcol1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <p style="color: #64748b; margin: 0; font-size: 0.9rem;">إجمالي القطع المرصودة</p>
                    <h2 style="color: #2563eb; margin: 5px 0 0 0;">{total_items_count} قطعة</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
          with mcol2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <p style="color: #64748b; margin: 0; font-size: 0.9rem;">التكلفة الإجمالية للعتاد</p>
                    <h2 style="color: #16a34a; margin: 5px 0 0 0;">{total_cost:,.2f} دج</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

          # عرض الجدول التفصيلي بشكل أنيق
          st.markdown("### 📋 جدول الكميات المعتمد (BOQ)")
          st.dataframe(df, use_container_width=True)

          # ميزة التصدير إلى ملف Excel
          output = io.BytesIO()
          with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Electrical_BOQ")
          processed_data_excel = output.getvalue()

          st.markdown("<br>", unsafe_allow_html=True)
          st.download_button(
              label="📥 تحميل جدول الكميات والتكاليف (Excel)",
              data=processed_data_excel,
              file_name="Electrical_BOQ_Estimate.xlsx",
              mime=(
                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              ),
          )

        except Exception as e:
          st.error(f"حدث خطأ أثناء المعالجة التقنية: {e}")

