import streamlit as st
st.title("Energy Path Long Island")
st.write("Answer a few questions to find energy-saving ideas for your home.")
home_status = st.radio(
  "Do you rent or own your home?",
  ["Rent", "Own"]
)
equipment_control = st.radio(
   "Can you make changes to installed heating, cooling, or water-heating equipment?",
  [
    "Yes, I can authorize equipment changes",
    "Only with landlord or property-manager approval",
    "No, I cannot authorize equipment changes",
    "I am not sure"
  ],
  index=None
)
  
main_goal = st.radio(
  "What is your main energy goal?",
  [
    "Lower my energy bill",
    "Make my home more comfortable",
    "Use less energy",
    "Learn about bigger home upgrades"
  ]
)
main_concern = st.radio(
  "What is your biggest energy concern right now?",
  [
    "Drafts or rooms that feel too hot or cold",
    "Heating or cooling",
    "Lighting and electronics",
    "Water use or water heating",
    "Appliances or high electricity use"
  ]
)
change_level = st.radio(
  "What kind of energy changes are you interested in?",
  [
    "Easy changes I can do now",
    "Programs or incentives to explore",
    "Bigger long-term updates"
  ]
)
heating_source = st.radio(
  "What is your primary heating source?",
  [
    "Electric heat",
    "Oil",
    "Natural Gas",
    "Heat pump",
    "I am not sure"
  ]
)

build_plan = st.button("Build My Plan", type="primary")

if not build_plan:
  st.info("Complete the questions, then select: Build My Plan.")
  st.stop()
if equipment_control is None:
  st.warning("Please answer the equipment-control question.")
  st.stop()
st.divider()
st.header("Your Energy Path")
st.subheader("Start Saving Now")

if main_concern == "Lighting and electronics":
  st.write("Use LED bulbs in the rooms you use most, turn off lights when leaving a room, and unplug chargers or electronics that are not being used.")
elif main_concern == "Water use or water heating":
  st.write("Take shorter showers, wash clothes in cold water when possible, and run full loads in the dishwasher or washing machine.")
elif main_concern == "Drafts or rooms that feel too hot or cold":
  st.write("Close curtains at night and check for noticeable gaps around doors and windows.")
elif main_concern == "Heating or cooling":
  st.write("Use thermostat settings consistently, keep vents clear, and avoid heating or cooling unused rooms when possible.")
elif main_concern == "Appliances or high electricity use":
  st.write("Run full appliance loads, use energy-saving settings, and replace older products with efficient models when they need to be replaced.")


st.subheader("Your Home Situation")

if home_status == "Rent":
  st.info(
    "You selected Rent. Your plan should distinguish actions you can take"
    "from equipment changes requiring approval."
  )
else:
  st.info(
    "You selected Own. This guide can include both everyday actions "
    "and potential home upgrades. Upgrade suggestions are starting "
    "points to investigate."
  )
