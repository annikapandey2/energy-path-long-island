import json
from html import escape
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Energy Path",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "screen" not in st.session_state:
    st.session_state.screen = "home"

ACTIONS_PATH = Path(__file__).resolve().parent / "actions.json"
PROGRAMS_PATH = Path(__file__).resolve().parent / "programs.json"


def reset_energy_plan():
    keys_to_clear = [
        "submitted_plan",
        "plan_main_concern",
        "plan_change_level",
        "plan_home_status",
        "plan_dwelling_units",
        "plan_equipment_control",
        "plan_main_goal",
        "plan_heating_source",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.session_state.screen = "home"


@st.cache_data
def load_json(path: Path):
    """Load JSON from path and cache the result."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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
        ),
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
        ),
    }

    for action in actions:
        if concern not in action["concerns"]:
            continue

        if change_level not in action["change_levels"]:
            continue

        allowed_control = action.get("allowed_equipment_control")

        if allowed_control is not None and equipment_control not in allowed_control:
            continue

        if action["requires_equipment_control"] and equipment_control != "Yes, I can authorize equipment changes":
            excluded.append(
                {
                    "id": action["id"],
                    "title": action["title"],
                    "reason": (
                        "This equipment-planning step is not shown because "
                        "you have not confirmed that you can approve changes. "
                        "The next step above focuses on that first."
                    ),
                }
            )
            continue

        if allowed_control is not None:
            reason = control_reasons.get(
                equipment_control,
                "Confirm who can approve changes before planning equipment work.",
            )
        else:
            reason = general_reasons.get(
                change_level,
                "This step matches your selected concern and type of change.",
            )

        matches.append(
            {
                "id": action["id"],
                "title": action["title"],
                "description": action["description"],
                "reason": reason,
                "requires_equipment_control": action["requires_equipment_control"],
            }
        )

    return matches, excluded


# --- Small UI helpers -----------------------------------------------------

def top_bar():
    st.markdown(
        """
        <style>
        .ep-topbar {
            display:flex;align-items:center;justify-content:space-between;padding:10px 18px;border-bottom:1px solid #e6eef0;margin-bottom:14px;background:linear-gradient(90deg,#ffffff,#f7fffb);}
        .ep-logo {font-weight:800;color:#164B40;font-size:1.1rem;display:flex;align-items:center;gap:10px}
        .ep-logo .leaf{font-size:1.2rem}
        .ep-top-actions a{color:#164B40;text-decoration:none;font-weight:600}
        </style>
        <div class="ep-topbar">
            <div class="ep-logo"><span class="leaf">🍃</span>Energy Path</div>
            <div class="ep-top-actions"><a href="https://github.com/annikapandey2/energy-path-long-island" target="_blank">Source ↗</a></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Renderers -------------------------------------------------------------

def render_home():
    st.markdown(
        """
        <style>
        .ep-hero {
            text-align: center;
            padding: 2.5rem 1.5rem;
            margin-bottom: 1.4rem;
            background: #EAF6F1;
            border: 2px solid #176B68;
            border-radius: 20px;
        }

        .ep-hero h1.ep-title {
            color: #083F36;
            font-family: system-ui, sans-serif;
            font-size: clamp(2.6rem, 5vw, 4rem) !important;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.1;
            margin: 0;
            padding: 0;
        }

        .ep-location {
            color: #176B68;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.24em;
            margin: 0.9rem 0;
        }

        .ep-hero .ep-tagline {
            color: #164B40;
            font-size: 1.2rem;
            line-height: 1.5;
            margin: 0 0 0.6rem;
        }

        .ep-hero .ep-intro {
            color: #38524B;
            font-size: 1rem;
            line-height: 1.6;
            max-width: 650px;
            margin: 0 auto;
            text-align: center;
        }

       .st-key-home_primary button,
        .st-key-home_secondary button {
            width: 100%;
            min-height: 150px;
            border-radius: 18px;
            padding: 1.5rem 1.2rem;
            transition:
                transform 160ms ease,
                box-shadow 160ms ease,
                background-color 160ms ease;
        }

        .st-key-home_primary button p,
        .st-key-home_secondary button p {
            font-family:
                "Segoe UI", system-ui, -apple-system,
                BlinkMacSystemFont, sans-serif;
            font-size: clamp(1.15rem, 2vw, 1.4rem);
            font-weight: 700;
            line-height: 1.35;
            letter-spacing: -0.02em;
            text-align: center;
        }

        .st-key-home_primary button {
            background: #176B68;
            color: #FFFFFF;
            border: 1px solid #125854;
            box-shadow: 0 6px 0 #104E4B,
                        0 10px 20px rgba(23, 107, 104, 0.16);
        }

        .st-key-home_secondary button {
            background: #EDF5FC;
            color: #164B40;
            border: 1px solid #BDD4E8;
            box-shadow: 0 6px 0 #C2D4E2,
                        0 10px 20px rgba(35, 75, 101, 0.10);
        }

        .st-key-home_primary button:hover {
            background: #125E5B;
            color: #FFFFFF;
            border-color: #104E4B;
            transform: translateY(-2px);
            box-shadow: 0 8px 0 #104E4B,
                        0 14px 24px rgba(23, 107, 104, 0.19);
        }

        .st-key-home_secondary button:hover {
            background: #E3EFF9;
            color: #164B40;
            border-color: #9BBFD9;
            transform: translateY(-2px);
            box-shadow: 0 8px 0 #C2D4E2,
                        0 14px 24px rgba(35, 75, 101, 0.14);
        }

        .st-key-home_primary button:active,
        .st-key-home_secondary button:active {
            transform: translateY(2px);
            box-shadow: 0 2px 0 rgba(16, 78, 75, 0.4);
        }

        .ep-choice-caption {
            color: #38524B;
            text-align: center;
            font-size: 0.9rem;
            line-height: 1.5;
            margin: 0.9rem 0 0;
        }



      

        .ep-button-note {
            color: #526B64;
            text-align: center;
            font-size: 0.88rem;
            line-height: 1.5;
            max-width: 600px;
            margin: 0.8rem auto 0;
        }

        .ep-section-label {
            text-align: center;
            color: #176B68;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            margin: 2rem 0 1rem;
        }

        .ep-feature {
            border: 1px solid #B8D6CC;
            border-radius: 14px;
            padding: 1.4rem;
            min-height: 210px;
        }

        .ep-feature-number {
            color: #176B68;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .ep-feature h3 {
            color: #164B40;
            font-size: 1.25rem;
            line-height: 1.35;
            margin: 0 0 0.7rem;
            padding: 0;
        }

        .ep-feature p {
            color: #264D47;
            line-height: 1.6;
            margin: 0;
        }

        .ep-feature-options {
            background: #EDF5FC;
            border-color: #BDD4E8;
        }

        .ep-feature-permissions {
            background: #EAF6F1;
            border-color: #B8D6C8;
        }

        .ep-feature-resources {
            background: #E8F5F5;
            border-color: #ACD3D3;
        }

        .ep-about {
            background: #F3F8F6;
            border: 1px solid #C8DDD5;
            border-left: 4px solid #176B68;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1.5rem 0 1rem;
        }

        .ep-about .ep-about-kicker {
            color: #176B68;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin: 0 0 0.5rem;
        }

        .ep-about h3 {
            color: #083F36;
            margin: 0 0 0.6rem;
            padding: 0;
        }

        .ep-about .ep-about-copy {
            color: #38524B;
            line-height: 1.7;
            margin: 0;
            max-width: 850px;
        }

        .st-key-home_about details {
            background: #FFFFFF;
            border: 1px solid #C8DDD5;
            border-radius: 12px;
        }

        .st-key-home_about summary {
            color: #164B40;
            padding: 0.8rem 1rem;
        }

        .st-key-home_about summary:hover {
            background: #F3F8F6;
            border-radius: 12px;
        }

        @media (max-width: 640px) {
            .ep-hero {
                padding: 2rem 1rem;
            }

            .ep-feature {
                min-height: auto;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .st-key-home_primary button,
            .st-key-home_secondary button {
                transition: none;
            }

            .st-key-home_primary button:hover,
            .st-key-home_secondary button:hover {
                transform: none;
            }
        }
        </style>

        <section class="ep-hero">
            <h1 class="ep-title">Energy Path</h1>
            <div class="ep-location">LONG ISLAND</div>
            <p class="ep-tagline">
                Your home-energy concern. A clearer next step.
            </p>
            <p class="ep-intro">
                Explore practical guidance and official resources
                for your home, whether you rent or own.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

  




left_space, button_area, right_space = st.columns([1, 2, 1])

    with button_area:
        primary_col, secondary_col = st.columns(2, gap="medium")

        with primary_col:
            with st.container(key="home_primary"):
                if st.button(
                    "Find My Next Step →",
                    key="home_find_next_step",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.screen = "questionnaire"
                    st.rerun()

            st.markdown(
                '<p class="ep-choice-caption">'
                'Get guidance for your home-energy concern.'
                '</p>',
                unsafe_allow_html=True,
            )

        with secondary_col:
            with st.container(key="home_secondary"):
                if st.button(
                    "Explore Upgrade Payback →",
                    key="home_open_payback",
                    use_container_width=True,
                ):
                    st.session_state.screen = "simulator"
                    st.rerun()

            st.markdown(
                '<p class="ep-choice-caption">'
                'Compare a project cost with assumed savings.'
                '</p>',
                unsafe_allow_html=True,
            )





    st.markdown(
        '<div class="ep-section-label">A PLACE TO BEGIN</div>',
        unsafe_allow_html=True,
    )

    features = [
        (
            "ep-feature-options",
            "01 / YOUR CONCERN",
            "Understand your options",
            "Start with what matters to you—from drafts and hot "
            "water to lighting and electricity use.",
        ),
        (
            "ep-feature-permissions",
            "02 / YOUR SITUATION",
            "Plan around permissions",
            "Explore next steps that account for whether you can "
            "approve equipment changes or need someone else's approval.",
        ),
        (
            "ep-feature-resources",
            "03 / YOUR NEXT STEP",
            "Find helpful resources",
            "Get a practical starting action and explore available "
            "official guidance and program pages.",
        ),
    ]

    for column, feature in zip(st.columns(3), features):
        css_class, label, title, description = feature

        with column:
            st.markdown(
                f'<div class="ep-feature {css_class}">'
                f'<div class="ep-feature-number">{escape(label)}</div>'
                f'<h3>{escape(title)}</h3>'
                f'<p>{escape(description)}</p>'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <section class="ep-about">
            <p class="ep-about-kicker">A CLEARER START</p>
            <h3>Why Energy Path?</h3>
            <p class="ep-about-copy">
                You have a home-energy concern—but knowing what
                to do next can be confusing. Energy Path brings
                together a practical starting action and relevant
                official resources, with guidance that accounts
                for who can approve equipment changes.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="home_about"):
        with st.expander("About Energy Path"):
            st.markdown("#### Built for a practical first step")
            st.write(
                "Energy Path is a student-built prototype for "
                "renters and homeowners in Nassau and Suffolk "
                "counties on Long Island."
            )
            st.write(
                "Answer a few questions to explore a starting "
                "action and relevant official resources. Or use "
                "the separate payback calculator to compare a "
                "project cost with assumed savings."
            )

            st.markdown("#### What to keep in mind")
            st.write(
                "Resource coverage is limited. Matches do not "
                "confirm rebate eligibility, replace a home-energy "
                "assessment, or guarantee energy or cost savings."
            )



def render_simulator():
    top_bar()
  
    st.title("Explore Upgrade Payback")
    if st.button("←Back to home", key="payback_back_home"):
        st.session_state.screen = "home"
        st.rerun()
    st.write("Explore how an upgrade's upfront cost compares with its assumed energy savings over time.")
    st.caption("Start with a guided example, or enter savings from your own project estimate.")

    mode = st.radio(
        "Choose your starting point",
        ["Explore an air-sealing + insulation example", "My own estimate"],
        key="payback_mode",
    )

    benchmark_mode = mode == "Explore an air-sealing + insulation example"

    if benchmark_mode:
        st.subheader("Air sealing + insulation")
        st.info("This example uses ENERGY STAR's estimated national average savings of 11% on total home-energy costs from combined air sealing and insulation. Actual savings vary by home.")
        st.markdown("[View the official ENERGY STAR methodology](https://www.energystar.gov/saveathome/seal_insulate/methodology)")

    else:
        st.info("Use a savings estimate from an assessment, contractor, or your own hypothetical scenario. Energy Path calculates payback from your inputs; it does not independently predict the savings.")

    with st.form("payback_scenario_form"):
        upfront_cost = st.number_input("Upfront project cost you would pay ($)", min_value=0.0, max_value=1000000.0, value=1500.0, step=50.0, format="%.2f", key="payback_project_cost", help=("Replace the example with your project estimate or quote. Do not subtract unconfirmed rebates or tax credits. In benchmark mode, the cost should cover the combined air-sealing and insulation work being explored."))

        if benchmark_mode:
            annual_energy_spending = st.number_input("Total annual home-energy spending ($/year)", min_value=0.0, max_value=1000000.0, value=3000.0, step=100.0, format="%.2f", key="payback_annual_energy_spending", help=("Add a full year of electricity and any natural gas, heating oil, propane, or other home-energy costs. Include each fuel once. Do not include water, internet, or vehicle fuel."))
            st.caption("Calculation: annual home-energy spending × 11% ÷ 12 = assumed average monthly savings.")
            monthly_savings = annual_energy_spending * 0.11 / 12
        else:
            monthly_savings = st.number_input("Assumed monthly savings ($)", min_value=0.0, max_value=100000.0, value=20.0, step=5.0, format="%.2f", key="payback_own_monthly_savings", help=("Enter your own estimate. This value is not supplied or verified by Energy Path."))

        years = st.slider("Years to explore", min_value=1, max_value=30, value=5, key="payback_horizon")
        submitted = st.form_submit_button("Run my scenario", type="primary")

    if submitted:
        st.session_state.payback_scenario = {"upfront_cost": float(upfront_cost), "monthly_savings": float(monthly_savings), "years": int(years), "mode": mode, "annual_energy_spending": float(annual_energy_spending) if benchmark_mode else None}

    scenario = st.session_state.get("payback_scenario")
    if scenario is None:
        st.caption("Enter your estimates, then select 'Run my scenario' to see the results.")
        return

    cost = scenario["upfront_cost"]
    savings = scenario["monthly_savings"]
    horizon_years = scenario["years"]

    total_months = horizon_years * 12
    annual_savings = savings * 12
    net_savings = savings * total_months - cost

    st.subheader("Your scenario results")
    result_mode = scenario.get("mode", "My own estimate")
    st.write(f"Scenario basis: {result_mode}")

    if result_mode == "Explore an air-sealing + insulation example":
        annual_spending = scenario["annual_energy_spending"]
        st.caption("Savings assumption: ENERGY STAR's 11% national modeled benchmark for combined air sealing and insulation, applied to " f"${annual_spending:,.2f} in annual home-energy spending.")
        st.markdown("[Benchmark source: ENERGY STAR](https://www.energystar.gov/saveathome/seal_insulate/methodology)")
    else:
        st.caption("Savings assumption: the monthly amount you entered—not an official benchmark.")

    st.caption("Results reflect your last submitted scenario: " f"${cost:,.2f} upfront, {savings:,.2f} saved per month, over {horizon_years} years. If you change the inputs, select 'Run my scenario' again.")

    if cost == 0:
        payback_months = 0.0
        payback_label = "No upfront cost"
    elif savings == 0:
        payback_months = None
        payback_label = "No payback"
    else:
        payback_months = cost / savings
        payback_label = f"{payback_months / 12:,.1f} years" if payback_months >= 12 else f"{payback_months:,.1f} months"

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Simple payback", payback_label)
    metric2.metric("Assumed annual savings", f"${annual_savings:,.2f}")
    metric3.metric(f"Net savings after {horizon_years} years", f"${net_savings:,.2f}")

    if cost == 0:
        st.info("You entered no upfront cost, so there is no initial investment to recover.")
    elif savings == 0:
        st.warning("With no monthly savings, this scenario does not recover its upfront cost.")
    elif payback_months > total_months:
        st.warning(
            f"This scenario does not recover its upfront cost within the selected {horizon_years} years. At the same monthly savings, simple payback would take {payback_months:,.1f} months ({payback_months/12:,.1f} years)."
        )
    else:
        st.success(f"Under these assumptions, savings recover the upfront cost after {payback_months:,.1f} months ({payback_months/12:,.1f} years).")

    months = list(range(total_months + 1))
    if payback_months is not None and 0 < payback_months <= total_months and payback_months not in months:
        months = sorted(months + [payback_months])

    balances = [savings * month - cost for month in months]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=balances, mode="lines", name="Savings minus upfront cost", line={"color": "#176B68", "width": 4}, hovertemplate=("Month %{x:.1f}<br>Net savings: $%{y:,.2f}<extra></extra>"),))
    fig.add_hline(y=0, line_dash="dash", line_color="#64748B", annotation_text="Break-even", annotation_position="top left")

    if payback_months is not None and 0 < payback_months <= total_months:
        fig.add_trace(go.Scatter(x=[payback_months], y=[0], mode="markers", name="Payback point", marker={"color": "#164B40", "size": 12}, hovertemplate=("Payback: %{x:.1f} months<extra></extra>")))

    fig.update_layout(title="How assumed savings compare with upfront cost", xaxis_title="Months after upgrade", yaxis_title="Cumulative savings minus upfront cost ($)", template="plotly_white", hovermode="x unified", showlegend=False, margin={"l": 20, "r": 20, "t": 70, "b": 30})
    fig.update_xaxes(range=[0, total_months])
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")

    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

    with st.expander("Sources, assumptions & calculation"):
        st.markdown("#### Where the numbers come from")
        if result_mode == "Explore an air-sealing + insulation example":
            st.write("The savings percentage comes from ENERGY STAR's published national modeled benchmark for combined air sealing and insulation. The source link appears above these results. Applying that percentage to your entered spending is an illustration, not a home-specific prediction.")
        else:
            st.write("The monthly savings figure is the amount you entered. Energy Path does not verify or independently predict that amount.")
        st.write("Project cost and the time period are your inputs. Starting dollar amounts are editable examples, not researched typical costs.")
        st.markdown("#### Formulas and limitations")
        st.write("Simple payback in months = upfront cost ÷ assumed monthly savings.")
        st.write("Net savings = assumed monthly savings × number of months − upfront cost.")
        st.write("The graph begins below zero when there is an upfront cost. It reaches break-even when cumulative savings equal that cost.")
        st.write("This simplified scenario assumes constant monthly savings. It excludes financing, maintenance, replacements, changing energy prices, inflation, and the time value of money. It does not check equipment life, rebate eligibility, or whether an upgrade is appropriate for your home.")


def render_questionnaire():
    st.markdown(
        """
        <style>
        .ep-survey-header {
            background: #EAF6F1;
            border: 1px solid #B8D6C8;
            border-left: 5px solid #176B68;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
        }

        .ep-survey-brand {
            color: #176B68;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            margin: 0 0 0.6rem;
        }

        .ep-survey-header h1 {
            color: #083F36;
            font-size: clamp(1.6rem, 3vw, 2.3rem) !important;
            line-height: 1.2;
            margin: 0 0 0.6rem;
            padding: 0;
        }

        .ep-survey-header p.ep-survey-description {
            color: #264D47;
            font-size: 1rem;
            line-height: 1.6;
            margin: 0;
            text-align: left;
        }

        .st-key-survey_priorities {
            background: #EDF5FC;
            border: 1px solid #BDD4E8 !important;
            border-radius: 14px;
            padding: 1.25rem;
        }

        .st-key-survey_home {
            background: #EAF6F1;
            border: 1px solid #B8D6C8 !important;
            border-radius: 14px;
            padding: 1.25rem;
        }

        .st-key-survey_priorities h3,
        .st-key-survey_home h3 {
            color: #164B40;
            font-size: 1.3rem !important;
            padding-top: 0;
        }

        .st-key-survey_priorities label p,
        .st-key-survey_home label p {
            color: #183F38;
        }
        </style>

        <section class="ep-survey-header">
            <p class="ep-survey-brand">ENERGY PATH · LONG ISLAND</p>
            <h1>Build your energy action plan</h1>
            <p class="ep-survey-description">
                Choose your home-energy concern and tell us about
                your situation. Find a practical starting action
                and relevant official resources.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Back to Home", type="secondary"):
        st.session_state.screen = "home"
        st.rerun()

    with st.form("energy_plan_form"):
        st.caption(
            "Start with your priorities, then tell us about "
            "your home and equipment-change permissions."
        )

        concern_col, home_col = st.columns(2)

        with concern_col:
            with st.container(
                border=True,
                key="survey_priorities",
            ):
                st.subheader("1. Your priorities")

                main_concern = st.selectbox(
                    "Your main concern",
                    [
                        "Drafts or rooms that feel too hot or cold",
                        "Heating or cooling",
                        "Lighting and electronics",
                        "Water use or water heating",
                        "Appliances or high electricity use",
                    ],
                    index=None,
                    placeholder="Choose a concern",
                    key="plan_main_concern",
                )

                change_level = st.radio(
                    "What kind of next step are you looking for?",
                    [
                        "Easy changes I can do now",
                        "Programs or incentives to explore",
                        "Bigger long-term updates",
                    ],
                    key="plan_change_level",
                )

                st.caption(
                    "Our resource list is still growing. "
                    "Matching a resource does not confirm "
                    "that you qualify."
                )

        with home_col:
            with st.container(
                border=True,
                key="survey_home",
            ):
                st.subheader("2. Your home")

                home_status = st.radio(
                    "Do you rent or own?",
                    ["Rent", "Own"],
                    horizontal=True,
                    key="plan_home_status",
                )

                dwelling_units = st.selectbox(
                    "How many homes or apartments are in your building?",
                    [
                        "1–4",
                        "5 or more",
                        "I am not sure",
                    ],
                    index=None,
                    placeholder="Choose a building size",
                    help=(
                        "Count your own home too. Count whole homes, "
                        "not rooms or people. A single-family house"
                        "—even with 5 bedrooms—counts as 1. "
                        "A building with 6 separate apartments "
                        "counts as 6."
                    ),
                    key="plan_dwelling_units",
                )

                equipment_control = st.selectbox(
                    "Can you approve changes to installed equipment?",
                    [
                        "Yes, I can authorize equipment changes",
                        "Only with landlord or property-manager approval",
                        "No, I cannot authorize equipment changes",
                        "I am not sure",
                    ],
                    index=None,
                    placeholder="Choose an answer",
                    key="plan_equipment_control",
                )

                st.caption(
                    "Think about heating, cooling, water-heating "
                    "equipment, and appliances involved in your concern."
                )

        build_plan = st.form_submit_button(
            "Build My Energy Action Plan",
            type="primary",
            use_container_width=True,
        )


    if build_plan:
        if main_concern is None:
            st.warning("Choose your main concern first.")
            st.stop()

        if equipment_control is None:
            st.warning("Choose an equipment-control answer. If you are unsure, select 'I am not sure'.")
            st.stop()

        st.session_state.submitted_plan = {
            "main_concern": main_concern,
            "change_level": change_level,
            "home_status": home_status,
            "dwelling_units": dwelling_units,
            "equipment_control": equipment_control,
        }

    submitted_plan = st.session_state.get("submitted_plan")
    if submitted_plan is None:
        return

    main_concern = submitted_plan["main_concern"]
    change_level = submitted_plan["change_level"]
    home_status = submitted_plan["home_status"]
    dwelling_units = submitted_plan["dwelling_units"]
    equipment_control = submitted_plan["equipment_control"]

    st.divider()

    result_col1, result_col2 = st.columns([4, 1])
    with result_col1:
        st.markdown(
            '<section style="background:#EAF6F1; '
            'border:1px solid #B8D6C8; '
            'border-left:6px solid #176B68; '
            'border-radius:16px; '
            'padding:1.4rem 1.6rem; '
            'margin-bottom:1rem;">'
            '<p style="color:#176B68; font-size:0.8rem; '
            'font-weight:700; letter-spacing:0.14em; '
            'margin:0 0 0.5rem;">'
            'ENERGY PATH · LONG ISLAND</p>'
            '<h2 style="color:#083F36; '
            'font-size:clamp(1.4rem, 2.4vw, 2rem); '
            'line-height:1.2; margin:0 0 0.4rem; padding:0;">'
            'Your Energy Action Plan</h2>'
            '<p style="color:#38574F; font-size:1rem; '
            'line-height:1.5; margin:0;">'
            'A starting point based on your concern, preferred '
            'next step, and equipment-change permissions.</p>'
            '</section>',
            unsafe_allow_html=True,
        )


    with result_col2:
        st.button("Start a New Plan", type="secondary", use_container_width=True, on_click=reset_energy_plan)

    # Load actions and match
    try:
        actions = load_json(ACTIONS_PATH)
    except Exception:
        st.error("The action catalog could not be loaded. Check that actions.json is beside app.py and contains valid JSON.")
        return

    matches, excluded = match_actions(actions=actions, concern=main_concern, change_level=change_level, equipment_control=equipment_control)


    st.markdown(
        """
        <style>
        .ep-action-title {
            color: #083F36;
            font-size: clamp(1.25rem, 2vw, 1.6rem) !important;
            font-weight: 750;
            line-height: 1.3;
            margin: 0 0 0.8rem;
            padding-top: 0;
        }

        .ep-action-panel {
            background: #EAF6F1;
            border: 1px solid #B8D6C8;
            border-left: 4px solid #176B68;
            border-radius: 12px;
            padding: 1.1rem 1.2rem;
            margin: 0 0 0.9rem;
            color: #264D47;
            line-height: 1.65;
            box-shadow: none;
        }

        .ep-action-panel p {
            margin: 0;
            color: #264D47;
            line-height: 1.65;
        }

        .ep-action-panel ul {
            margin: 0.3rem 0 0;
            padding-left: 1.3rem;
        }

        .ep-action-panel li {
            margin-bottom: 0.4rem;
        }

        .ep-action-label {
            display: inline-block;
            background: #D3EAE1;
            color: #164B40;
            font-size: 0.75rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            margin-bottom: 0.7rem;
        }

        .ep-resource-provider {
            display: inline-block;
            background: #EDF5FC;
            border: 1px solid #BDD4E8;
            color: #234B65;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 650;
        }

        .ep-resource-heading {
            color: #083F36;
            font-size: clamp(1.15rem, 2vw, 1.4rem) !important;
            font-weight: 750;
            line-height: 1.35;
            margin: 0.8rem 0 0.5rem;
            padding-top: 0;
        }

        .ep-resource-summary {
            color: #38524B;
            line-height: 1.65;
            margin: 0 0 1rem;
        }

        .ep-resource-step {
            background: #E8F5F5;
            border: 1px solid #ACD3D3;
            border-left: 4px solid #176B68;
            padding: 1rem 1.1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: none;
        }

        .ep-resource-step-label {
            display: block;
            color: #176B68;
            font-size: 0.75rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
        }

        .ep-resource-step p {
            color: #264D47;
            line-height: 1.65;
            margin: 0;
        }

        .ep-resource-note {
            color: #38524B;
            line-height: 1.6;
            margin-top: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
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
                    if (
                        equipment_control
                        == "Only with landlord or property-manager approval"
                    ):
                        card_title = "Talk to your landlord or property manager"
                    elif (
                        equipment_control
                        == "No, I cannot authorize equipment changes"
                    ):
                        card_title = "Find the person who can approve changes"
                    else:
                        card_title = "Check who can approve changes"

                    st.markdown(
                        f'<h3 class="ep-action-title">'
                        f'{escape(card_title)}</h3>',
                        unsafe_allow_html=True,
                    )

                    if main_concern == "Heating or cooling":
                        conversation_items = [
                            "Note which rooms are affected.",
                            "Write down when the problem happens.",
                            "Identify the heating or cooling equipment, "
                            "if you know it.",
                        ]
                    elif main_concern == "Water use or water heating":
                        conversation_items = [
                            "Describe the water-use or hot-water issue.",
                            "Note where and when it happens.",
                            "Identify the fixture or equipment involved, "
                            "if you know it.",
                        ]
                    else:
                        conversation_items = [
                            "List the appliances you are concerned about.",
                            "Describe the problem or electricity-use concern.",
                            "Note which appliances belong to you and which "
                            "belong to the property owner.",
                        ]

                    items_html = "".join(
                        f"<li>{escape(item)}</li>"
                        for item in conversation_items
                    )

                    st.markdown(
                        f'<div class="ep-action-panel">'
                        f'<span class="ep-action-label">BEFORE YOU TALK</span>'
                        f"<ul>{items_html}</ul>"
                        f"</div>",
                        unsafe_allow_html=True,
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
                            "Note which rooms feel too hot or cold, when it "
                            "happens, and any noticeable drafts around windows "
                            "or doors. Record what you find before deciding "
                            "on property changes."
                        )

                    st.markdown(
                        f'<h3 class="ep-action-title">'
                        f"{escape(card_title)}</h3>"
                        f'<div class="ep-action-panel">'
                        f'<span class="ep-action-label">YOUR FIRST MOVE</span>'
                        f"<p>{escape(card_description)}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                if action["requires_equipment_control"]:
                    st.caption(
                        "Explore your options first. This is not a "
                        "recommendation to buy or replace equipment."
                    )

                if action["id"] == "equipment_permission_next_step":
                    with st.expander("Why this step?"):
                        st.write(action["reason"])

    else:
        st.info(
            "No action matches your current selections yet. "
            "Try adjusting your concern or next-step preference."
        )

    matching_programs = []

    try:
        programs = load_json(PROGRAMS_PATH)
        matching_programs = [
            program
            for program in programs
            if main_concern in program.get("concerns", [])
            and change_level in program.get("change_levels", [])
        ]
    except Exception:
        st.warning(
            "Helpful resources could not be loaded. "
            "Your action recommendations are still available."
        )

    st.subheader("Resources for your next step")
    st.caption(
        "Resources match your current topic—not confirmed eligibility."
    )

    if matching_programs:
        for program in matching_programs:
            is_heat_pump = (
                program.get("id") == "pseg_li_home_comfort_heat_pumps"
            )

            provider_text = escape(str(program.get("provider", "")))
            title_text = escape(str(program.get("name", "")))
            summary_text = escape(str(program.get("summary", "")))
            next_step_text = escape(str(program.get("next_step", "")))

            with st.container(border=True):
                st.markdown(
                    f'<span class="ep-resource-provider">'
                    f"{provider_text}</span>"
                    f'<h3 class="ep-resource-heading">{title_text}</h3>'
                    f'<p class="ep-resource-summary">{summary_text}</p>'
                    f'<div class="ep-resource-step">'
                    f'<span class="ep-resource-step-label">NEXT STEP</span>'
                    f"<p>{next_step_text}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if is_heat_pump:
                    st.markdown("#### Check your building category")

                    if dwelling_units == "1–4":
                        st.success(
                            "Your answer places your building "
                            "in the 1–4-unit category."
                        )
                        st.caption(
                            "Building size only—not an eligibility decision. "
                            "Project, equipment, contractor, and other "
                            "requirements still need review."
                        )

                    elif dwelling_units == "5 or more":
                        st.info(
                            "Your answer places your building in the "
                            "separate multifamily category."
                        )
                        st.caption(
                            "The 1–4-unit screening path does not apply. "
                            "Other rebates may be available; review the "
                            "multifamily requirements on the official page."
                        )

                    else:
                        st.warning(
                            "Confirm the number of homes or apartments in "
                            "your building to identify the category to review."
                        )
                        st.caption(
                            "Ask the owner or manager if needed. Count "
                            "separate homes or apartments, not bedrooms."
                        )

                    heat_pump_permission_notes = {
                        "Yes, I can authorize equipment changes": (
                            "You reported that you can approve equipment "
                            "changes. Review the program requirements "
                            "before planning a purchase."
                        ),
                        "Only with landlord or property-manager approval": (
                            "Discuss proposed equipment changes with your "
                            "landlord or property manager before moving forward."
                        ),
                        "No, I cannot authorize equipment changes": (
                            "Identify who can approve equipment changes "
                            "before planning an upgrade."
                        ),
                        "I am not sure": (
                            "Confirm who can approve equipment changes "
                            "before planning an upgrade."
                        ),
                    }

                    permission_note = heat_pump_permission_notes.get(
                        equipment_control,
                        "Confirm who can approve equipment changes "
                        "before planning an upgrade.",
                    )

                    st.markdown(
                        f'<p class="ep-resource-note">'
                        f"{escape(permission_note)} "
                        f"Building category and equipment permission are "
                        f"separate checks. Neither establishes rebate "
                        f"eligibility.</p>",
                        unsafe_allow_html=True,
                    )

                else:
                    scope_note = program.get("eligibility_note","")
                    if scope_note:
                        st.caption(scope_note)

                button_label = (
                    "Explore the program ↗"
                    if is_heat_pump
                    else "Open official resource ↗"
                )

                st.link_button(
                    button_label,
                    program.get("source_url"),
                    type="primary",
                    use_container_width=False,
                )

             

    else:
        st.info(
            "No matching resource is listed in our current catalog. "
            "Other guidance, programs, or incentives may be available."
        )

    with st.expander("About this plan & source details"):
        st.markdown("#### How your plan is matched")
        st.write(
            "Actions match your concern, preferred next step, and "
            "equipment-change permissions. Resources match your "
            "concern and preferred next step."
        )
        st.write(
            "For the heat-pump resource, your building-size answer "
            "also determines which category guidance is shown."
        )
        st.caption(
            "Matches are starting points—not confirmed eligibility "
            "or recommendations to buy equipment."
        )

        for program in matching_programs:
            st.divider()
            st.markdown(
                f"#### {program.get('name', 'Resource')}"
            )
            st.write(
                f"Provider: {program.get('provider', 'Not listed')}"
            )
            st.caption(
                "Source checked: "
                f"{program.get('source_checked_on') or 'Not recorded'}"
            )

            requirements = program.get("verified_requirements", [])
            if requirements:
                st.write("Selected requirements to review:")
                for requirement in requirements:
                    description = requirement.get("description", "")
                    if description:
                        st.write(f"- {description}")

                st.caption(
                    "These are selected requirements, not a complete "
                    "eligibility checklist. Review the official page."
                )








    st.divider()

    st.subheader("Explore a potential upgrade")
    st.write("Have a project cost and savings estimate? See how they compare over time.")
    if st.button("Explore Upgrade Payback", key="results_open_payback", type="primary"):
        st.session_state.screen = "simulator"
        st.rerun()


# --- App routing -----------------------------------------------------------
screen = st.session_state.get("screen", "home")
if screen == "home":
    render_home()
elif screen == "simulator":
    render_simulator()
else:
    render_questionnaire()
