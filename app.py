import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)  # Allows your HTML pages to talk to this server

@app.route('/api/generate', methods=['POST'])
def generate_ad():
    try:
        data = request.json
        prompt = data.get('prompt')
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return jsonify({"text": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def recommend_channels():
    try:
        data = request.json
        
        # Build the exact prompt previously used in JavaScript
        prompt = f"""
        You are an expert advertising strategist. Based on the following business information, 
        recommend the TOP 3 BEST advertising channels from this list:
        - Newspaper Ads
        - TV Ads
        - Billboard Ads
        - Influencer Marketing
        - Google Ads
        - YouTube Ads
        - Meta Ads (Facebook/Instagram)

        Analyze the "Monthly Budget" and apply these exclusion rules strictly:
        1. If budget is less than ₹3,000: Do Not recommend Google ads.
        2. If Budget is less than ₹4,000: Do NOT recommend Influencer Marketing, YouTube Ads, or TV Ads.
        3. If Budget is less than ₹30,000: Do NOT recommend TV Ads, Influencer Marketing.

        Business Details:
        - Business Name: {data.get('businessName')}
        - Products/Services: {data.get('whatTheySell')}
        - Target Customer: {data.get('targetCustomer')}
        - Business Goal: {data.get('businessGoals')}
        - Location: {data.get('location', {}).get('city')}, {data.get('location', {}).get('state')}
        - Monthly Budget: ₹{data.get('budgetINR')}

        Return ONLY a valid JSON array with exactly 3 recommendations, each containing:
        {{
          "channel": "exact channel name from the list above",
          "reasons": ["reason point 1", "reason point 2", "reason point 3"]
        }}
        """

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        # Use generation_config to ensure JSON output
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse the AI response and send back to frontend
        
        return jsonify(json.loads(response.text))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard-analyze', methods=['POST'])
def analyze_dashboard():
    try:
        data = request.json
        business_name = data.get('businessName')
        business_type = data.get('businessType')
        budget = data.get('budget')
        
        # Move the creative and logic-heavy prompt here
        prompt = f"""
        You are a marketing expert. Analyze the following business and recommend the top 3 advertising channels from this list:
        1. Google Ads, 2. Youtube Ads, 3. Meta Ads, 4. Newspaper Ads, 5. TV Ads, 6. Billboard Ads, 7. Influencer Marketing

        Strict Exclusion Rules based on Monthly Budget:
        1. Budget < ₹3,000: Do NOT recommend Google Ads.
        2. Budget < ₹20,000: Do NOT recommend Influencer Marketing, YouTube Ads, or TV Ads.
        3. Budget < ₹50,000: Do NOT recommend TV Ads.

        Business Details:
        - Name: {business_name}
        - Type: {business_type}
        - Ad Budget: ₹{budget}

        Provide: Channel name, allocation percentage (summing to 100), expected conversion rate, and a brief reason.
        Return ONLY valid JSON:
        {{
          "channels": [
            {{
              "name": "Channel Name",
              "percentage": 45,
              "conversionRate": 4.5,
              "reason": "Brief explanation"
            }}
          ]
        }}
        """

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        # Use generation_config to force valid JSON output
        response = model.generate_content(
            prompt,
            generation_config={ "response_mime_type": "application/json" }
        )
        
        return jsonify(json.loads(response.text))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)