import json
from pathlib import Path

import streamlit as st


def match_actions(actions, concern, change_level, equipment_control):
    matches = []
    excluded = []

    for action in actions:
        if concern not in action["concerns"]:
            continue

        if change_level not in action["change_levels"]:
            continue

        if (
            action["requires_equipment_control"]
            and equipment_control
            != "Yes, I can authorize equipment changes"
        ):
            excluded.append({
                "title": action["title"],
                "reason": (
                    "This action requires authority to change installed "
                    "equipment. Your answer does not confirm that authority."
                )
            })
            continue

        matches.append({
            "title": action["title"],
            "description": action["description"],
            "reason": (
                f"It addresses '{concern}' and fits your preference "
                f"for '{change_level}'."
            ),
            "requires_equipment_control": (
                action["requires_equipment_control"]
            )
        })

    return matches, excluded

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
st.subheader("Your Recommended Next Steps")

catalog_path = Path(__file__).resolve().parent / "actions.json"

try:
    with catalog_path.open("r", encoding="utf-8") as file:
        actions = json.load(file)
except (OSError, json.JSONDecodeError):
    st.error(
        "The action catalog could not be loaded. "
        "Check that actions.json is beside app.py and contains valid JSON."
    )
    st.stop()

matches, excluded = match_actions(
    actions=actions,
    concern=main_concern,
    change_level=change_level,
    equipment_control=equipment_control
)

if matches:
    for number, action in enumerate(matches, start=1):
        st.markdown(f"### {number}. {action['title']}")
        st.write(action["description"])
        st.caption(f"Why this appears: {action['reason']}")

        if action["requires_equipment_control"]:
            st.caption(
                "Your equipment-control answer confirms that you "
                "can authorize changes. This is an investigation "
                "step, not a recommendation to purchase equipment."
            )
else:
    st.info(
        "No action in the current starter catalog matches this "
        "combination. That does not mean no suitable option exists."
    )

if change_level == "Programs or incentives to explore":
    st.caption(
        "Local-program matching is not connected yet. "
        "We will add verified resources separately."
    )

if excluded:
    with st.expander("What was not included, and why?"):
        for action in excluded:
            st.write(action["title"])
            st.caption(action["reason"])

st.caption(
    "Prototype: this first matching function uses your concern, "
    "change preference, and equipment control. Goal-based "
    "prioritization and heating-source matching are not connected yet."
)



st.subheader("Your Home Situation")

if home_status == "Rent":
  st.info(
    "You selected Rent. Your plan should distinguish actions you can take "
    "from equipment changes requiring approval."
  )
else:
  st.info(
    "You selected Own. This guide can include both everyday actions "
    "and potential home upgrades. Upgrade suggestions are starting "
    "points to investigate."
  )
