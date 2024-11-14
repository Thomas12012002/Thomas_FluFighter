import subprocess
import sys

# Ensure matplotlib is installed
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Matplotlib not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt  # Re-import after installation

import streamlit as st
import numpy as np

# Function to simulate infection dynamics
def simulate_infection_graph(population_size, initial_infected, R0, recovery_rate, isolation_rate, days, vaccination_rate, vaccine_efficacy):
    vaccinated_population = population_size * vaccination_rate
    unvaccinated_population = population_size * (1 - vaccination_rate)

    susceptible_vaccinated = [vaccinated_population - initial_infected * vaccination_rate]
    susceptible_unvaccinated = [unvaccinated_population - initial_infected * (1 - vaccination_rate)]
    infected_vaccinated = [initial_infected * vaccination_rate]
    infected_unvaccinated = [initial_infected * (1 - vaccination_rate)]
    recovered_vaccinated = [0]
    recovered_unvaccinated = [0]

    for _ in range(1, days + 1):
        new_infected_vaccinated = min((infected_vaccinated[-1] * R0 * vaccine_efficacy) * (susceptible_vaccinated[-1] / population_size) * (1 - isolation_rate), susceptible_vaccinated[-1])
        new_infected_unvaccinated = min((infected_unvaccinated[-1] * R0) * (susceptible_unvaccinated[-1] / population_size) * (1 - isolation_rate), susceptible_unvaccinated[-1])
        
        new_recovered_vaccinated = infected_vaccinated[-1] * recovery_rate
        new_recovered_unvaccinated = infected_unvaccinated[-1] * recovery_rate

        susceptible_vaccinated.append(susceptible_vaccinated[-1] - new_infected_vaccinated)
        susceptible_unvaccinated.append(susceptible_unvaccinated[-1] - new_infected_unvaccinated)
        infected_vaccinated.append(infected_vaccinated[-1] + new_infected_vaccinated - new_recovered_vaccinated)
        infected_unvaccinated.append(infected_unvaccinated[-1] + new_infected_unvaccinated - new_recovered_unvaccinated)
        recovered_vaccinated.append(recovered_vaccinated[-1] + new_recovered_vaccinated)
        recovered_unvaccinated.append(recovered_unvaccinated[-1] + new_recovered_unvaccinated)

    total_susceptible = np.array(susceptible_vaccinated) + np.array(susceptible_unvaccinated)
    total_infected = np.array(infected_vaccinated) + np.array(infected_unvaccinated)
    total_recovered = np.array(recovered_vaccinated) + np.array(recovered_unvaccinated)

    return total_susceptible, total_infected, total_recovered

# Streamlit UI
st.title("Interactive Infection Simulation")
st.write("Simulate infection dynamics with customizable parameters. Click 'Add Simulation' to add new scenarios, each will appear in a separate chart.")

# Parameters for the simulation
if 'simulations' not in st.session_state:
    st.session_state.simulations = []

# Form to add a new simulation
with st.form("Add new simulation"):
    population_size = st.number_input("Population Size", min_value=50, max_value=500, value=100, step=10)
    initial_infected = st.number_input("Initial Infected", min_value=1, max_value=50, value=5, step=1)
    R0 = st.slider("R0 (Infection Rate)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
    recovery_rate = st.slider("Recovery Rate", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    isolation_rate = st.slider("Isolation Rate", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    days = st.slider("Days", min_value=1, max_value=50, value=20, step=1)
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

# Display each simulation in a separate chart
for idx, params in enumerate(st.session_state.simulations):
    st.subheader(f"Simulation {idx + 1}")
    susceptible, infected, recovered = simulate_infection_graph(
        params["population_size"], params["initial_infected"], params["R0"], 
        params["recovery_rate"], params["isolation_rate"], params["days"], 
        params["vaccination_rate"], params["vaccine_efficacy"]
    )

    # Plot for each simulation
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(params["days"] + 1), susceptible, label='Susceptible', color='orange')
    ax.plot(range(params["days"] + 1), infected, label='Infected', color='red')
    ax.plot(range(params["days"] + 1), recovered, label='Recovered', color='green')
    
    ax.set_title(f'Infection Simulation {idx + 1}: Population Dynamics')
    ax.set_xlabel('Days')
    ax.set_ylabel('Population')
    ax.legend()
    ax.grid(True)
    
    # Display the chart for this simulation
    st.pyplot(fig)
