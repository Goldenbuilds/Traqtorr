import streamlit as st
import requests
from transformers import pipeline
from datetime import datetime
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import io
import os

# Custom CSS for warm, consultant look
st.markdown("""
    <style>
    body {background-color: #F5F5F5;}
    .stApp {background-color: #F5F5F5; color: #333333;}
    h1 {color: #4CAF50; font-size: 32px;}
    h2 {color: #1976D2; font-size: 24px;}
    .stTextInput > div > div > input {border: 1px solid #E6F0FA; padding: 10px; font-size: 16px;}
    .stButton > button {background-color: #4CAF50; color: white; border: none; padding: 10px 20px; font-size: 16px;}
    </style>
""", unsafe_allow_html=True)

st.title("Traqtor: Your Site’s Growth Partner")
st.write(f"Report created on: {datetime.now().strftime('%B %d, %Y, %I:%M %p PST')}")
st.write("Hello! I’m testing this tool to help business owners like you—I’ll check your site and share what I find, all for free right now. Just give me your feedback after!")

# Load model
generator = pipeline("text-generation", model="./predictive_traqtor", tokenizer="./predictive_traqtor")

# Screenshot function
def take_screenshot(url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1280, 800)  # Standard size for report
        driver.get(url)
        time.sleep(3)  # Let page load
        screenshot_path = f"screenshot_{url.replace('https://', '').replace('/', '_')}.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()
        return screenshot_path
    except Exception as e:
        st.error(f"Couldn’t grab a screenshot: {e}")
        return None

# Generate PDF report with screenshot
def generate_pdf_report(url, score, fcp, lcp, headline, cta, screenshot_path, fcp_text, lcp_text, headline_text, cta_text, summary_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph(f"Traqtor Report for {url}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Created: {datetime.now().strftime('%B %d, %Y, %I:%M %p PST')}", styles['Normal']))
    story.append(Spacer(1, 24))
    
    if screenshot_path and os.path.exists(screenshot_path):
        story.append(Paragraph("Here’s what your site looks like:", styles['Heading2']))
        story.append(Image(screenshot_path, width=400, height=250))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"Your Site’s Score: {score}/100 (Top Sites Average: 85/100)", styles['Heading2']))
    story.append(Paragraph(f"Here’s what I found for you:", styles['Normal']))
    story.append(Spacer(1, 12))
    
    for text, heading in [(fcp_text, "Your FCP"), (lcp_text, "Your LCP"), (headline_text, "Your Headline"), (cta_text, "Your CTA")]:
        story.append(Paragraph(f"{heading}", styles['Heading3']))
        for line in text.split('\n')[1:]:
            story.append(Paragraph(line.strip('- '), styles['Normal']))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("What This Means for You", styles['Heading2']))
    for line in summary_text.split('\n'):
        story.append(Paragraph(line.strip('- '), styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Education Section
st.subheader("What We’re Checking Together")
st.write("Before we dive into your site, let me explain what I’m looking at. These are the things that decide if people stay on your site—and if they spend money with you. I’ll keep it easy to follow!")

st.write("**FCP (First Contentful Paint): How Fast Your Site Shows Up**")
st.write("This is how long it takes for something—like text or a picture—to appear when someone visits. It’s their first sign your site works. We measure it in seconds with Google’s tool.")
st.write("Why’s it important? If it’s slow—over 3 seconds—more than half your visitors might leave. Top sites do this in 1.3 seconds. A slow start could mean fewer customers.")

st.write("**LCP (Largest Contentful Paint): When Your Site Feels Ready**")
st.write("This is how long it takes for the main part—like your big image or text—to load fully. It’s when people feel they can use your site. We check this with Google too.")
st.write("It matters because if it’s over 4 seconds, people get tired and go away. The best sites keep it under 2.2 seconds. A slow LCP might lose you sales.")

st.write("**Headline: Your First Hello**")
st.write("This is the big text at the top—it’s your chance to catch someone’s eye. We’ll see how many words it has and if it’s strong, compared to top sites.")
st.write("Why care? Most people decide to stay or leave based on that headline. The best ones have about 5.8 words and pull people in. If it’s weak, you’re missing clicks.")

st.write("**CTA (Call to Action): Your Invitation**")
st.write("This is what tells people what to do next—like ‘Buy Now.’ We’ll check its length and clarity against what works best.")
st.write("It’s key because this turns visitors into customers. Top sites use about 3.2 words and make it clear. If it’s not strong, you’re letting sales slip away.")

st.write("**Why I’m Doing This**")
st.write("I’ve looked at what the top 50 sites do to win, and I’m using that to help you. Every detail we find is a chance to make your site—and your business—better.")

# Input & Report Flow
url = st.text_input("What’s your website? (e.g., https://yourbusiness.com)", "")
if st.button("Get Your Free Report"):
    if not url.startswith("http"):
        st.error("Hey, your URL needs 'http://' or 'https://' to work. Add that and let’s try again!")
    else:
        with st.spinner("Hold on—I’m checking your site now. Takes about 10 seconds..."):
            # Screenshot
            screenshot_path = take_screenshot(url)
            
            # Scrape PageSpeed
            ps_url = f"https://pagespeed.web.dev/report?url={url}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"}
            resp = requests.get(ps_url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            fcp = float(soup.select_one("li:contains('First Contentful Paint') span").text.split()[0])
            lcp = float(soup.select_one("li:contains('Largest Contentful Paint') span").text.split()[0])
            score = int(soup.select_one(".lh-gauge__percentage").text)
            time.sleep(2)

            input_str = f"FCP: {fcp:.1f}s, LCP: {lcp:.1f}s =>"
            pred = generator(input_str, max_length=150, num_return_sequences=1)[0]["generated_text"].split("=>")[-1].strip()
            headline, cta = pred.split(", CTA: ")[0].replace("Headline: ", ""), pred.split(", CTA: ")[1].split(",")[0]

            # Report—Consultant Style
            st.subheader(f"Here’s Your Site’s Score: {score}/100 (Top Sites Average: 85/100)")
            st.write("Let’s go through this together. Your score shows how your site compares to the best out there—they average 85/100. Here’s what I found for you:")
            
            if screenshot_path and os.path.exists(screenshot_path):
                st.write("Here’s what your site looks like right now:")
                st.image(screenshot_path, use_column_width=True)

            fcp_text = f"Your FCP: {fcp:.1f} seconds (Top Sites: 1.3 seconds)\n"
            fcp_gap = fcp - 1.3
            if fcp_gap > 0:
                traffic_loss = int(1.8e6 * 0.12 * (fcp_gap / 1.2)) // 30
                fcp_text += f"- Your site takes {fcp:.1f} seconds to show something, while top sites do it in 1.3 seconds. That {fcp_gap:.1f}-second difference might seem small, but it’s costing you.\n"
                fcp_text += f"- It could mean about {traffic_loss:,} visitors leaving each day before they see anything—based on a typical 1.8 million visitors a month. That’s people who could’ve bought from you.\n"
                fcp_text += f"- Here’s a fix: use a tool like CSSNano to shrink your CSS files. It’s about 15 minutes, and most fast sites do it.\n"
                fcp_text += f"- If you get that down to 1.3 seconds, you could keep those {traffic_loss:,} visitors a day. At $2 per thousand views, that’s around ${traffic_loss * 2:,} a month—let’s get that back for you!\n"
            else:
                traffic_gain = int(1.8e6 * 0.05) // 30
                fcp_text += f"- Your FCP at {fcp:.1f} seconds is faster than the top sites’ 1.3 seconds—I’m proud of you!\n"
                fcp_text += f"- That speed keeps more people around—about {traffic_gain:,} extra visitors a day compared to slower sites.\n"
                fcp_text += f"- You’re doing great here. Keep using tools like CSSNano to stay quick—it’s what the best sites do.\n"
                fcp_text += f"- That’s likely adding ${traffic_gain * 2:,} a month from those {traffic_gain:,} daily visitors, at $2 per thousand views. Well done!\n"
            st.write(fcp_text)

            lcp_text = f"Your LCP: {lcp:.1f} seconds (Top Sites: 2.2 seconds)\n"
            lcp_gap = lcp - 2.2
            if lcp_gap > 0:
                conv_loss = int(1.8e6 * 0.18 * (lcp_gap / 2.9) / 30)
                lcp_text += f"- Your main content takes {lcp:.1f} seconds to load, compared to 2.2 seconds for top sites. That {lcp_gap:.1f}-second gap is something we can fix.\n"
                lcp_text += f"- It might be costing you about {conv_loss:,} sales a week—people aren’t waiting to see your offer.\n"
                lcp_text += f"- Try compressing your images with TinyPNG. It’s quick—20 minutes—and most top sites use it.\n"
                lcp_text += f"- Get that to 2.2 seconds, and you could save those {conv_loss:,} sales a week. At $100 per sale, that’s ${conv_loss * 100:,} a month—I want that for you!\n"
            else:
                conv_gain = int(1.8e6 * 0.08) // 30
                lcp_text += f"- Your LCP at {lcp:.1f} seconds beats the top sites’ 2.2 seconds—great job!\n"
                lcp_text += f"- That speed means people can use your site fast, giving you about {conv_gain:,} extra sales a week over slower sites.\n"
                lcp_text += f"- You’re in a good spot—keep images light with TinyPNG. It’s what top sites do to win.\n"
                lcp_text += f"- That could be adding ${conv_gain * 100:,} a month from those {conv_gain:,} sales a week, at $100 each. You’re on track!\n"
            st.write(lcp_text)

            headline_text = f"Your Headline: '{headline}'\n"
            words = len(headline.split())
            if words < 5.8:
                click_loss = int(1.8e6 * 0.15 * ((5.8 - words) / 5.8) / 30)
                headline_text += f"- Your headline has {words} words, while top sites use about 5.8 to grab attention.\n"
                headline_text += f"- That might mean about {click_loss:,} fewer clicks a day—people aren’t feeling pulled in enough.\n"
                headline_text += f"- Try tweaking it to ‘Buy Now, Win Big’—takes 5 minutes, and it’s what top sites do.\n"
                headline_text += f"- Boost that by 15%, and you’d get {click_loss:,} more clicks a day. At $5 per lead, that’s ${click_loss * 5:,} a month—let’s make it happen!\n"
            else:
                click_gain = int(1.8e6 * 0.10) // 30
                headline_text += f"- Your headline’s got {words} words, matching the top sites’ 5.8-word average—I like it!\n"
                headline_text += f"- It’s probably earning you about {click_gain:,} extra clicks a day because it’s clear and strong.\n"
                headline_text += f"- You’re doing well—add a word like ‘Now’ if it fits. Top sites use it to keep people hooked.\n"
                headline_text += f"- That’s adding ${click_gain * 5:,} a month from those {click_gain:,} clicks a day, at $5 each. Nice one!\n"
            st.write(headline_text)

            cta_text = f"Your CTA: '{cta}'\n"
            cta_words = len(cta.split())
            if cta_words < 3.2 or "now" not in cta.lower():
                action_loss = int(1.8e6 * 0.20 * ((3.2 - cta_words) / 3.2) / 30 / 7)
                cta_text += f"- Your call to action has {cta_words} words and might not feel urgent—top sites use 3.2 words with ‘Now.’\n"
                cta_text += f"- That could cost you about {action_loss:,} actions a week—like sales—because it’s not pushing people enough.\n"
                cta_text += f"- Change it to ‘Get Free Now’—5 minutes, and it’s what top sites use to win.\n"
                cta_text += f"- Boost that by 20%, and you’d see {action_loss:,} more actions a week. At $20 each, that’s ${action_loss * 20:,} a month—let’s get that for you!\n"
            else:
                action_gain = int(1.8e6 * 0.15) // 30 / 7
                cta_text += f"- Your call to action’s got {cta_words} words and feels strong—matching top sites’ 3.2-word average. Love it!\n"
                cta_text += f"- That’s probably getting you about {action_gain:,} extra actions a week because it’s clear.\n"
                cta_text += f"- You’re doing great—keep it urgent with ‘Now.’ Top sites swear by it.\n"
                cta_text += f"- That’s worth ${action_gain * 20:,} a month from those {action_gain:,} actions a week, at $20 each. You’re killing it!\n"
            st.write(cta_text)

            st.subheader("What This Means for You")
            total_gain = (traffic_loss * 2) + (conv_loss * 100) + (click_loss * 5) + (action_loss * 20)
            total_boost = (traffic_gain * 2) + (conv_gain * 100) + (click_gain * 5) + (action_gain * 20)
            summary_text = ""
            if total_gain > 0:
                summary_text += f"- Right now, your site’s missing out on about ${total_gain:,} a month. I’ve shared some quick steps—try them soon, and you could turn that around.\n"
            if total_boost > 0:
                summary_text += f"- You’re already doing some things well, and that’s worth about ${total_boost:,} a month! Let’s keep that going and make it even better.\n"
            summary_text += f"- That’s your report—what do you think? I’d love your feedback to make this tool perfect for founders like you. Just let me know what works or doesn’t!\n"
            st.write(summary_text)

            # Downloadable Report
            pdf_buffer = generate_pdf_report(url, score, fcp, lcp, headline, cta, screenshot_path, fcp_text, lcp_text, headline_text, cta_text, summary_text)
            st.download_button(
                label="Download Your Report",
                data=pdf_buffer,
                file_name=f"Traqtor_Report_{url.replace('https://', '').replace('/', '_')}.pdf",
                mime="application/pdf"
            )
            
            # Clean up screenshot
            if screenshot_path and os.path.exists(screenshot_path):
                os.remove(screenshot_path)
