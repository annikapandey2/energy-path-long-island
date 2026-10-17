
import json
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Energy Path",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "screen" not in st.session_state:
    st.session_state.screen = "home"

def reset_energy_plan():
    keys_to_clear = [
        "submitted_plan",
        "plan_main_concern",
        "plan_change_level",
        "plan_home_status",
        "plan_dwelling_units",
        "plan_equipment_control",
        "plan_main_goal",
        "plan_heating_source"
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.session_state.screen = "home"


if st.session_state.screen == "simulator":



    if st.button("← Back to Home", key="payback_back_home"):
        st.session_state.screen = "home"
        st.rerun()

    st.title("Explore Upgrade Payback")
    st.write(
        "Explore how an upgrade's upfront cost compares "
        "with its assumed energy savings over time."
    )
    st.caption(
        "Try a sourced air-sealing and insulation example, "
        "or use an estimate from a quote or assessment. "
        "This calculator explores assumptions—it does not "
        "predict savings for your home."
    )


    mode = st.radio(
        "Choose your starting point",
        [
            "Explore an air-sealing + insulation example",
            "My own estimate"
        ],
        key="payback_mode"
    )

    benchmark_mode = (
        mode == "Explore an air-sealing + insulation example"
    )

    if benchmark_mode:
        st.subheader("Air sealing + insulation")

        st.info(
            "ENERGY STAR estimates average savings of 11% "
            "on total home-energy costs from combined "
            "air sealing and insulation improvements. "
            "This is a national modeled benchmark—not "
            "a prediction for your home."
        )

        st.markdown(
            "[View the official ENERGY STAR methodology]"
            "(https://www.energystar.gov/"
            "saveathome/seal_insulate/methodology)"
        )

        with st.expander("What this benchmark covers"):
            st.write(
                "The estimate covers combined improvements: "
                "sealing air leaks throughout the home and "
                "adding insulation in areas such as attics, "
                "floors over crawl spaces, and accessible "
                "basement rim joists."
            )
            st.write(
                "It does not describe weatherstripping alone "
                "or attic sealing alone. Existing insulation, "
                "air leakage, climate, and the work performed "
                "can change actual savings."
            )
            st.write(
                "Energy Path applies the published 11% "
                "national average to the annual home-energy "
                "spending you enter. It does not model "
                "your individual home."
            )

    else:
        st.info(
            "Use a savings estimate from an assessment, "
            "contractor, or your own hypothetical scenario. "
            "Energy Path calculates payback from your inputs; "
            "it does not independently predict the savings."
        )

    st.caption(
        "Starting dollar amounts are editable examples, "
        "not researched typical costs or household bills."
    )

    with st.form("payback_scenario_form"):

        upfront_cost = st.number_input(
            "Upfront project cost you would pay ($)",
            min_value=0.0,
            max_value=1000000.0,
            value=1500.0,
            step=50.0,
            format="%.2f",
            key="payback_project_cost",
            help=(
                "Replace the example with your project "
                "estimate or quote. Do not subtract "
                "unconfirmed rebates or tax credits. "
                "In benchmark mode, the cost should cover "
                "the combined air-sealing and insulation "
                "work being explored."
            )
        )

        if benchmark_mode:
            annual_energy_spending = st.number_input(
                "Total annual home-energy spending ($/year)",
                min_value=0.0,
                max_value=1000000.0,
                value=3000.0,
                step=100.0,
                format="%.2f",
                key="payback_annual_energy_spending",
                help=(
                    "Add a full year of electricity and "
                    "any natural gas, heating oil, propane, "
                    "or other home-energy costs. Include "
                    "each fuel once. Do not include water, "
                    "internet, or vehicle fuel."
                )
            )

            st.caption(
                "Calculation: annual home-energy spending "
                "× 11% ÷ 12 = assumed average monthly savings."
            )

            monthly_savings = (
                annual_energy_spending * 0.11 / 12
            )

        else:
            monthly_savings = st.number_input(
                "Assumed monthly savings ($)",
                min_value=0.0,
                max_value=100000.0,
                value=20.0,
                step=5.0,
                format="%.2f",
                key="payback_own_monthly_savings",
                help=(
                    "Enter your own estimate. This value "
                    "is not supplied or verified by "
                    "Energy Path."
                )
            )

        years = st.slider(
            "Years to explore",
            min_value=1,
            max_value=30,
            value=5,
            key="payback_horizon"
        )

        submitted = st.form_submit_button(
            "Run my scenario",
            type="primary"
        )

    if submitted:
        st.session_state.payback_scenario = {
            "upfront_cost": float(upfront_cost),
            "monthly_savings": float(monthly_savings),
            "years": int(years),
            "mode": mode,
            "annual_energy_spending": (
                float(annual_energy_spending)
                if benchmark_mode
                else None
            )
        }


    scenario = st.session_state.get("payback_scenario")

    if scenario is None:
        st.caption(
            "Enter your assumptions, then select "
            "'Run my scenario' to see the results."
        )

    else:
        cost = scenario["upfront_cost"]
        savings = scenario["monthly_savings"]
        horizon_years = scenario["years"]

        total_months = horizon_years * 12
        annual_savings = savings * 12
        net_savings = savings * total_months - cost

        st.subheader("Your scenario results")
        result_mode = scenario.get(
            "mode",
            "My own estimate"
        )

        st.write(f"Scenario basis: {result_mode}")

        if result_mode == "Explore an air-sealing + insulation example":
            annual_spending = scenario[
                "annual_energy_spending"
            ]

            st.caption(
                "Savings assumption: ENERGY STAR's 11% "
                "national modeled benchmark for combined "
                "air sealing and insulation, applied to "
                f"${annual_spending:,.2f} in annual "
                "home-energy spending."
            )

            st.markdown(
                "[Benchmark source: ENERGY STAR]"
                "(https://www.energystar.gov/"
                "saveathome/seal_insulate/methodology)"
            )

        else:
            st.caption(
                "Savings assumption: the monthly amount "
                "you entered—not an official benchmark."
            )

        st.caption(
            "Results reflect your last submitted scenario: "
            f"${cost:,.2f} upfront, "
            f"${savings:,.2f} saved per month, "
            f"over {horizon_years} years. "
            "If you change the inputs, select "
            "'Run my scenario' again."
        )

        if cost == 0:
            payback_months = 0.0
            payback_label = "No upfront cost"
        elif savings == 0:
            payback_months = None
            payback_label = "No payback"
        else:
            payback_months = cost / savings

            if payback_months >= 12:
                payback_label = (
                    f"{payback_months / 12:,.1f} years"
                )
            else:
                payback_label = (
                    f"{payback_months:,.1f} months"
                )


        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Simple payback",
            payback_label
        )

        metric2.metric(
            "Assumed annual savings",
            f"${annual_savings:,.2f}"
        )

        metric3.metric(
            f"Net savings after {horizon_years} years",
            f"${net_savings:,.2f}"
        )

        if cost == 0:
            st.info(
                "You entered no upfront cost, so there is "
                "no initial investment to recover."
            )
        elif savings == 0:
            st.warning(
                "With no monthly savings, this scenario "
                "does not recover its upfront cost."
            )
        elif payback_months > total_months:
            st.warning(
                "This scenario does not recover its upfront "
                f"cost within the selected {horizon_years} years. "
                "At the same monthly savings, simple payback "
                f"would take {payback_months:,.1f} months "
                f"({payback_months / 12:,.1f} years)."
            )
        else:
            st.success(
                "Under these assumptions, savings recover "
                f"the upfront cost after {payback_months:,.1f} "
                f"months ({payback_months / 12:,.1f} years)."
            )

        months = list(range(total_months + 1))

        if (
            payback_months is not None
            and 0 < payback_months <= total_months
            and payback_months not in months
        ):
            months = sorted(months + [payback_months])

        balances = [
            savings * month - cost
            for month in months
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=months,
                y=balances,
                mode="lines",
                name="Savings minus upfront cost",
                line={
                    "color": "#176B68",
                    "width": 4
                },
                hovertemplate=(
                    "Month %{x:.1f}<br>"
                    "Net savings: $%{y:,.2f}"
                    "<extra></extra>"
                )
            )
        )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#64748B",
            annotation_text="Break-even",
            annotation_position="top left"
        )

        if (
            payback_months is not None
            and 0 < payback_months <= total_months
        ):
            fig.add_trace(
                go.Scatter(
                    x=[payback_months],
                    y=[0],
                    mode="markers",
                    name="Payback point",
                    marker={
                        "color": "#164B40",
                        "size": 12
                    },
                    hovertemplate=(
                        "Payback: %{x:.1f} months"
                        "<extra></extra>"
                    )
                )
            )

        fig.update_layout(
            title="How assumed savings compare with upfront cost",
            xaxis_title="Months after upgrade",
            yaxis_title="Cumulative savings minus upfront cost ($)",
            template="plotly_white",
            hovermode="x unified",
            showlegend=False,
            margin={
                "l": 20,
                "r": 20,
                "t": 70,
                "b": 30
            }
        )

        fig.update_xaxes(
            range=[0, total_months]
        )

        fig.update_yaxes(
            tickprefix="$",
            tickformat=",.0f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displaylogo": False}
        )

       with st.expander("Sources, assumptions & calculation"):
            st.markdown(
                "#### Where the numbers come from"
            )

            if result_mode == (
                "Explore an air-sealing + insulation example"
            ):
                st.write(
                    "The savings percentage comes from "
                    "ENERGY STAR's published national modeled "
                    "benchmark for combined air sealing and "
                    "insulation. The source link appears above "
                    "these results. Applying that percentage "
                    "to your entered spending is an illustration, "
                    "not a home-specific prediction."
                )
            else:
                st.write(
                    "The monthly savings figure is the amount "
                    "you entered. Energy Path does not verify "
                    "or independently predict that amount."
                )

            st.write(
                "Project cost and the time period are your "
                "inputs. Starting dollar amounts are editable "
                "examples, not researched typical costs."
            )

            st.markdown("#### Formulas and limitations")

            st.write(
                "Simple payback in months = upfront cost "
                "÷ assumed monthly savings."
            )
            st.write(
                "Net savings = assumed monthly savings "
                "× number of months − upfront cost."
            )
            st.write(
                "The graph begins below zero when there is "
                "an upfront cost. It reaches break-even "
                "when cumulative savings equal that cost."
            )
            st.write(
                "This simplified scenario assumes constant "
                "monthly savings. It excludes financing, "
                "maintenance, replacements, changing energy "
                "prices, inflation, and the time value of money. "
                "It does not check equipment life, rebate "
                "eligibility, or whether an upgrade is "
                "appropriate for your home."
            )

    st.stop()




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

        if st.button(
            "Explore Upgrade Payback",
            key="home_open_payback",
            use_container_width=True
        ):
            st.session_state.screen = "simulator"
            st.rerun()

        st.caption(
            "Already have a cost and savings estimate? "
            "Explore a what-if scenario."
        )



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
                placeholder="Choose a concern",
                key="plan_main_concern"
            )

            change_level = st.radio(
                "What kind of next step are you looking for?",
                [
                    "Easy changes I can do now",
                    "Programs or incentives to explore",
                    "Bigger long-term updates"
                ],
                key="plan_change_level"
            )

            st.caption(
                "Our resource list is still growing. "
                "Matching a resource does not confirm that you qualify."
            )

    with home_col:
        with st.container(border=True):
            st.subheader("2. Your home")

            home_status = st.radio(
                "Do you rent or own?",
                ["Rent", "Own"],
                horizontal=True,
                key="plan_home_status"
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
                ),
                key="plan_dwelling_units"
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
                placeholder="Choose an answer",
                key="plan_equipment_control"
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
            index=None,
            key="plan_main_goal"
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
            placeholder="Choose a heating source",
            key="plan_heating_source"
        )

    build_plan = st.form_submit_button(
        "Build My Energy Action Plan",
        type="primary",
        use_container_width=True
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

    st.session_state.submitted_plan = {
        "main_concern": main_concern,
        "change_level": change_level,
        "home_status": home_status,
        "dwelling_units": dwelling_units,
        "equipment_control": equipment_control
    }

submitted_plan = st.session_state.get("submitted_plan")

if submitted_plan is None:
    st.stop()

main_concern = submitted_plan["main_concern"]
change_level = submitted_plan["change_level"]
home_status = submitted_plan["home_status"]
dwelling_units = submitted_plan["dwelling_units"]
equipment_control = submitted_plan["equipment_control"]

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

  

   
with result_col2:
    st.button(
        "Start a New Plan",
        type="secondary",
        use_container_width=True,
        on_click=reset_energy_plan
    )

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
            if action["id"] == "equipment_permission_next_step":
                with st.expander("Why this step?"):
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
        "Resources match your current topic - not confirmed eligiblity."
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
                            NEXT STEP
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
                    with st.expander("Resource scope and limitations"):
                        st.write(program["eligibility_note"])
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
            "No matching resource is listed in our currnt catalog. "
            "Other guidance, programs, or incentives may be available."
        )
       
with st.expander("How your plan is matched"):
    st.write(
        "Actions are matched to your concern, next-step preference, "
        "and equipment-change permissions. Resources are matched "
        "to your concern and next-step preference."
    )
    st.write(
        "The heat-pump resource also displays a building-category "
        "check based on your answer."
    )
    st.caption(
        "Your optional goal and heating source do not affect "
        "recommendations yet."
    )


