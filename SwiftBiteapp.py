
import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SwiftBite Sales Intelligence Agent",
    page_icon="🍕",
    layout="wide"
)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🍕 SwiftBite Sales Intelligence Agent")
st.markdown("*AI-powered account insights for your next sales meeting*")
st.markdown("---")

# ─────────────────────────────────────────────
# SIDEBAR — API KEY INPUT
# ─────────────────────────────────────────────
st.sidebar.header("⚙️ Configuration")
groq_api_key = st.sidebar.text_input(
    "Enter your Groq API Key",
    type="password",
    help="Get your free API key at https://console.groq.com"
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 How to Use")
st.sidebar.markdown("""
1. Enter your Groq API key above
2. Fill in all the fields on the main page
3. Click **Generate Insights**
4. Download your one-pager report
""")

# ─────────────────────────────────────────────
# INPUT FORM
# ─────────────────────────────────────────────
st.header("📋 Sales Rep Input Form")
st.markdown("Fill in the details below to generate your account insight report.")

col1, col2 = st.columns(2)

with col1:
    product_name = st.text_input(
        "🏷️ Product Name",
        value="SwiftBite Delivery Management Platform",
        help="Name of the product you are selling"
    )
    company_url = st.text_input(
        "🌐 Target Company URL",
        value="https://www.chipotle.com",
        help="Website of the company you want to sell to"
    )
    product_category = st.text_input(
        "📂 Product Category",
        value="Restaurant Tech / Food Delivery SaaS",
        help="One word or short phrase describing your product category"
    )
    value_proposition = st.text_area(
        "💡 Value Proposition",
        value="Reduce delivery costs by 30% while increasing order accuracy through AI-powered dispatch and real-time tracking",
        help="One sentence summarizing what your product does for the customer"
    )

with col2:
    target_customer = st.text_input(
        "🎯 Target Customer",
        value="Chief Digital Officer",
        help="The person or role you are trying to sell to"
    )
    competitor1_url = st.text_input(
        "🥊 Competitor 1 URL",
        value="https://www.olo.com",
        help="URL of first competitor"
    )
    competitor2_url = st.text_input(
        "🥊 Competitor 2 URL",
        value="https://www.toast.com",
        help="URL of second competitor"
    )
    competitor3_url = st.text_input(
        "🥊 Competitor 3 URL",
        value="https://www.doordash.com",
        help="URL of third competitor (optional)"
    )

st.markdown("---")

# ─────────────────────────────────────────────
# WEB SCRAPING FUNCTION
# ─────────────────────────────────────────────
def scrape_website(url):
    """
    Scrapes basic text content from a given URL.
    Returns a short excerpt to feed into the AI prompt.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        # Get visible text
        text = soup.get_text(separator=" ", strip=True)

        # Return first 1500 characters to keep prompt short
        return text[:1500]
    except Exception as e:
        return f"Could not scrape {url}: {str(e)}"


# ─────────────────────────────────────────────
# GROQ AI FUNCTION
# ─────────────────────────────────────────────
def generate_insights(api_key, product, company_url, category,
                      value_prop, customer, competitors,
                      company_text, competitor_texts):
    """
    Sends a structured prompt to Groq's LLM and returns
    a formatted one-pager account insight report.
    """
    client = Groq(api_key=api_key)

    prompt = f"""
You are an expert B2B sales intelligence assistant specializing in 
the food delivery and restaurant technology industry.

A sales representative is preparing to sell the following product:

PRODUCT DETAILS:
- Product Name: {product}
- Product Category: {category}
- Value Proposition: {value_prop}
- Target Customer Title: {customer}

TARGET COMPANY:
- URL: {company_url}
- Website Content Excerpt: {company_text}

COMPETITORS:
{competitors}

COMPETITOR WEBSITE EXCERPTS:
{competitor_texts}

Your task is to generate a professional ONE-PAGE ACCOUNT INSIGHT REPORT 
for the sales representative. The report must include these sections:

---
SWIFTBITE ACCOUNT INSIGHT REPORT
Target Company: [Extract company name from URL]
Date: March 2026
Product: {product}
Prepared For: Sales Representative
---

1. COMPANY STRATEGY SUMMARY
   - Summarize what the company is focused on
   - Mention digital ordering or technology investments
   - Note relevant executive statements or technology direction
   - Identify job posting signals or technology stack hints

2. COMPETITOR LANDSCAPE
   - Mention which competitors the target company may be using
   - Note any publicly known partnerships or technology integrations
   - Highlight gaps that SwiftBite could fill

3. KEY LEADERSHIP INFORMATION
   - List the most relevant decision makers for this sale
   - Include their titles and why they matter
   - Note any public quotes or speaking engagements

4. PRODUCT/STRATEGY INSIGHTS
   - Summarize relevant financial or strategic data
   - Include annual report or press release highlights
   - Note technology investment trends

5. RECOMMENDED SALES TALKING POINTS
   - Provide 3 to 5 specific talking points for this account
   - Connect SwiftBite value proposition to company priorities
   - Suggest how to position against known competitors

6. SUGGESTED ARTICLE LINKS & SOURCES
   - List 3 to 5 sources the sales rep should review
   - Include trade publications, press releases, earnings calls
   - Format as: Source Name — Description — URL

Keep the tone professional, concise, and actionable.
Every sentence must be useful to the sales rep.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a professional B2B sales intelligence assistant. You only respond to sales account research tasks. You do not engage in general conversation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────
# GENERATE BUTTON
# ─────────────────────────────────────────────
if st.button("🚀 Generate Account Insights", type="primary", use_container_width=True):

    if not groq_api_key:
        st.error("❌ Please enter your Groq API key in the sidebar.")
    elif not company_url:
        st.error("❌ Please enter a target company URL.")
    else:
        progress = st.progress(0)
        status = st.empty()

        # Step 1 — Scrape target company
        status.info("🔍 Step 1/4 — Scraping target company website...")
        company_text = scrape_website(company_url)
        progress.progress(25)

        # Step 2 — Scrape competitors
        status.info("🔍 Step 2/4 — Scraping competitor websites...")
        competitor_urls = [competitor1_url, competitor2_url, competitor3_url]
        competitor_texts = ""
        for i, url in enumerate(competitor_urls):
            if url:
                text = scrape_website(url)
                competitor_texts += f"\nCompetitor {i+1} ({url}):\n{text[:500]}\n"
        progress.progress(50)

        competitors_list = "\n".join([
            f"- {url}" for url in competitor_urls if url
        ])

        # Step 3 — Generate AI report
        status.info("🤖 Step 3/4 — Generating AI-powered insights with Groq...")
        try:
            report = generate_insights(
                api_key=groq_api_key,
                product=product_name,
                company_url=company_url,
                category=product_category,
                value_prop=value_proposition,
                customer=target_customer,
                competitors=competitors_list,
                company_text=company_text,
                competitor_texts=competitor_texts
            )
            progress.progress(75)

            status.info("📄 Step 4/4 — Formatting your report...")
            progress.progress(100)
            status.success("✅ Report generated successfully!")

            st.markdown("---")
            st.header("📄 Account Insight Report")

            st.markdown(
                f"""
                <div style="
                    background-color: #f8f9fa;
                    border-left: 5px solid #FF6B35;
                    padding: 20px;
                    border-radius: 8px;
                    font-family: monospace;
                    white-space: pre-wrap;
                    font-size: 14px;
                ">
                {report}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")

            st.download_button(
                label="⬇️ Download Report as .txt",
                data=report,
                file_name="swiftbite_account_report.txt",
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            st.info("💡 Check that your Groq API key is correct and try again.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>SwiftBite Sales Intelligence Agent — CAP 931 Capstone Project</p>",
    unsafe_allow_html=True
)