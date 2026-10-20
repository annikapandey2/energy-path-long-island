import json
import time
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



def load_json(path: Path):
    """Read the current json catalog from disk"""
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
        /* Home background */
        .stApp:has(.ep-hero) {
            background: #103D3B;
        }

        .stApp:has(.ep-hero) [data-testid="stHeader"] {
            background: #103D3B;
        }

        /* Main introduction */
        .ep-hero {
            text-align: center;
            padding: 2.8rem 1.5rem;
            margin-bottom: 1.8rem;
            background: #EAF6F1;
            border: 2px solid #83C6B2;
            border-radius: 22px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
        }

        .ep-hero h1.ep-title {
            color: #083F36;
            font-family: "Segoe UI", system-ui, sans-serif;
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

        /* Raised action tiles */
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
            font-family: "Segoe UI", system-ui, sans-serif;
            font-size: clamp(1.15rem, 2vw, 1.4rem);
            font-weight: 700;
            line-height: 1.35;
            letter-spacing: -0.02em;
            text-align: center;
            color: inherit;
        }

        .st-key-home_primary button {
            background: #247B72;
            color: #FFFFFF;
            border: 1px solid #79C2AF;
            box-shadow:
                0 6px 0 #082F2D,
                0 12px 22px rgba(0, 0, 0, 0.20);
        }

        .st-key-home_secondary button {
            background: #EDF5FC;
            color: #164B40;
            border: 1px solid #BDD4E8;
            box-shadow:
                0 6px 0 #8EAFC3,
                0 12px 22px rgba(0, 0, 0, 0.17);
        }

        .st-key-home_primary button:hover {
            background: #1B695F;
            color: #FFFFFF;
            border-color: #A3D9C9;
            transform: translateY(-2px);
            box-shadow:
                0 8px 0 #082F2D,
                0 16px 26px rgba(0, 0, 0, 0.23);
        }

        .st-key-home_secondary button:hover {
            background: #DDECF7;
            color: #164B40;
            border-color: #9BBFD9;
            transform: translateY(-2px);
            box-shadow:
                0 8px 0 #8EAFC3,
                0 16px 26px rgba(0, 0, 0, 0.20);
        }

        .st-key-home_primary button:active,
        .st-key-home_secondary button:active {
            transform: translateY(2px);
            box-shadow: 0 2px 0 #082F2D;
        }

        .st-key-home_primary button:focus-visible,
        .st-key-home_secondary button:focus-visible {
            outline: 3px solid #F2D58A;
            outline-offset: 5px;
        }

        .ep-choice-caption {
            color: #E1EFEB;
            text-align: center;
            font-size: 0.9rem;
            line-height: 1.5;
            margin: 1rem 0 0;
        }

        .ep-section-label {
            text-align: center;
            color: #B8E0D2;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            margin: 2.3rem 0 1.2rem;
        }

        /* Supporting cards */
        .ep-feature {
            border: 1px solid #B8D6CC;
            border-radius: 16px;
            padding: 1.4rem;
            min-height: 210px;
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.10);
        }

        .ep-feature-number {
            color: #10594D;
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
            color: #123D35;
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

        /* Why Energy Path */
        .ep-about {
            background: #F3F8F6;
            border: 1px solid #C8DDD5;
            border-left: 5px solid #71BDA5;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1.6rem 0 1rem;
        }

        .ep-about .ep-about-kicker {
            color: #10594D;
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
            color: #123D35;
            line-height: 1.7;
            margin: 0;
            max-width: 850px;
        }

        /* About dropdown */
        .st-key-home_about details {
            background: #EAF3EF;
            border: 1px solid #A8CFC0;
            border-radius: 14px;
            color: #164B40;
        }

        .st-key-home_about summary {
            color: #164B40;
            padding: 0.8rem 1rem;
        }

        .st-key-home_about summary:hover {
            background: #DBECE4;
            border-radius: 14px;
        }

        .st-key-home_about [data-testid="stMarkdownContainer"],
        .st-key-home_about [data-testid="stMarkdownContainer"] p,
        .st-key-home_about [data-testid="stMarkdownContainer"] h4 {
            color: #164B40;
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
                transform: none !important;
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
            st.markdown("#### Why I created it")
            st.write(
                "I created Energy Path to give Long Island renters "
                "and homeowners a clearer place to start with "
                "home-energy questions. I wanted to bring practical "
                "next steps and official resources together, rather "
                "than leave people with another list of links."
            )

            st.markdown("#### What I wanted to do differently")
            st.write(
                "Not everyone can replace equipment or approve "
                "changes to their home. I wanted the guidance to "
                "account for that—not assume that every user owns "
                "their home or can make those decisions."
            )
            st.write(
                "I also included a separate payback calculator "
                "so you can explore how a project cost compares "
                "with assumed savings over time."
            )

            st.markdown("#### What to keep in mind")
            st.write(
                "Energy Path is a student-built prototype, and "
                "its resource list is limited. It does not confirm "
                "rebate eligibility, replace a home-energy "
                "assessment, or guarantee savings."
            )




def render_simulator():
    top_bar()

    st.title("Explore Upgrade Payback")

    if st.button(
        "← Back to home",
        key="payback_back_home",
        type="secondary",
    ):
        st.session_state.screen = "home"
        st.rerun()

    st.write(
        "Explore how upfront costs and assumed savings "
        "compare over time."
    )

    benchmark_label = "Explore an air-sealing + insulation example"
    source_url = (
        "https://www.energystar.gov/"
        "saveathome/seal_insulate/methodology"
    )

    mode = st.radio(
        "Choose your starting point",
        [benchmark_label, "My own estimate"],
        key="payback_mode",
    )

    benchmark_mode = mode == benchmark_label
    compare = False

    if benchmark_mode:
        st.info(
            "This guided example applies ENERGY STAR's "
            "11% national modeled savings benchmark for combined "
            "air sealing and insulation to your annual home-energy "
            "spending. It is not a home-specific prediction."
        )
        st.markdown(
            f"[View the ENERGY STAR methodology]({source_url})"
        )
    else:
        st.caption(
            "Use estimates for the same home and a comparable scope "
            "of work. Savings are your assumptions—not predictions "
            "made by Energy Path."
        )
        compare = st.checkbox(
            "Compare two project estimates",
            key="payback_compare_enabled",
        )

    def project_inputs(label, prefix, default_cost, default_savings):
        st.subheader(label)

        cost = st.number_input(
            "Upfront cost you would pay ($)",
            min_value=0.0,
            max_value=1000000.0,
            value=default_cost,
            step=50.0,
            format="%.2f",
            key=f"{prefix}_cost",
            help=(
                "Use a quote or hypothetical amount. "
                "Do not subtract unconfirmed rebates or tax credits."
            ),
        )

        savings = st.number_input(
            "Assumed monthly savings ($)",
            min_value=0.0,
            max_value=100000.0,
            value=default_savings,
            step=5.0,
            format="%.2f",
            key=f"{prefix}_savings",
            help=(
                "Use a project estimate or a hypothetical scenario. "
                "Energy Path does not verify this amount."
            ),
        )

        return {
            "label": label,
            "cost": float(cost),
            "monthly_savings": float(savings),
        }

    with st.form("payback_comparison_form"):
        annual_spending = None

        if benchmark_mode:
            st.subheader("Air sealing + insulation")

            cost = st.number_input(
                "Upfront project cost you would pay ($)",
                min_value=0.0,
                max_value=1000000.0,
                value=1500.0,
                step=50.0,
                format="%.2f",
                key="payback_project_cost",
                help=(
                    "Use the combined cost of the air-sealing "
                    "and insulation work. The starting amount "
                    "is an example, not a researched typical cost."
                ),
            )

            annual_spending = st.number_input(
                "Total annual home-energy spending ($/year)",
                min_value=0.0,
                max_value=1000000.0,
                value=3000.0,
                step=100.0,
                format="%.2f",
                key="payback_annual_energy_spending",
                help=(
                    "Include a full year of electricity and other "
                    "home-energy fuels, each counted once. "
                    "Exclude water, internet, and vehicle fuel."
                ),
            )

            projects = [{
                "label": "Air sealing + insulation",
                "cost": float(cost),
                "monthly_savings": float(
                    annual_spending * 0.11 / 12
                ),
            }]

            st.caption(
                "Assumed monthly savings = "
                "annual home-energy spending × 11% ÷ 12."
            )

        elif compare:
            col_a, col_b = st.columns(2)

            with col_a:
                option_a = project_inputs(
                    "Option A", "payback_a", 1500.0, 25.0
                )

            with col_b:
                option_b = project_inputs(
                    "Option B", "payback_b", 3000.0, 45.0
                )

            projects = [option_a, option_b]

            st.caption(
                "Starting amounts are hypothetical examples, "
                "not quotes or typical project costs."
            )

        else:
            projects = [
                project_inputs(
                    "Your estimate",
                    "payback_single",
                    1500.0,
                    20.0,
                )
            ]

        years = st.slider(
            "Years to explore",
            min_value=1,
            max_value=30,
            value=5,
            key="payback_horizon",
        )

        run = st.form_submit_button(
            "Compare my scenarios" if compare else "Run my scenario",
            type="primary",
            use_container_width=True,
        )

    if run:
        st.session_state["payback_comparison_result"] = {
            "mode": mode,
            "projects": projects,
            "years": int(years),
            "annual_spending": annual_spending,
        }

    result = st.session_state.get("payback_comparison_result")

    if result is None:
        st.caption(
            "Enter your assumptions, then run the scenario "
            "to see the results."
        )
        return

    saved_projects = result["projects"]
    saved_years = result["years"]
    total_months = saved_years * 12

    st.divider()
    st.subheader(
        "Your comparison"
        if len(saved_projects) == 2
        else "Your scenario results"
    )

    st.caption(
        f"Last submitted: {result['mode']} · "
        f"{saved_years}-year horizon. "
        "After changing inputs or modes, submit again "
        "to update these results."
    )

    if result["mode"] == benchmark_label:
        st.caption(
            "Savings basis: the 11% national modeled benchmark "
            "applied to "
            f"${result['annual_spending']:,.2f} "
            "in annual home-energy spending."
        )
        st.markdown(
            f"[Benchmark source: ENERGY STAR]({source_url})"
        )
    else:
        st.caption(
            "Savings basis: user-entered monthly estimates. "
            "No savings amounts have been independently verified."
        )

    colors = ["#176B68", "#8B3F95"]
    calculated = []

    for project in saved_projects:
        cost = project["cost"]
        savings = project["monthly_savings"]

        if cost == 0:
            payback = 0.0
            payback_label = "No upfront cost"
        elif savings == 0:
            payback = None
            payback_label = "No payback"
        else:
            payback = cost / savings
            payback_label = (
                f"{payback / 12:,.1f} years"
                if payback >= 12
                else f"{payback:,.1f} months"
            )

        calculated.append({
            **project,
            "payback": payback,
            "payback_label": payback_label,
            "annual_savings": savings * 12,
            "net": savings * total_months - cost,
        })

    result_columns = st.columns(len(calculated))

    for column, project in zip(result_columns, calculated):
        with column:
            with st.container(border=True):
                st.subheader(project["label"])
                st.caption(
                    f"${project['cost']:,.2f} upfront · "
                    f"${project['monthly_savings']:,.2f}/month "
                    "assumed savings"
                )
                st.metric(
                    "Simple payback",
                    project["payback_label"],
                )
                st.metric(
                    "Assumed annual savings",
                    f"${project['annual_savings']:,.2f}",
                )
                st.metric(
                    f"Net savings after {saved_years} years",
                    f"${project['net']:,.2f}",
                )

                if project["cost"] == 0:
                    st.info("No initial cost to recover.")
                elif project["payback"] is None:
                    st.warning(
                        "With zero savings, the upfront "
                        "cost is not recovered."
                    )
                elif project["payback"] > total_months:
                    st.warning(
                        "Does not break even within "
                        "the selected period."
                    )
                else:
                    st.caption(
                        "Break-even occurs within "
                        "the selected period."
                    )

    if len(calculated) == 2:
        a, b = calculated
        difference = a["net"] - b["net"]

        if abs(difference) < 0.005:
            st.info(
                f"Both options have the same modeled net savings "
                f"after {saved_years} years."
            )
        else:
            leader = a if difference > 0 else b
            st.info(
                f"At {saved_years} years, {leader['label']} has "
                f"${abs(difference):,.2f} higher modeled net savings. "
                "This compares entered assumptions—not overall "
                "suitability or guaranteed performance."
            )

        savings_difference = (
            a["monthly_savings"] - b["monthly_savings"]
        )

        if savings_difference != 0:
            crossover = (
                a["cost"] - b["cost"]
            ) / savings_difference

            if crossover > 0:
                if crossover <= total_months:
                    st.caption(
                        "The options reach equal cumulative net "
                        f"savings at {crossover:,.1f} months "
                        f"({crossover / 12:,.1f} years). "
                        "That is not necessarily either "
                        "option's break-even point."
                    )
                else:
                    st.caption(
                        "The options would reach equal cumulative "
                        f"net savings at {crossover / 12:,.1f} years, "
                        "beyond the selected period, if the same "
                        "assumptions continued."
                    )

    fig = go.Figure()

    for index, project in enumerate(calculated):
        months = list(range(total_months + 1))
        payback = project["payback"]

        if payback is not None and 0 < payback <= total_months:
            months = sorted(set(months + [payback]))

        balances = [
            project["monthly_savings"] * month - project["cost"]
            for month in months
        ]

        fig.add_trace(
            go.Scatter(
                x=months,
                y=balances,
                mode="lines",
                name=project["label"],
                line={
                    "color": colors[index],
                    "width": 4,
                    "dash": "solid" if index == 0 else "dash",
                },
                hovertemplate=(
                    "Month %{x:.1f}<br>"
                    "Net savings: $%{y:,.2f}"
                    "<extra>%{fullData.name}</extra>"
                ),
            )
        )

        if payback is not None and 0 < payback <= total_months:
            fig.add_trace(
                go.Scatter(
                    x=[payback],
                    y=[0],
                    mode="markers",
                    name=f"{project['label']} break-even",
                    marker={
                        "color": colors[index],
                        "size": 11,
                    },
                    showlegend=False,
                    hovertemplate=(
                        "Break-even: %{x:.1f} months"
                        "<extra>%{fullData.name}</extra>"
                    ),
                )
            )

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="#64748B",
        annotation_text="Zero net savings",
        annotation_position="top left",
    )

    fig.update_layout(
        title="Upfront cost versus accumulated assumed savings",
        xaxis_title="Months after upgrade",
        yaxis_title="Cumulative savings minus upfront cost ($)",
        template="plotly_white",
        hovermode="x unified",
        showlegend=len(calculated) == 2,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        margin={"l": 20, "r": 20, "t": 100, "b": 30},
    )
    fig.update_xaxes(range=[0, total_months])
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    st.caption(
        "Below zero: savings have not recovered the upfront cost. "
        "Above zero: assumed savings exceed the upfront cost."
    )

    with st.expander("Sources, assumptions & calculations"):
        st.write(
            "Simple payback in months = upfront cost ÷ "
            "assumed monthly savings."
        )
        st.write(
            "Cumulative net savings = assumed monthly savings × "
            "months − upfront cost."
        )
        st.write(
            "In comparison mode, the options are alternatives "
            "considered separately—not combined projects."
        )
        st.write(
            "The guided example"
        )

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
            st.warning(
                "Choose an equipment-control answer. "
                "If you are unsure, select 'I am not sure'."
            )
            st.stop()

        with st.spinner("Preparing your energy action plan…"):
            time.sleep(2)

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
    except Exception as error:
        st.error(
            f"Action catalog error — "
            f"{type(error).__name__}: {error}"
        )
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
    resources_load_failed = False

    try:
        programs = load_json(PROGRAMS_PATH)
        matching_programs = [
            program
            for program in programs
            if main_concern in program.get("concerns", [])
            and change_level in program.get("change_levels", [])
        ]
    except Exception:
        resources_load_failed = True
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

             

    elif not resources_load_failed:
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
