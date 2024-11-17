import subprocess
import sys

# Ensure necessary packages are installed
required_packages = ['matplotlib', 'streamlit', 'numpy', 'plotly']
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Function to simulate infection dynamics and track individual states
def simulate_infection_with_individuals(population_size, initial_infected, R0, recovery_rate, isolation_rate, days, vaccination_rate, vaccine_efficacy):
    # Initialize population
    population = []
    for i in range(population_size):
        if i < initial_infected:
            status = 'Infected'
        else:
            status = 'Susceptible'
        vaccinated = np.random.rand() < vaccination_rate
        population.append({
            'status': status,
            'vaccinated': vaccinated,
            'position': np.random.rand(2)  # Random initial position
        })
    
    # Lists to store aggregate data
    susceptible_vaccinated = []
    susceptible_unvaccinated = []
    infected_vaccinated = []
    infected_unvaccinated = []
    recovered_vaccinated = []
    recovered_unvaccinated = []

    # Lists to store population states per day for animation
    population_history = []

    for day in range(days + 1):
        # Record current state
        susceptible_vaccinated_day = sum(1 for p in population if p['status'] == 'Susceptible' and p['vaccinated'])
        susceptible_unvaccinated_day = sum(1 for p in population if p['status'] == 'Susceptible' and not p['vaccinated'])
        infected_vaccinated_day = sum(1 for p in population if p['status'] == 'Infected' and p['vaccinated'])
        infected_unvaccinated_day = sum(1 for p in population if p['status'] == 'Infected' and not p['vaccinated'])
        recovered_vaccinated_day = sum(1 for p in population if p['status'] == 'Recovered' and p['vaccinated'])
        recovered_unvaccinated_day = sum(1 for p in population if p['status'] == 'Recovered' and not p['vaccinated'])

        susceptible_vaccinated.append(susceptible_vaccinated_day)
        susceptible_unvaccinated.append(susceptible_unvaccinated_day)
        infected_vaccinated.append(infected_vaccinated_day)
        infected_unvaccinated.append(infected_unvaccinated_day)
        recovered_vaccinated.append(recovered_vaccinated_day)
        recovered_unvaccinated.append(recovered_unvaccinated_day)

        # Record population state for animation
        population_snapshot = []
        for p in population:
            population_snapshot.append({
                'status': p['status'],
                'vaccinated': p['vaccinated'],
                'position': p['position'].copy()
            })
        population_history.append(population_snapshot)

        if day == days:
            break  # Don't simulate beyond the last day

        # Infection spread
        for p in population:
            if p['status'] == 'Infected':
                # Determine number of contacts
                contacts = np.random.poisson(R0)
                for _ in range(contacts):
                    target = np.random.choice(population)
                    if target['status'] == 'Susceptible':
                        # Apply isolation rate
                        if np.random.rand() < (1 - isolation_rate):
                            # Apply vaccine efficacy if target is vaccinated
                            if target['vaccinated']:
                                effective_R0 = R0 * vaccine_efficacy
                            else:
                                effective_R0 = R0
                            if np.random.rand() < effective_R0 / R0:  # Simple infection probability
                                target['status'] = 'Infected'

        # Recovery
        for p in population:
            if p['status'] == 'Infected':
                if np.random.rand() < recovery_rate:
                    p['status'] = 'Recovered'

    # Aggregate data
    total_susceptible = np.array(susceptible_vaccinated) + np.array(susceptible_unvaccinated)
    total_infected = np.array(infected_vaccinated) + np.array(infected_unvaccinated)
    total_recovered = np.array(recovered_vaccinated) + np.array(recovered_unvaccinated)

    return (total_susceptible, total_infected, total_recovered, population_history)

# Streamlit UI
st.title("Interactive Infection Simulation")
st.write("Simulate infection dynamics with customizable parameters. Click 'Add Simulation' to add new scenarios, each will appear with a static curve and an animated dots simulation.")

# Parameters for the simulation
if 'simulations' not in st.session_state:
    st.session_state.simulations = []

# Form to add a new simulation
with st.form("Add new simulation"):
    population_size = st.number_input("Population Size", min_value=50, max_value=1000, value=200, step=10)
    initial_infected = st.number_input("Initial Infected", min_value=1, max_value=100, value=10, step=1)
    R0 = st.slider("R0 (Infection Rate)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
    recovery_rate = st.slider("Recovery Rate", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    isolation_rate = st.slider("Isolation Rate", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    days = st.slider("Days", min_value=1, max_value=100, value=30, step=1)
    vaccination_rate = st.slider("Vaccination Rate", min_value=0.0, max_value=1.0, value=0.7, step=0.01)
    vaccine_efficacy = st.slider("Vaccine Efficacy", min_value=0.1, max_value=1.0, value=0.9, step=0.01)
    
    # Submit button
    if st.form_submit_button("Add Simulation"):
        simulation_parameters = {
            "population_size": population_size,
            "initial_infected": initial_infected,
            "R0": R0,
            "recovery_rate": recovery_rate,
            "isolation_rate": isolation_rate,
            "days": days,
            "vaccination_rate": vaccination_rate,
            "vaccine_efficacy": vaccine_efficacy,
        }
        st.session_state.simulations.append(simulation_parameters)

# Display each simulation with curve and animated dots
for idx, params in enumerate(st.session_state.simulations):
    st.subheader(f"Simulation {idx + 1}")

    # Run simulation
    susceptible, infected, recovered, population_history = simulate_infection_with_individuals(
        params["population_size"], params["initial_infected"], params["R0"], 
        params["recovery_rate"], params["isolation_rate"], params["days"], 
        params["vaccination_rate"], params["vaccine_efficacy"]
    )

    # Create columns for side-by-side layout
    curve_col, dots_col = st.columns(2)

    # Plot the static curve in the right column
    with curve_col:
        fig_curve, ax_curve = plt.subplots(figsize=(5, 4))
        ax_curve.plot(range(params["days"] + 1), susceptible, label='Susceptible', color='orange')
        ax_curve.plot(range(params["days"] + 1), infected, label='Infected', color='red')
        ax_curve.plot(range(params["days"] + 1), recovered, label='Recovered', color='green')
        
        ax_curve.set_title(f'Population Dynamics')
        ax_curve.set_xlabel('Days')
        ax_curve.set_ylabel('Number of Individuals')
        ax_curve.legend()
        ax_curve.grid(True)
        
        st.pyplot(fig_curve)

    # Create the animated dots plot in the left column
    with dots_col:
        # Prepare data for Plotly animation
        frames = []
        for day, population_snapshot in enumerate(population_history):
            x = [p['position'][0] + np.random.uniform(-0.05, 0.05) for p in population_snapshot]  # Add slight movement
            y = [p['position'][1] + np.random.uniform(-0.05, 0.05) for p in population_snapshot]
            colors = []
            for p in population_snapshot:
                if p['status'] == 'Susceptible':
                    colors.append('blue' if p['vaccinated'] else 'lightblue')
                elif p['status'] == 'Infected':
                    colors.append('red')
                elif p['status'] == 'Recovered':
                    colors.append('green')
            frames.append(go.Frame(data=[go.Scatter(
                x=x,
                y=y,
                mode='markers',
                marker=dict(color=colors, size=8, opacity=0.7),
                showlegend=False
            )],
            name=str(day)))

        # Initial data
        initial_population = population_history[0]
        x_init = [p['position'][0] for p in initial_population]
        y_init = [p['position'][1] for p in initial_population]
        colors_init = ['blue' if p['vaccinated'] else 'lightblue' for p in initial_population]

        fig_dots = go.Figure(
            data=[go.Scatter(
                x=x_init,
                y=y_init,
                mode='markers',
                marker=dict(color=colors_init, size=8, opacity=0.7)
            )],
            layout=go.Layout(
                title='Infection Spread Simulation',
                xaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False),
                yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False),
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(label="Play",
                                  method="animate",
                                  args=[None, {"frame": {"duration": 500, "redraw": True},
                                               "fromcurrent": True, "transition": {"duration": 0}}])]
                )]
            ),
            frames=frames
        )

        st.plotly_chart(fig_dots, use_container_width=True)
