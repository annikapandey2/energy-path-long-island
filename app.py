import json
from pathlib import Path

import streamlit as st


def match_actions(actions, concern, change_level, equipment_control):
    matches = []
    excluded = []

    control_reasons = {
        "Only with landlord or property-manager approval": (
            "You said equipment changes require approval, so your "
            "next step is a discussion rather than an equipment purchase."
        ),
        "No, I cannot authorize equipment changes": (
            "You said you cannot authorize equipment changes, so "
            "this step focuses on documenting the issue for whoever can."
        ),
        "I am not sure": (
            "You are unsure about equipment authority, so clarify "
            "that before planning equipment changes."
        )
    }

    for action in actions:
        if concern not in action["concerns"]:
            continue

        if change_level not in action["change_levels"]:
            continue

        allowed_control = action.get("allowed_equipment_control")

        if (
            allowed_control is not None
            and equipment_control not in allowed_control
        ):
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

        reason = (
            f"It addresses '{concern}' and fits your preference "
            f"for '{change_level}'."
        )

        if allowed_control is not None:
            reason += " " + control_reasons[equipment_control]

        matches.append({
            "title": action["title"],
            "description": action["description"],
            "reason": reason,
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
st.header("Your next step")
st.write("A starting point based on your answers.")

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
        is_authority_summary = (
            action["title"].strip().lower()
            == "clarify equipment authority and prepare your concern summary"
        )

        with st.container(border=True):
            if len(matches) > 1:
                st.caption(f"STEP {number}")

            if is_authority_summary:
                st.subheader("Start with the person who can approve changes")
                st.write(
                    "Describe the heating or cooling problem before "
                    "planning equipment work. If you do not know who "
                    "can approve changes, find that out first."
                )

                st.markdown("#### Put together a few details")
                st.markdown(
                    "- Which rooms are affected?\n"
                    "- When does the problem happen?\n"
                    "- What equipment is involved, if you know?"
                )

                if home_status == "Rent":
                    st.write(
                        "Use these notes to start a conversation with "
                        "your landlord or property manager."
                    )
                else:
                    st.write(
                        "Share these notes with the person responsible "
                        "for approving equipment changes."
                    )
            else:
                st.subheader(action["title"])
                st.write(action["description"])

            if action["requires_equipment_control"]:
                st.caption(
                    "Explore your options first. This is not a "
                    "recommendation to buy or replace equipment."
                )

            with st.expander("Why this step?"):
                st.write(action["reason"])

                if action["requires_equipment_control"]:
                    st.write(
                        "You said you can authorize equipment changes."
                    )
else:
    st.info(
        "We do not have a next step for this combination yet. "
        "The current catalog is limited; this does not mean "
        "you have no options."
    )

if change_level == "Programs or incentives to explore":
    st.info(
        "Program and incentive matching is not available yet. "
        "No eligibility or rebate has been confirmed."
    )

if excluded:
    with st.expander("Other options—and why they are not shown"):
        for action in excluded:
            st.markdown(f"#### {action['title']}")
            st.write(action["reason"])
st.divider()
st.caption("ABOUT THIS PLAN")

if home_status == "Rent":
    st.caption(
        "You selected Rent. Equipment changes may need approval; "
        "the recommendations use your equipment-control answer."
    )
else:
    st.caption(
        "You selected Own. Equipment suggestions are options "
        "to investigate, not purchase recommendations."
    )

st.caption(
    "Early prototype: recommendations currently use your main concern, "
    "change preference, and equipment-control answer. Your goal and "
    "heating source do not affect the results yet."
)
