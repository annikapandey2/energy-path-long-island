import streamlit as st
st.title("Energy Path Long Island")
st.write("Answer a few questions to find energy-saving ideas for your home.")
home_status = st.radio(
  "Do you rent or own your home?",
  ["Rent", "Own"]
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

st.subheader("Estimated Impact")

if main_concern == "Water use or water heating":
    st.info(
        "For eligible ENERGY STAR-certified heat-pump water heaters, "
        "PSEG Long Island says rebates may be available up to $1,200. "
        "PSEG Long Island states that heat-pump water heaters can "
        "use up to 50% less energy than traditional water heaters. "
        "Actual savings and eligibility vary."
    )

elif main_concern == "Heating or cooling":
    st.info(
        "ENERGY STAR estimates that some homes with high heating and cooling "
        "bills, or homes unoccupied for much of the day, may save approximately "
        "$100 per year with an ENERGY STAR-certified smart thermostat. "
        "Actual savings and eligibility vary."
    )

elif main_concern == "Lighting and electronics":
    st.info(
        "PSEG Long Island recommends turning off lights and electronics when "
        "they are not in use and choosing efficient lighting and electronics. "
        "Your exact savings depend on your current equipment and habits."
    )

else:
    st.info(
        "Your exact savings depend on your home, heating system, equipment, "
        "energy use, and any improvements completed. This app provides guidance, "
        "not a guaranteed savings estimate."
    )
st.subheader("Your Home Situation")

if home_status == "Rent":
  st.info(
    "You selected Rent. This guide will prioritze changes that do not"
    "require replacing building equipment. Before making changes to"
    "the property or installed equipment, check with your landlord"
    "or property manager."
  )
else:
  st.info(
    "You selected Own. This guide can include both everday actions"
    "and potential home upgrades. Upgrade suggestions are starting"
    "points to investigate."
  )
