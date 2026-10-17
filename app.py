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
           .ep-hero .ep-title {
            margin: 0 !important;
            padding: 0 !important;
            text-align: center !important;
        }

        .ep-hero .ep-location {
            margin: 0.35rem 0 0.55rem !important;
            padding: 0 !important;
            letter-spacing: 0.18em;
            text-align: center !important;
        }

        .ep-hero .ep-tagline {
            display: block;
            width: 100%;
            max-width: 650px;
            margin: 0 auto 0.8rem !important;
            padding: 0 !important;
            text-align: center !important;
        }

        .ep-hero .ep-intro {
            display: block;
            width: 100%;
            max-width: 640px;
            margin: 0 auto !important;
            padding: 0 !important;
            text-align: center !important;
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
    st.subheader("Build your energy action plan")
    st.caption(
        "Choose your concern and tell us about your home. "
        "We will use your answers to suggest a practical next step."
    )

    concern_col, home_col = st.columns(2)

    with concern_col:
        with st.container(border=True):
            st.subheader("1. Your priorities")
            st.caption("What would you like to tackle?")

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

    with home_col:
        with st.container(border=True):
            st.subheader("2. Your home")
            st.caption("Help us suggest appropriate next steps.")

            home_status = st.radio(
                "Do you rent or own?",
                ["Rent", "Own"],
                horizontal=True
            )

            dwelling_units = st.selectbox(
                "How many homes or apartments are in your building?",
                [
                    "1–4",
                    "5 or more",
                    "I am not sure"
                ],
                index=None,
                placeholder="Choose a building size",
                help=(
                    "Count your own home too. Count whole homes, "
                    "not rooms or people. "
                    "A single-family house—even with 5 bedrooms—"
                    "counts as 1. A building with 6 separate "
                    "apartments counts as 6."
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
                "Think about heating, cooling, water-heating "
                "equipment, and appliances involved in your concern."
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
        "Build My Energy Action Plan",
        type="primary",
        use_container_width=True
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
    st.markdown(
        """
        <section style="
            background: linear-gradient(135deg, #DDECE2, #E7F2EC);
            border: 1px solid #C7DDD2;
            border-left: 6px solid #176B68;
            border-radius: 18px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        ">
            <p style="
                color: #176B68;
                font-size: 0.8rem;
                font-weight: 750;
                letter-spacing: 0.14em;
                margin: 0 0 0.5rem;
            ">ENERGY PATH · LONG ISLAND</p>
            <h2 style="
                color: #164B40;
                font-size: clamp(1.6rem, 3vw, 2.2rem);
                line-height: 1.2;
                margin: 0 0 0.6rem;
                padding: 0;
            ">Your Energy Action Plan</h2>
            <p style="
                color: #38574F;
                font-size: 1rem;
                line-height: 1.6;
                margin: 0;
            ">
                A starting point based on your concern,
                preferred next step, and equipment-change permissions.
            </p>
        </section>
        """,
        unsafe_allow_html=True
    )

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
step_labels = {
    "Easy changes I can do now": "Easy changes",
    "Programs or incentives to explore": "Programs & incentives",
    "Bigger long-term updates": "Long-term updates"
}

permission_labels = {
    "Yes, I can authorize equipment changes": (
        "You can approve changes"
    ),
    "Only with landlord or property-manager approval": (
        "Landlord or manager approval needed"
    ),
    "No, I cannot authorize equipment changes": (
        "Someone else must approve changes"
    ),
    "I am not sure": (
        "Approval authority uncertain"
    )
}

with st.expander("Review your answers"):
    st.write(f"Concern: {main_concern}")
    st.write(
        f"Next-step preference: "
        f"{step_labels.get(change_level, change_level)}"
    )
    st.write(
        f"Equipment permissions: "
        f"{permission_labels.get(equipment_control, equipment_control)}"
    )

st.subheader("Start Here")





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

from html import escape

st.markdown(
    """
    <style>
    .ep-action-title {
        color: #164B40;
        font-family: system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
        font-size: clamp(1.35rem, 2.5vw, 1.8rem);
        font-weight: 750;
        line-height: 1.25;
        margin: 0.35rem 0 0.8rem;
        padding: 0;
    }

    .ep-action-panel {
        background: #F2F8F5;
        border-left: 4px solid #176B68;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.15rem;
        margin: 0 0 0.8rem;
    }

    .ep-action-panel p,
    .ep-action-panel li {
        color: #183247;
        font-size: 1rem;
        line-height: 1.65;
    }

    .ep-action-panel p {
        max-width: 760px;
        margin: 0;
    }

    .ep-action-panel ul {
        margin: 0;
        padding-left: 1.25rem;
        max-width: 760px;
    }

    .ep-action-label {
        display: inline-block;
        background: #F4C95D;
        color: #183247;
        font-size: 0.8rem;
        font-weight: 750;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        margin-bottom: 0.65rem;
    }
    </style>
    """,
    unsafe_allow_html=True
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
                    card_title = "Find the person who can approve changes"

                else:
                    card_title = "Check who can approve changes"

                st.markdown(
                    f'<h3 class="ep-action-title">'
                    f'{escape(card_title)}</h3>',
                    unsafe_allow_html=True
                )

                if main_concern == "Heating or cooling":
                    conversation_items = [
                        "Note which rooms are affected.",
                        "Write down when the problem happens.",
                        "Identify the heating or cooling equipment, "
                        "if you know it."
                    ]

                elif main_concern == "Water use or water heating":
                    conversation_items = [
                        "Describe the water-use or hot-water issue.",
                        "Note where and when it happens.",
                        "Identify the fixture or equipment involved, "
                        "if you know it."
                    ]

                else:
                    conversation_items = [
                        "List the appliances you are concerned about.",
                        "Describe the problem or electricity-use concern.",
                        "Note which appliances belong to you "
                        "and which belong to the property owner."
                    ]

                items_html = "".join(
                    f"<li>{escape(item)}</li>"
                    for item in conversation_items
                )

                st.markdown(
                    f"""
                    <div class="ep-action-panel">
                        <span class="ep-action-label">
                            BEFORE YOU TALK
                        </span>
                        <ul>{items_html}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if home_status == "Rent":
                    st.write(
                        "Share your notes with your landlord or property "
                        "manager. Ask who handles equipment decisions "
                        "if you are unsure."
                    )

                else:
                    st.write(
                        "Share your notes with the person responsible "
                        "for approving equipment changes."
                    )

            else:
                card_title = action["title"]
                card_description = action["description"]

                if (
                    main_concern
                    == "Drafts or rooms that feel too hot or cold"
                    and change_level == "Easy changes I can do now"
                    and card_title
                    == "Identify where comfort problems occur"
                ):
                    card_title = "Find your comfort trouble spots"
                    card_description = (
                        "Note which rooms feel too hot or cold, "
                        "when it happens, and any noticeable drafts "
                        "around windows or doors. Record what you "
                        "find before deciding on property changes."
                    )

                st.markdown(
                    f"""
                    <h3 class="ep-action-title">
                        {escape(card_title)}
                    </h3>
                    <div class="ep-action-panel">
                        <span class="ep-action-label">
                            YOUR FIRST MOVE
                        </span>
                        <p>{escape(card_description)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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
            "Explore Resources for your next step below "
            "for matching resources or current coverage."
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

st.markdown(
    """
    <style>
    .ep-resource-provider {
        display: inline-block;
        background: #EAF4FC;
        color: #183247;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 650;
        margin: 0.25rem 0 0.8rem;
    }

    .ep-resource-heading {
        color: #164B40;
        font-family: system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
        font-size: clamp(1.35rem, 2.5vw, 1.8rem);
        font-weight: 750;
        line-height: 1.25;
        margin: 0 0 0.6rem;
        padding: 0;
    }

    .ep-resource-summary {
        color: #38524B;
        font-size: 1.02rem;
        line-height: 1.65;
        max-width: 760px;
        margin: 0 0 1rem;
    }

    .ep-resource-step {
        background: #F2F8F5;
        border-left: 4px solid #176B68;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.15rem;
        margin: 0.5rem 0 1rem;
    }

    .ep-resource-step-label {
        display: inline-block;
        background: #F4C95D;
        color: #183247;
        font-size: 0.8rem;
        font-weight: 750;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        margin-bottom: 0.6rem;
    }

    .ep-resource-step p {
        color: #183247;
        font-size: 1rem;
        line-height: 1.65;
        max-width: 760px;
        margin: 0;
    }

    .ep-resource-note {
        color: #38524B;
        font-size: 0.92rem;
        line-height: 1.6;
        max-width: 760px;
        margin: 0.3rem 0 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

from html import escape

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

    st.subheader("Resources for your next step")
    st.caption(
        "Explore the guidance below. "
        "A match does not confirm program eligibility."
    )

    if matching_programs:
        for program in matching_programs:
            is_heat_pump = (
                program["id"] == "pseg_li_home_comfort_heat_pumps"
            )

            provider_text = escape(str(program["provider"]))
            title_text = escape(str(program["name"]))
            summary_text = escape(str(program["summary"]))
            next_step_text = escape(str(program["next_step"]))

            with st.container(border=True):
                st.markdown(
                    f"""
                    <span class="ep-resource-provider">
                        {provider_text}
                    </span>
                    <h3 class="ep-resource-heading">
                        {title_text}
                    </h3>
                    <p class="ep-resource-summary">
                        {summary_text}
                    </p>
                    <div class="ep-resource-step">
                        <span class="ep-resource-step-label">
                            YOUR FIRST MOVE
                        </span>
                        <p>{next_step_text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if is_heat_pump:
                    st.markdown("#### Check your building category")

                    if dwelling_units == "1–4":
                        st.success(
                            "Your answer places your building "
                            "in the 1–4-unit category."
                        )
                        st.caption(
                            "Building size only—not an eligibility "
                            "decision. Project, equipment, contractor, "
                            "and other requirements still need review."
                        )

                    elif dwelling_units == "5 or more":
                        st.info(
                            "Your answer places your building "
                            "in the separate multifamily category."
                        )
                        st.caption(
                            "The 1–4-unit screening path does not apply. "
                            "Other rebates may be available; review "
                            "the multifamily requirements on the "
                            "official page."
                        )

                    else:
                        st.warning(
                            "Confirm the number of homes or apartments "
                            "in your building to identify the category "
                            "to review."
                        )
                        st.caption(
                            "Ask the owner or manager if needed. "
                            "Count separate homes or apartments, "
                            "not bedrooms."
                        )

                    heat_pump_permission_notes = {
                        "Yes, I can authorize equipment changes": (
                            "You reported that you can approve equipment "
                            "changes. Review the program requirements "
                            "before planning a purchase."
                        ),
                        "Only with landlord or property-manager approval": (
                            "Discuss proposed equipment changes with "
                            "your landlord or property manager before "
                            "moving forward."
                        ),
                        "No, I cannot authorize equipment changes": (
                            "Identify who can approve equipment changes "
                            "before planning an upgrade."
                        ),
                        "I am not sure": (
                            "Confirm who can approve equipment changes "
                            "before planning an upgrade."
                        )
                    }

                    permission_note = (
                        heat_pump_permission_notes.get(
                            equipment_control,
                            "Confirm who can approve equipment changes "
                            "before planning an upgrade."
                        )
                    )

                    st.markdown(
                        f"""
                        <p class="ep-resource-note">
                            {escape(permission_note)}
                            Building category and equipment permission
                            are separate checks. Neither establishes
                            rebate eligibility.
                        </p>
                        """,
                        unsafe_allow_html=True
                    )

                else:
                    eligibility_text = escape(
                        str(program["eligibility_note"])
                    )

                    st.markdown(
                        f"""
                        <p class="ep-resource-note">
                            {eligibility_text}
                        </p>
                        """,
                        unsafe_allow_html=True
                    )

                button_label = (
                    "Explore the program ↗"
                    if is_heat_pump
                    else "Open official resource ↗"
                )

                st.link_button(
                    button_label,
                    program["source_url"],
                    type="primary",
                    use_container_width=False
                )

                with st.expander("Source details & requirements"):
                    st.write(f"Provider: {program['provider']}")
                    st.caption(
                        "Source checked: "
                        f"{program['source_checked_on']}"
                    )

                    if program["verified_requirements"]:
                        st.write("Requirements to review")
                        st.caption(
                            "Selected requirements—not a complete "
                            "eligibility checklist."
                        )

                        for requirement in program["verified_requirements"]:
                            st.write(
                                f"- {requirement['description']}"
                            )

    else:
        st.info(
            "We do not have a resource matching both your concern "
            "and preferred next step yet."
        )
        st.caption(
            "Other guidance, programs, or incentives may still "
            "be available."
        )

st.caption(
    "About your results: recommendations use your concern, "
    "next-step preference, and equipment-control answer. "
    "Some resources also display a building-size check. "
    "Your optional goal and heating source do not affect results yet."
)


