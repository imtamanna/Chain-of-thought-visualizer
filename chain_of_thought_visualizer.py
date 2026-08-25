#!/usr/bin/env python3
"""
Simple Chain-of-Thought Visualizer
Live toolkit with Ollama - visualizes AI reasoning patterns
"""

import re
import ollama
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo

class ChainOfThoughtVisualizer:
    def __init__(self, model="llama3:latest"):
        self.model = model
        
        # Thinking stage patterns
        self.patterns = {
            'analysis': [r'analyz', r'examin', r'consider', r'look at'],
            'planning': [r'plan', r'structur', r'organiz', r'approach'],
            'research': [r'research', r'information', r'fact', r'data'],
            'synthesis': [r'combin', r'integrat', r'put together', r'synthes'],
            'evaluation': [r'evaluat', r'assess', r'compar', r'weigh'],
            'problem_solving': [r'solv', r'fix', r'address', r'method']
        }
    
    def get_thinking(self, query):
        """Get chain-of-thought from Ollama"""
        prompt = f"""Think step by step about this query and explain your reasoning process:

Query: {query}

Please format your response as:
THINKING: [Your detailed step-by-step thinking process]
ANSWER: [Your final answer]

Be explicit about your reasoning stages - analysis, planning, research, synthesis, evaluation, and problem-solving."""
        
        response = ollama.generate(model=self.model, prompt=prompt)
        full_response = response['response']
        
        # Extract thinking and answer
        if "THINKING:" in full_response and "ANSWER:" in full_response:
            thinking = full_response.split("THINKING:")[1].split("ANSWER:")[0].strip()
            answer = full_response.split("ANSWER:")[1].strip()
        else:
            thinking = full_response
            answer = "Generated response"
            
        return thinking, answer
    
    def parse_thinking(self, thinking_text):
        """Parse thinking into stages"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', thinking_text) if s.strip()]
        stages = []
        
        for i, sentence in enumerate(sentences):
            stage_type = self.classify_stage(sentence.lower())
            duration = len(sentence.split()) * 0.1  # ~100ms per word
            
            stages.append({
                'content': sentence,
                'type': stage_type,
                'duration': duration,
                'index': i
            })
        
        return stages
    
    def classify_stage(self, text):
        """Classify text into thinking stage"""
        for stage_type, patterns in self.patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                return stage_type
        return 'general'
    
    def create_visualizations(self, stages):
        """Create both interval and pie charts"""
        # Prepare data
        stage_names = [s['type'].replace('_', ' ').title() for s in stages]
        durations = [s['duration'] for s in stages]
        contents = [s['content'][:50] + '...' if len(s['content']) > 50 else s['content'] for s in stages]
        
        # Colors for stages
        colors = {
            'Analysis': '#FF6B6B', 'Planning': '#4ECDC4', 'Research': '#45B7D1',
            'Synthesis': '#FFA07A', 'Evaluation': '#98D8C8', 'Problem Solving': '#F7DC6F',
            'General': '#BDC3C7'
        }
        
        # Create subplots with more space
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Thinking Sequence (Interval Chart)', 'Time Distribution (Pie Chart)'),
            specs=[[{"type": "bar"}, {"type": "pie"}]],
            horizontal_spacing=0.25,
            column_widths=[0.55, 0.45]
        )
        
        # Interval chart - add individual traces for legend
        for i, (stage_name, duration, content) in enumerate(zip(stage_names, durations, contents)):
            fig.add_trace(
                go.Bar(
                    x=[duration],
                    y=[i],
                    orientation='h',
                    text=[content],
                    textposition='inside',
                    marker_color=colors.get(stage_name, '#BDC3C7'),
                    name=stage_name,
                    hovertemplate=f'<b>{content}</b><br>Duration: {duration:.1f}s<extra></extra>',
                    legendgroup=stage_name,
                    showlegend=stage_name not in [trace.name for trace in fig.data if hasattr(trace, 'name')]
                ),
                row=1, col=1
            )
        
        # Pie chart - aggregate by stage type
        stage_totals = {}
        for stage in stages:
            stage_type = stage['type'].replace('_', ' ').title()
            stage_totals[stage_type] = stage_totals.get(stage_type, 0) + stage['duration']
        
        fig.add_trace(
            go.Pie(
                labels=list(stage_totals.keys()),
                values=list(stage_totals.values()),
                hole=0.3,
                marker_colors=[colors.get(label, '#BDC3C7') for label in stage_totals.keys()],
                showlegend=True,
                legendgroup="pie",
                textinfo='label+percent',
                textposition='inside'
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Chain-of-Thought Analysis",
            height=650,
            showlegend=True,
            margin=dict(l=60, r=120, t=80, b=60),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.9,
                xanchor="left",
                x=1.02
            )
        )
        
        fig.update_xaxes(title_text="Duration (seconds)", row=1, col=1)
        fig.update_yaxes(title_text="Thinking Sequence", row=1, col=1)
        
        return fig
    
    def visualize(self, query):
        """Complete visualization pipeline"""
        print(f"🤔 Processing: {query}")
        
        # Get AI thinking
        thinking, answer = self.get_thinking(query)
        
        # Parse stages
        stages = self.parse_thinking(thinking)
        
        print(f"🧠 Identified {len(stages)} thinking stages")
        
        # Create and show visualization
        fig = self.create_visualizations(stages)
        pyo.plot(fig, filename='chain_of_thought.html', auto_open=True)
        
        print("📊 Visualization opened in browser")
        return thinking, answer, stages

def main():
    """Live chain-of-thought visualizer"""
    visualizer = ChainOfThoughtVisualizer()
    
    print("🚀 Chain-of-Thought Visualizer")
    print("Enter queries to see AI reasoning patterns")
    print("Type 'quit' to exit\n")
    
    while True:
        query = input("Query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
            
        if not query:
            continue
            
        try:
            thinking, answer, stages = visualizer.visualize(query)
            print(f"\n💡 Answer: {answer[:100]}...")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 