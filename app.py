import json
from pathlib import Path

import streamlit as st
def match_actions(actions, concern, change_level, equipment_control):
    matches = []
    excluded = []

    control_reasons = {
        "Only with landlord or property-manager approval": (
            "Equipment changes need your landlord or property manager's "
            "approval, so start with a conversation."
        ),
        "No, I cannot authorize equipment changes": (
            "You cannot approve equipment changes yourself. "
            "These notes can help you explain the problem to someone who can."
        ),
        "I am not sure": (
            "You are not sure who can approve equipment changes. "
            "Find that out before planning equipment work."
        )
    }

    general_reasons = {
        "Easy changes I can do now": (
            "You chose steps you can take now. "
            "This starts with understanding your concern, "
            "rather than replacing equipment."
        ),
        "Bigger long-term updates": (
            "You want to explore a larger update. "
            "Start by understanding the existing equipment "
            "and the problem you want to solve."
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
                "id": action["id"],
                "title": action["title"],
                "reason": (
                    "This equipment-planning step is not shown because "
                    "you have not confirmed that you can approve changes. "
                    "The next step above focuses on that first."
                )
            })
            continue

        if allowed_control is not None:
            reason = control_reasons.get(
                equipment_control,
                "Confirm who can approve changes before planning equipment work."
            )
        else:
            reason = general_reasons.get(
                change_level,
                "This step matches your selected concern and type of change."
            )

        matches.append({
            "id": action["id"],
            "title": action["title"],
            "description": action["description"],
            "reason": reason,
            "requires_equipment_control": (
                action["requires_equipment_control"]
            )
        })

    return matches, excluded



st.title("Energy Path Long Island")
st.write(
    "Choose a home-energy concern and the kind of help you want."
)

with st.form("energy_plan_form"):
    st.subheader("What would you like to tackle?")

    main_concern = st.selectbox(
        "Your main concern",
        [
            "Drafts or rooms that feel too hot or cold",
            "Heating or cooling",
            "Lighting and electronics",
            "Water use or water heating",
            "Appliances or high electricity use"
        ],
        index=None,
        placeholder="Choose a concern"
    )

    change_level = st.radio(
        "What kind of next step are you looking for?",
        [
            "Easy changes I can do now",
            "Programs or incentives to explore",
            "Bigger long-term updates"
        ]
    )

    st.caption(
        "Local-resource coverage is limited."
        "Eligibilty screening is not available yet."
    )

    st.divider()
    st.subheader("A little about your home")

    home_status = st.radio(
        "Do you rent or own?",
        ["Rent", "Own"],
        horizontal=True
    )

    equipment_control = st.selectbox(
        "Can you approve changes to installed equipment?",
        [
            "Yes, I can authorize equipment changes",
            "Only with landlord or property-manager approval",
            "No, I cannot authorize equipment changes",
            "I am not sure"
        ],
        index=None,
        placeholder="Choose an answer"
    )

    st.caption(
        "Think about heating, cooling, water-heating equipment, "
        "and appliances involved in your concern."
    )

    with st.expander("Optional details—not used in matching yet"):
        st.caption(
            "These answers do not change your recommendations "
            "in the current prototype."
        )

        main_goal = st.radio(
            "Your main energy goal",
            [
                "Lower my energy bill",
                "Make my home more comfortable",
                "Use less energy",
                "Learn about bigger home upgrades"
            ],
            index=None
        )

        heating_source = st.selectbox(
            "Your primary heating source",
            [
                "Electric heat",
                "Oil",
                "Natural Gas",
                "Heat pump",
                "I am not sure"
            ],
            index=None,
            placeholder="Choose a heating source"
        )

    build_plan = st.form_submit_button(
        "Show My Next Step",
        type="primary"
    )

if not build_plan:
    st.stop()

if main_concern is None:
    st.warning("Choose your main concern first.")
    st.stop()

if equipment_control is None:
    st.warning(
        "Choose an equipment-control answer. "
        "If you are unsure, select 'I am not sure'."
    )
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
            action["id"] == "equipment_permission_next_step"
        )

    with st.container(border=True):
            if len(matches) > 1:
                st.caption(f"STEP {number}")

            if is_authority_summary:
                if equipment_control == (
                    "Only with landlord or property-manager approval"
                ):
                    card_title = "Talk to your landlord or property manager"
                elif equipment_control == (
                    "No, I cannot authorize equipment changes"
                ):
                    card_title = "Bring the problem to someone who can approve changes"
                else:
                    card_title = "Find out who can approve changes"

                st.subheader(card_title)
                st.write(
                    "A short description of the problem gives you "
                    "a starting point for that conversation."
                )

                st.markdown("#### Before the conversation")

                if main_concern == "Heating or cooling":
                    st.markdown(
                        "- Note which rooms are affected.\n"
                        "- Write down when the problem happens.\n"
                        "- Identify the heating or cooling equipment, "
                        "if you know it."
                    )
                elif main_concern == "Water use or water heating":
                    st.markdown(
                        "- Describe the water-use or hot-water issue.\n"
                        "- Note where and when it happens.\n"
                        "- Identify the fixture or equipment involved, "
                        "if you know it."
                    )
                else:
                    st.markdown(
                        "- List the appliances you are concerned about.\n"
                        "- Describe the problem or electricity-use concern.\n"
                        "- Note which appliances belong to you "
                        "and which belong to the property owner."
                    )

                if home_status == "Rent":
                    st.write(
                        "Share these details with your landlord or "
                        "property manager. If someone else handles "
                        "equipment decisions, ask who to contact."
                    )
                else:
                    st.write(
                        "Share these details with the person responsible "
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
        "See local resources below when a matching program is available."
        "Eligibility screening is not available yet."
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
    programs_path = Path(__file__).resolve().parent / "programs.json"

try:
    with programs_path.open("r", encoding="utf-8") as file:
        programs = json.load(file)
except (OSError, json.JSONDecodeError):
    st.warning(
        "Local resources could not be loaded. "
        "Your action recommendations are still available."
    )
else:
    matching_programs = [
        program
        for program in programs
        if main_concern in program["concerns"]
        and change_level in program["change_levels"]
    ]

    if matching_programs:
        st.divider()
        st.subheader("Local resources")
        st.write(
            "These resources relate to your concern. "
            "A resource match does not establish rebate eligibility."
        )

        for program in matching_programs:
            with st.container(border=True):
                st.caption(program["provider"])
                st.subheader(program["name"])
                st.write(program["summary"])

                st.markdown("#### Where to start")
                st.write(program["next_step"])

                st.info(program["eligibility_note"])

                with st.expander("Requirements to review"):
                    st.caption(
                        "These are selected requirements, "
                        "not a complete eligibility checklist."
                    )

                    for requirement in program["verified_requirements"]:
                        st.write(
                            f"- {requirement['description']}"
                        )

                st.link_button(
                    "View Official Program Details",
                    program["source_url"]
                )

                st.caption(
                    "Source checked: "
                    f"{program['source_checked_on']}"
                )


st.caption(
    "Early prototype: recommendations currently use your main concern, "
    "change preference, and equipment-control answer. Your goal and "
    "heating source do not affect the results yet."
)
