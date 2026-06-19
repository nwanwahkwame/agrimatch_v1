# The Reason for starting the project.
# Problem Statement
# Pictures, link to GitHub, link to Linkedin
# Blurb, fun fact.

from utils import inject_css, init_session, logo
import streamlit as st

# 1. Page Configurations
st.set_page_config(
    page_title="About Our Team — AgriMatch",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

logo()

# Custom CSS for polished, profile card designs
st.markdown("""
<style>
    .team-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .team-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .member-name {
        font-size: 20px;
        font-weight: bold;
        color: #1f2937;
        margin-top: 10px;
    }
    .member-role {
        font-size: 14px;
        color: #ff4b4b;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .member-bio {
        font-size: 14px;
        color: #4b5563;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">🚀 Meet the Dream Team</div>
    <div class="page-header-sub" style="text-align: center;">We are a passionate group of data scientists, and our aim is to build the future one line of code at a time.</div>
</div>""", unsafe_allow_html=True)

# 4. Team Data: Females
team_members_1 = [
    {
        "name": "Ena 'Adurowura' Ayimey",
        "role": "Data Scientist/Post-Harvest Enthusiast",
        "image": "https://media.licdn.com/dms/image/v2/D4E03AQGn309JuKXutw/profile-displayphoto-crop_800_800/B4EZwM6xT.JgAI-/0/1769743261365?e=1782950400&v=beta&t=6V3RWJ4miLF0yAK_LiclZoFVwWSbFxwICBcFJjFD5n0",
        "bio": "With a background in Agriculture, Ena is committed to leveraging post-harvest technology to empower farmers and strengthen food security."
    },
    {
        "name": "Olivia 'Olive' Matey",
        "role": "Data Scientist/L&D Analyst",
        "image": "https://media.licdn.com/dms/image/v2/D4D03AQHTe-zEsZJLdQ/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1725479822210?e=1782950400&v=beta&t=__-k04M4b_UdA9BcO2WwWOOVAcKLXzRJV4tZvGSlqUY",
        "bio": "With a background in customer experience optimization and data-driven improvement, Olivia's goal is turning uncertainty into better decisions."
    },
    {
        "name": "Rebecca 'Becks' Eshun",
        "role": "Data Scientist/Geologist",
        "image": "https://media.licdn.com/dms/image/v2/D4D03AQEoPQaXr9em5A/profile-displayphoto-crop_800_800/B4DZwT3q4CIgAI-/0/1769859887587?e=1782950400&v=beta&t=usNysP1Txyu7lbiOPDjHyrnFNQW26gInpmrDsH3dEdI",
        "bio": "With a background in Geography, Rebecca is passionate about using data and technology to address agricultural challenges."
    }
]

# 5. Dynamic Grid Layout for Team Profile Cards
cols_1 = st.columns(len(team_members_1))

for index_1, member_1 in enumerate(team_members_1):
    github = ['https://github.com/Ena753',
              'https://github.com/mateyolivia-maker', 'https://github.com/Eshun-Rebecca']
    with cols_1[index_1]:
        # Flexbox layout wrap for the card container
        st.markdown(f"""
        <div class="team-card">
            <img src="{member_1['image']}" style="border-radius: 50%; width: 110px; height: 110px; object-fit: cover;">
            <div class="member-name">{member_1['name']}</div>
            <div class="member-role">{member_1['role']}</div>
            <p class="member-bio">{member_1['bio']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Interactive Streamlit widget mapped directly under each individual card
        st.link_button("GitHub", github[index_1],
                       use_container_width=True, type='primary')
        # if st.button(f"View Projects", key=f"btn_{index_1}", use_container_width=True):
        #     st.info(
        #         f"Showing portfolio links and case studies for **{member_1['name']}** below shortly!")


# 6. Team Data: Males
team_members_2 = [
    {
        "name": "Kwame 'K.B' Nwanwah",
        "role": "Data Scientist/Statistician",
        "image": "https://avatars.githubusercontent.com/u/12522322?v=4",
        "bio": "With a degree in Mathematics and Statistics, Kwame likes to work with numbers because they have no opinions. Garbage in, garbage out."
    },
    {
        "name": "Robert 'Ing RAKE' Agbo",
        "role": "Data Scientist/Electrical Engineer",
        "image": "https://media.licdn.com/dms/image/v2/D4D03AQEDIu00SMv-DQ/profile-displayphoto-crop_800_800/B4DZmSMEJbH0AI-/0/1759094262817?e=1782950400&v=beta&t=dRbrPj90mPN3xEBfjjy4994_H1DMOEY85jV_OTePbJI",
        "bio": "As an Electrical Engineer and project and operations management professional, Robert leverages data science to address energy, climate, and food security challenges."
    }
]

# 7. Dynamic Grid Layout for Team Profile Cards
cols_2 = st.columns([len(team_members_2), len(team_members_2)])

for index_2, member_2 in enumerate(team_members_2):
    github = ['https://github.com/nwanwahkwame', 'https://github.com/Ing-RAKE']
    with cols_2[index_2]:
        # Flexbox layout wrap for the card container
        st.markdown(f"""
        <div class="team-card">
            <img src="{member_2['image']}" style="border-radius: 50%; width: 110px; height: 110px; object-fit: cover;">
            <div class="member-name">{member_2['name']}</div>
            <div class="member-role">{member_2['role']}</div>
            <p class="member-bio">{member_2['bio']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Interactive Streamlit widget mapped directly under each individual card
        st.link_button("GitHub", github[index_2],
                       use_container_width=True, type='primary')
        # if st.button(f"View Projects", key=f"btn_{member_2}", use_container_width=True):
        #     st.link_button("Go to Google", "https://google.com")
        #     st.link_button("Go to Google", "https://google.com")

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">The Motivation</div>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 5])
with col1:
    st.write("""
             **Team KORRE** was born out of passion and urgency; passion to see the Agricultural Sector evolve, urgency to see it thrive. 
             
             


             As a group, **KORRE** decided to tackle  post-harvest losses by building a digital market place that connects farmers directly with buyers and industry processors, 
             thereby cutting down on food waste.
             

             
             
             This ensures that more produced food actually reaches the market, supporting food security and promoting sustainable food systems.
             This is how **Team KORRE** was born.""")
with col2:
    st.image('../app/images/group.jpg')
