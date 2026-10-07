import re

def update_app():
    with open("c:/Users/Administrator/Desktop/ps4/app.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Regex to find render_cost_analytics
    pattern = re.compile(
        r'(def render_cost_analytics\(\):\s*st\.html\(.*?"Cost Analytics".*?st\.info\(.*?"Cost analytics will use the benchmark profile.*?\)\n)(.*?def render_request_history\(\):)',
        re.DOTALL
    )
    
    new_func = """def render_cost_analytics():

    st.html(
        '<div class="dashboard-title">Cost Analytics</div>',
    )

    st.html(
        '<div class="dashboard-subtitle">'
        "Analyze the simulated inference cost of each model."
        "</div>",
    )

    try:
        cost_simulator = get_cost_simulator()
        cost_profile = cost_simulator.get_cost_profile()
    except Exception as e:
        st.error(f"Failed to load cost data: {e}")
        return

    if not cost_profile or "Model A" not in cost_profile:
        st.warning("Cost profile is incomplete.")
        return

    # Calculate Summaries
    model_a_cost = cost_profile["Model A"]["simulated_cost"]
    
    most_expensive_model = max(cost_profile.keys(), key=lambda k: cost_profile[k]["simulated_cost"])
    highest_ratio = max(cost_profile[k]["latency_ratio"] for k in cost_profile.keys())
    num_models = len(cost_profile)

    # Render summary cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Baseline Cost
                </div>
                <div class="metric-value">
                    ₹{model_a_cost:.4f}
                </div>
            </div>
            ''')
        )

    with col2:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Most Expensive Model
                </div>
                <div class="metric-value">
                    {most_expensive_model}
                </div>
            </div>
            ''')
        )

    with col3:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Highest Cost Ratio
                </div>
                <div class="metric-value">
                    {highest_ratio:.2f}×
                </div>
            </div>
            ''')
        )

    with col4:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Models Analyzed
                </div>
                <div class="metric-value">
                    {num_models}
                </div>
            </div>
            ''')
        )

    import pandas as pd

    st.html(
        '<div class="section-title">Model Cost Comparison</div>',
    )
    
    chart_data = pd.DataFrame(
        [
            {"Model": m, "Simulated Cost (₹)": cost_profile[m]["simulated_cost"]} 
            for m in cost_profile
        ]
    ).set_index("Model")
    
    st.bar_chart(chart_data)

    table_data = []
    for m in cost_profile:
        table_data.append({
            "Model": m,
            "Latency (ms)": f"{cost_profile[m]['latency_ms']:.2f} ms",
            "Relative Cost": f"{cost_profile[m]['latency_ratio']:.2f}×",
            "Simulated Cost (₹)": f"₹{cost_profile[m]['simulated_cost']:.4f}"
        })
    st.table(pd.DataFrame(table_data))

    st.html(
        '<div class="section-title">Simulated Cost Savings</div>',
    )
    
    for m in cost_profile:
        if m == "Model A":
            continue
            
        savings_info = cost_simulator.calculate_savings("Model A", m)
        expensive_cost = cost_profile[m]["simulated_cost"]
        saving_amt = savings_info["savings"]
        pct_saving = savings_info["savings_percentage"]
        
        st.html(
            dedent(f'''
            <div class="info-card">
                <strong>Model A vs {m}</strong><br>
                <div style="margin-top:0.5rem; color:#172033;">
                    Cost of {m}: ₹{expensive_cost:.4f} <br>
                    Cost of Model A: ₹{model_a_cost:.4f} <br>
                    <strong>Simulated savings per request:</strong> ₹{saving_amt:.4f} <br>
                    <strong>Percentage difference:</strong> {pct_saving:.1f}%
                </div>
            </div>
            ''')
        )
        
    st.html(
        '<div class="section-title">How Cost Is Calculated</div>',
    )
    
    st.html(
        dedent('''
        <div class="info-card" style="color:#172033;">
            Model A is used as the baseline.<br><br>
            
            <strong>Latency ratio:</strong><br>
            model latency / Model A latency<br><br>
            
            <strong>Simulated cost:</strong><br>
            baseline cost × latency ratio<br><br>
            
            <em>Example:</em><br>
            If a model takes approximately 10× the baseline latency, 
            its simulated cost is approximately 10× the baseline cost.<br><br>
            
            <span style="color:#667085; font-size:0.85rem;">
                This is a simulated benchmark-based cost model for the educational 
                prototype and does not represent actual cloud provider pricing.
            </span>
        </div>
        ''')
    )


\\2"""
    
    # We replace everything between render_cost_analytics definition and render_request_history definition
    if pattern.search(content):
        new_content = pattern.sub(new_func, content)
        with open("c:/Users/Administrator/Desktop/ps4/app.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Replaced successfully!")
    else:
        print("Pattern not found!")

if __name__ == "__main__":
    update_app()
