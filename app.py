import json
from pathlib import Path

import streamlit as st
st.set_page_config(
    page_title="Energy Path",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)
if "screen" not in st.session_state:
    st.session_state.screen = "home"
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
            "You chose to explore a larger update. "
            "This step helps you compare options before "
            "committing to purchases or property changes."
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


if st.session_state.screen == "home":

    st.markdown(
        """
        <style>
        .ep-hero {
            text-align: center;
            padding: 3rem 1.5rem 2.2rem;
            margin: 0 0 1.2rem;
            background: linear-gradient(
                135deg,
                #DDECE2 0%,
                #E7F2EC 55%,
                #E5EFF4 100%
            );
            border: 1px solid #C7DDD2;
            border-radius: 24px;
        }

        .ep-title {
            color: #164B40;
            font-family: system-ui, -apple-system, BlinkMacSystemFont,
                         "Segoe UI", sans-serif;
            font-size: clamp(3rem, 7vw, 5.5rem);
            font-weight: 850;
            letter-spacing: -0.055em;
            line-height: 1.08;
            margin: 0;
        }

        .ep-location {
            color: #176B68;
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.28em;
            margin: 0.9rem 0 1.5rem;
        }

        .ep-tagline {
            color: #183247;
            font-size: clamp(1.2rem, 2.5vw, 1.65rem);
            font-weight: 650;
            line-height: 1.4;
            max-width: 650px;
            margin: 0 auto 0.9rem;
        }

        .ep-intro {
            color: #38574F;
            font-size: 1.05rem;
            line-height: 1.7;
            max-width: 640px;
            margin: 0 auto;
        }

        .ep-section-label {
            text-align: center;
            color: #176B68;
            font-size: 0.8rem;
            font-weight: 750;
            letter-spacing: 0.16em;
            margin: 2.5rem 0 1rem;
        }

        .ep-feature {
            background: #FFFFFF;
            border: 1px solid #CDDCD6;
            border-top: 5px solid #176B68;
            border-radius: 16px;
            padding: 1.5rem;
            min-height: 215px;
            box-sizing: border-box;
            margin-bottom: 1rem;
        }

        .ep-feature-number {
            color: #176B68;
            font-size: 0.85rem;
            font-weight: 750;
            letter-spacing: 0.1em;
            margin-bottom: 0.8rem;
        }

        .ep-feature h3 {
            color: #164B40;
            font-size: 1.2rem;
            font-weight: 750;
            line-height: 1.35;
            margin: 0 0 0.7rem;
            padding: 0;
        }

        .ep-feature p {
            color: #38524B;
            font-size: 1rem;
            line-height: 1.65;
            margin: 0;
        }

        .ep-about {
            background: #E1EDE5;
            border: 1px solid #C7DDD2;
            border-radius: 18px;
            padding: 1.8rem;
            margin: 1rem 0 1.5rem;
            text-align: center;
        }

        .ep-about h2 {
            color: #164B40;
            font-size: 1.5rem;
            margin: 0 0 0.8rem;
            padding: 0;
        }

        .ep-about p {
            color: #38524B;
            font-size: 1rem;
            line-height: 1.75;
            max-width: 760px;
            margin: 0 auto;
        }

        @media (max-width: 640px) {
            .ep-hero {
                padding: 2rem 1rem;
            }

            .ep-feature {
                min-height: auto;
            }
        }
        </style>

        <section class="ep-hero">
            <h1 class="ep-title">Energy Path</h1>
            <div class="ep-location">LONG ISLAND</div>
            <p class="ep-tagline">
                Your home-energy concern.<br>
                A clearer next step.
            </p>
            <p class="ep-intro">
                Explore practical guidance and official resources
                for your home, whether you rent or own.
            </p>
        </section>
        """,
        unsafe_allow_html=True
    )

    button_left, button_center, button_right = st.columns([1, 2, 1])

    with button_center:
        if st.button(
            "Find My Next Step",
            type="primary",
            use_container_width=True
        ):
            st.session_state.screen = "questionnaire"
            st.rerun()

    st.markdown(
        '<div class="ep-section-label">A PRACTICAL PLACE TO BEGIN</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <section class="ep-feature">
                <div class="ep-feature-number">01 / YOUR CONCERN</div>
                <h3>Understand your options</h3>
                <p>
                    Start with what matters to you—from drafts
                    and hot water to lighting and electricity use.
                </p>
            </section>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <section class="ep-feature">
                <div class="ep-feature-number">02 / YOUR SITUATION</div>
                <h3>Plan around permissions</h3>
                <p>
                    Explore next steps that account for whether
                    you can approve equipment changes or need
                    someone else's approval.
                </p>
            </section>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <section class="ep-feature">
                <div class="ep-feature-number">03 / YOUR NEXT STEP</div>
                <h3>Find helpful resources</h3>
                <p>
                    Get a practical starting action and explore
                    available official guidance and program pages.
                </p>
            </section>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <section class="ep-about">
            <h2>Why Energy Path?</h2>
            <p>
                Knowing where to begin can be the hardest part.
                Energy Path brings a starting action and relevant
                resources into one place, with guidance for renters
                and homeowners in Nassau and Suffolk counties.
            </p>
        </section>
        """,
        unsafe_allow_html=True
    )

    with st.expander("About this app"):
        st.write(
            "Energy Path is a student-built prototype for exploring "
            "home-energy next steps on Long Island. Recommendations "
            "use your main concern, preferred type of change, and "
            "equipment-change permission."
        )
        st.write(
            "Resource coverage is limited. The app does not establish "
            "rebate eligibility, provide a home-energy assessment, "
            "or guarantee energy or cost savings."
        )

    st.stop()


st.title("Energy Path")
st.subheader("A home-energy resource navigator for Long Island residents")
st.write(
    "Answer a few questions to find practical next steps and "
    "relevant local resources for your home."
)
if st.button("← Back to Home", type="secondary"):
    st.session_state.screen = "home"
    st.rerun()
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
        "Our resource list is still growing. "
        "Matching a resource does not confirm that you qualify."
    )

    st.divider()
    st.subheader("A little about your home")

    home_status = st.radio(
        "Do you rent or own?",
        ["Rent", "Own"],
        horizontal=True
    )
    dwelling_units = st.selectbox(
        "How many homes or apartments are in your building? Count your own home too.",
        [
            "1–4",
            "5 or more",
            "I am not sure"
        ],
        index=None,
        placeholder="Choose a building size",
        help=(
            "Count whole homes, not rooms or people. "
            "A single-family house—even with 5 bedrooms—counts as 1. "
            "A building with 6 separate apartments counts as 6."
        )
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

result_col1, result_col2 = st.columns([4, 1])

with result_col1:
    st.caption("YOUR PERSONALIZED PLAN")
    st.header("Your next step")
    concern_intros = {
        "Drafts or rooms that feel too hot or cold": (
            "Start here for drafts or uneven room temperatures."
        ),
        "Heating or cooling": (
            "Start here for your heating or cooling concern."
        ),
        "Lighting and electronics": (
            "Start here for lighting and electronics."
        ),
        "Water use or water heating": (
            "Start here for your water-use or hot-water concern."
        ),
        "Appliances or high electricity use": (
            "Start here for appliances or high electricity use."
        ),
    }

    st.write(
        concern_intros.get(
            main_concern,
            "Here is a practical place to begin."
        )
    )

with result_col2:
    if st.button(
        "Start over", 
        type="secondary",
        use_container_width=True
    ):
        st.session_state.screen = "home"
        st.rerun()
permission_notes = {
    "Yes, I can authorize equipment changes": (
        "You selected that you can approve equipment changes. "
        "Upgrade suggestions are options to investigate, not purchase advice."
    ),
    "Only with landlord or property-manager approval": (
        "This plan reflects your selection that equipment changes "
        "need landlord or property-manager approval."
    ),
    "No, I cannot authorize equipment changes": (
        "This plan reflects your selection that you cannot "
        "approve equipment changes."
    ),
    "I am not sure": (
        "You selected that equipment-change authority is uncertain. "
        "Confirm who can approve changes before planning an upgrade."
    ),
}




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
    if change_level == "Programs or incentives to explore":
        st.info(
            "See Helpful resources section below for matching resources "
            "or information about current coverage."
        )
    else:
        st.info(
            "No action in the current catalog matches your answers. "
            "This does not mean you have no options."
        )

if excluded:
    with st.expander("Why some equipment options are not recommended"):
        for action in excluded:
            st.markdown(f"**{action['title']}**")

            if equipment_control == (
                "Only with landlord or property-manager approval"
            ):
                st.write(
                    "This option requires approval from your landlord "
                    "or property manager. Start with the conversation above."
                )
            elif equipment_control == (
                "No, I cannot authorize equipment changes"
            ):
                st.write(
                    "You selected that you cannot approve equipment changes. "
                    "Identify who can approve them before planning an upgrade."
                )
            elif equipment_control == "I am not sure":
                st.write(
                    "You have not confirmed who can approve equipment changes. "
                    "Clarify that before planning an upgrade."
                )
            else:
                st.write(action["reason"])

permission_notes = {
    "Yes, I can authorize equipment changes": (
        "You selected that you can approve equipment changes. "
        "Upgrade suggestions are options to investigate, not purchase advice."
    ),
    "Only with landlord or property-manager approval": (
        "This plan reflects your selection that equipment changes "
        "need landlord or property-manager approval."
    ),
    "No, I cannot authorize equipment changes": (
        "This plan reflects your selection that you cannot "
        "approve equipment changes."
    ),
    "I am not sure": (
        "You selected that equipment-change authority is uncertain. "
        "Confirm who can approve changes before planning an upgrade."
    ),
}

st.caption(
    permission_notes.get(
        equipment_control,
        "Confirm who can approve equipment changes before planning an upgrade."
    )
)


programs_path = Path(__file__).resolve().parent / "programs.json"

try:
    with programs_path.open("r", encoding="utf-8") as file:
        programs = json.load(file)
except (OSError, json.JSONDecodeError):
    st.warning(
        "Helpful resources could not be loaded. "
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
        st.subheader("Helpful Resources")
        st.write(
            "Explore resources for your concern and preferred next step. "
            "A resource match does not establish rebate eligibility."
        )

        for program in matching_programs:
            with st.container(border=True):
                st.caption(program["provider"])
                st.subheader(program["name"])
                st.write(program["summary"])

                st.markdown("**Where to start**")
                st.write(program["next_step"])

                if program["id"] == "pseg_li_home_comfort_heat_pumps":
                    st.markdown("**Building-category check**")

                    if dwelling_units == "1–4":
                        st.success(
                            "Your building size fits the 1–4-unit "
                            "category we are checking."
                        )
                        st.caption(
                            "This checks building size only. "
                            "The project, equipment, contractor, "
                            "and other requirements still need review."
                        )

                    elif dwelling_units == "5 or more":
                        st.info(
                            "Your building falls in the separate "
                            "multifamily category. The 1–4-unit "
                            "screening path does not apply."
                        )
                        st.caption(
                            "This does not mean no rebate is available. "
                            "Review the multifamily requirements "
                            "on the official program page."
                        )

                    else:
                        st.warning(
                            "We need your building's unit count "
                            "to determine which category to review."
                        )
                        st.caption(
                            "Ask the property owner or manager if "
                            "you are unsure. A unit means a separate "
                            "home or apartment—not a bedroom."
                        )

                    st.caption(
                        "Rebate eligibility has not been established."
                    )
                    st.markdown("**Equipment-change permission**")

                    if equipment_control == (
                        "Yes, I can authorize equipment changes"
                    ):
                        st.info(
                            "You reported that you can approve equipment "
                            "changes. This is a planning answer, not "
                            "verification of rebate eligibility."
                        )

                    elif equipment_control == (
                        "Only with landlord or property-manager approval"
                    ):
                        st.info(
                            "You reported that equipment changes require "
                            "landlord or property-manager approval. "
                            "Your next planning step is to discuss the "
                            "proposed changes with them."
                        )

                    elif equipment_control == (
                        "No, I cannot authorize equipment changes"
                    ):
                        st.info(
                            "You reported that you cannot approve "
                            "equipment changes. Identify who can "
                            "authorize them before moving forward "
                            "with equipment planning."
                        )

                    else:
                        st.info(
                            "Permission to approve equipment changes "
                            "is unknown. Confirm who can authorize "
                            "changes before moving forward "
                            "with equipment planning."
                        )

                    st.caption(
                        "This note uses your permission answer only. "
                        "It does not change the building-category result "
                        "or establish rebate eligibility."
                    )


                else:
                    st.info(program["eligibility_note"])


                if program["verified_requirements"]:
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
                    "View Official Resource",
                    program["source_url"],
                    type="primary"
                )

                st.caption(
                    "Source checked: "
                    f"{program['source_checked_on']}"
                )

    else:
        st.divider()
        st.subheader("Helpful Resources")
        st.info(
            "No resource in the current catalog matches both "
            "your concern and preferred next step."
        )
        st.caption(
            "Coverage is limited. Other relevant guidance, programs, "
            "or incentives may still be available."
        )

st.caption(
    "Early prototype: recommendations currently use your main concern, "
    "change preference, and equipment-control answer. Your goal and "
    "heating source do not affect the results yet."
)
