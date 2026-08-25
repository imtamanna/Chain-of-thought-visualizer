#!/usr/bin/env python3
"""
Simple Web Portal for Chain-of-Thought Visualization
"""

from flask import Flask, render_template_string, request, jsonify
import json
from chain_of_thought_visualizer import ChainOfThoughtVisualizer
import plotly.utils

app = Flask(__name__)
visualizer = ChainOfThoughtVisualizer()

# Simple HTML template with everything inline
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chain-of-Thought Visualizer</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .query-section { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .query-input { width: 100%; padding: 15px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        .analyze-btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px; }
        .analyze-btn:hover { background: #0056b3; }
        .analyze-btn:disabled { background: #ccc; cursor: not-allowed; }
        .loading { display: none; text-align: center; padding: 20px; color: #666; }
        .results { display: none; margin-top: 20px; }
        .thinking-section, .answer-section { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .section-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333; }
        .thinking-text { background: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; font-family: monospace; font-size: 14px; }
        .answer-text { font-size: 16px; line-height: 1.6; }
        .charts { margin-top: 20px; }
        .chart { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 30px; height: 700px; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-top: 20px; display: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Chain-of-Thought Visualizer</h1>
        <p>Enter a query to see how AI thinks step by step</p>
    </div>

    <div class="query-section">
        <input type="text" id="queryInput" class="query-input" placeholder="Enter your query (e.g., 'Explain quantum computing')" />
        <button id="analyzeBtn" class="analyze-btn">Analyze Chain of Thought</button>
        
        <div class="loading" id="loading">
            AI is thinking... This may take a moment...
        </div>
    </div>

    <div class="results" id="results">
        <div class="thinking-section">
            <div class="section-title">Chain of Thought</div>
            <div class="thinking-text" id="thinkingText"></div>
        </div>

        <div class="answer-section">
            <div class="section-title">Final Answer</div>
            <div class="answer-text" id="answerText"></div>
        </div>

        <div class="charts">
            <div class="chart">
                <div id="visualization"></div>
            </div>
        </div>
    </div>

    <div class="error" id="error"></div>

    <script>
        const queryInput = document.getElementById('queryInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const error = document.getElementById('error');

        async function analyzeQuery() {
            const query = queryInput.value.trim();
            
            if (!query) {
                showError('Please enter a query');
                return;
            }

            // Show loading state
            analyzeBtn.disabled = true;
            loading.style.display = 'block';
            results.style.display = 'none';
            error.style.display = 'none';

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Analysis failed');
                }

                displayResults(data);

            } catch (err) {
                showError(err.message);
            } finally {
                analyzeBtn.disabled = false;
                loading.style.display = 'none';
            }
        }

        function displayResults(data) {
            document.getElementById('thinkingText').textContent = data.thinking;
            document.getElementById('answerText').textContent = data.answer;

            const figure = JSON.parse(data.visualization);
            Plotly.newPlot('visualization', figure.data, figure.layout);

            results.style.display = 'block';
        }

        function showError(message) {
            error.textContent = message;
            error.style.display = 'block';
        }

        analyzeBtn.addEventListener('click', analyzeQuery);
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') analyzeQuery();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main portal page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process query and return results"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Get AI thinking
        thinking, answer = visualizer.get_thinking(query)
        
        # Parse stages
        stages = visualizer.parse_thinking(thinking)
        
        # Create visualization
        fig = visualizer.create_visualizations(stages)
        
        # Convert to JSON for frontend
        fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'thinking': thinking,
            'answer': answer,
            'visualization': fig_json,
            'stages_count': len(stages)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Chain-of-Thought Web Portal...")
    print("Open http://localhost:8080 in your browser")
    app.run(debug=True, host='0.0.0.0', port=8080) 