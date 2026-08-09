
import streamlit as st
import requests


# ==========================================
# Configuration
# ==========================================

API_URL = "http://127.0.0.1:8000"


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="PeerMatch",
    page_icon="🤝",
    layout="wide"
)


# ==========================================
# Subject Data
# ==========================================

@st.cache_data
def load_subjects():

    response = requests.get(
        f"{API_URL}/subjects",
        timeout=10
    )

    response.raise_for_status()

    return response.json()
SUBJECTS = load_subjects()

# Flatten all subjects for validation/display
ALL_SUBJECTS = [
    subject
    for category in SUBJECTS.values()
    for subject in category
]


# ==========================================
# Helper Function
# ==========================================

def format_subjects(selected_subjects):

    result = []

    for subject in selected_subjects:

        for category, subjects in SUBJECTS.items():

            if subject in subjects:

                result.append(
                    f"{category} → {subject}"
                )

                break

    return result


# ==========================================
# Header
# ==========================================

st.title("🤝 PeerMatch")

st.subheader(
    "Peer Learning Recommendation System"
)

st.write(
    "Find peers who can teach you the subjects "
    "you want to learn while learning from your strengths."
)

st.divider()


# ==========================================
# User Input
# ==========================================

st.header("👤 Tell us about yourself")

col1, col2 = st.columns(2)


# ==========================================
# Strengths
# ==========================================

with col1:

    st.subheader("💪 Your Strengths")

    strengths = st.multiselect(
        "Select subjects you are good at",
        options=ALL_SUBJECTS,
        placeholder="Choose your strengths..."
    )


# ==========================================
# Weaknesses
# ==========================================

with col2:

    st.subheader("📚 Your Weaknesses")

    weaknesses = st.multiselect(
        "Select subjects you want to learn",
        options=ALL_SUBJECTS,
        placeholder="Choose your weaknesses..."
    )


# ==========================================
# Display Selected Subjects
# ==========================================

if strengths:

    st.markdown("**Your strengths:**")

    for subject in format_subjects(strengths):

        st.write(f"🟢 {subject}")


if weaknesses:

    st.markdown("**Your weaknesses:**")

    for subject in format_subjects(weaknesses):

        st.write(f"🔵 {subject}")


# ==========================================
# Validation
# ==========================================

common_subjects = set(strengths) & set(weaknesses)

if common_subjects:

    st.error(
        "A subject cannot be both a strength and a weakness: "
        + ", ".join(common_subjects)
    )


# ==========================================
# Find Matches
# ==========================================

st.divider()

if st.button(
    "🔍 Find My Best Matches",
    type="primary",
    use_container_width=True
):

    # -----------------------------
    # Validation
    # -----------------------------

    if not strengths:

        st.warning(
            "Please select at least one strength."
        )

    elif not weaknesses:

        st.warning(
            "Please select at least one weakness."
        )

    elif common_subjects:

        st.error(
            "Please remove subjects that appear "
            "in both strengths and weaknesses."
        )

    else:

        # -----------------------------
        # API Payload
        # -----------------------------

        payload = {
            "strengths": strengths,
            "weaknesses": weaknesses
        }


        try:

            with st.spinner(
                "🔎 Finding your best peer matches..."
            ):

                response = requests.post(
                    f"{API_URL}/recommend",
                    json=payload,
                    timeout=10
                )


            # ==================================
            # Successful Response
            # ==================================

            if response.status_code == 200:

                data = response.json()

                recommendations = data.get(
                    "recommendations",
                    []
                )


                if not recommendations:

                    st.info(
                        "😔 No suitable matches found."
                    )

                    st.write(
                        "Try selecting more strengths "
                        "or weaknesses."
                    )


                else:

                    st.success(
                        f"🎉 Found "
                        f"{len(recommendations)} "
                        f"potential peer(s)!"
                    )

                    st.divider()

                    st.header(
                        "🌟 Recommended Peers"
                    )


                    # ==================================
                    # Display Matches
                    # ==================================

                    for index, match in enumerate(
                        recommendations,
                        start=1
                    ):

                        with st.container(
                            border=True
                        ):

                            # --------------------------
                            # Name + Score
                            # --------------------------

                            col1, col2 = st.columns(
                                [3, 1]
                            )


                            with col1:

                                st.subheader(
                                    f"{index}. "
                                    f"{match['name']}"
                                )

                                st.write(
                                    f"**Match Quality:** "
                                    f"{match['quality']}"
                                )


                            with col2:

                                st.metric(
                                    "Match Score",
                                    f"{match['match_score']}%"
                                )


                            st.divider()


                            # --------------------------
                            # Learn / Teach
                            # --------------------------

                            col1, col2 = st.columns(2)


                            with col1:

                                st.markdown(
                                    "### 📚 You Can Learn"
                                )

                                if match["can_learn"]:

                                    for subject in match[
                                        "can_learn"
                                    ]:

                                        st.write(
                                            f"📘 {subject}"
                                        )

                                else:

                                    st.write(
                                        "No subjects to learn."
                                    )


                            with col2:

                                st.markdown(
                                    "### 🎓 You Can Teach"
                                )

                                if match["can_teach"]:

                                    for subject in match[
                                        "can_teach"
                                    ]:

                                        st.write(
                                            f"🎓 {subject}"
                                        )

                                else:

                                    st.write(
                                        "No subjects to teach."
                                    )


                            # --------------------------
                            # Reasons
                            # --------------------------

                            st.markdown(
                                "### 💡 Why This Match?"
                            )

                            for reason in match["reasons"]:

                                st.write(
                                    f"✅ {reason}"
                                )


            # ==================================
            # Bad Request
            # ==================================

            elif response.status_code == 400:

                error_data = response.json()

                st.error(
                    f"❌ Invalid input: "
                    f"{error_data.get('detail')}"
                )


            # ==================================
            # Backend Error
            # ==================================

            elif response.status_code >= 500:

                st.error(
                    "❌ Server error. "
                    "Please check your FastAPI backend."
                )


            # ==================================
            # Other Errors
            # ==================================

            else:

                st.error(
                    f"❌ API Error: "
                    f"{response.status_code}"
                )


        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to FastAPI."
            )

            st.info(
                "Make sure your backend is running:\n\n"
                "uvicorn app.main:app --reload"
            )


        except requests.exceptions.Timeout:

            st.error(
                "⏳ Request timed out. "
                "Please try again."
            )


        except Exception as e:

            st.error(
                f"❌ Something went wrong: {str(e)}"
            )

