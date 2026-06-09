# The Reason for starting the project.
# Problem Statement
# Pictures, link to GitHub, link to Linkedin
# Blurb, fun fact.

from utils import inject_css, init_session
import streamlit as st

# 1. Page Configurations
st.set_page_config(
    page_title="About Our Team — AgriMatch",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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


# Team Statistics (Quick Overview)
# col_stat1, col_stat2, col_stat3, col_stat4 = st.columns([2, 2, 2, 2])
# with col_stat1:
#     st.metric(label='Team No.', value='5 Members')
# with col_stat2:
#     st.metric(label="Coffee Consumed", value="Infinite ☕")
# with col_stat3:
#     st.metric(label="Lines of Code Written", value="2000+")
# with col_stat4:
#     st.metric(label='Program', value='Code4Food')


# st.divider()

# 4. Team Data: Females
team_members_1 = [
    {
        "name": "Ena 'Adurowura' Ayimey",
        "role": "Data Scientist",
        "image": "https://4kwallpapers.com/images/walls/thumbs_3t/14893.jpg",
        "bio": "Ena crafts machine learning pipelines and translates messy enterprise data into clear actionable strategies. She's a big woman."
    },
    {
        "name": "Olivia 'Olive' Matey",
        "role": "Data Scientist",
        "image": "https://4kwallpapers.com/images/walls/thumbs_3t/14890.jpg",
        "bio": "Olivia designs high-availability infrastructure layouts and keeps our applications running securely 24/7. She likes cats."
    },
    {
        "name": "Rebecca 'Becks' Eshun",
        "role": "Data Scientist",
        "image": "https://4kwallpapers.com/images/walls/thumbs_3t/14887.jpg",
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
                       use_container_width=True)
        # if st.button(f"View Projects", key=f"btn_{index_1}", use_container_width=True):
        #     st.info(
        #         f"Showing portfolio links and case studies for **{member_1['name']}** below shortly!")


# 6. Team Data: Males
team_members_2 = [
    {
        "name": "Kwame 'K.B' Nwanwah",
        "role": "Data Scientist",
        "image": "https://4kwallpapers.com/images/walls/thumbs_3t/14158.jpg",
        "bio": "With a degree in Mathematics and Statistics, Kwame likes to work with numbers because they have no opinions. Garbage in, garbage out."
    },
    {
        "name": "Robert 'Ing Rake' Agbo",
        "role": "Data Scientist",
        "image": "https://avatars.githubusercontent.com/u/210055536?v=4",
        "bio": "As an Electrical Engineer, Ing Rake  David designs high-availability infrastructure layouts and keeps our applications running securely 24/7."
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
                       use_container_width=True)
        # if st.button(f"View Projects", key=f"btn_{member_2}", use_container_width=True):
        #     st.link_button("Go to Google", "https://google.com")
        #     st.link_button("Go to Google", "https://google.com")

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">The Motivation</div>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 5])
with col1:
    st.write("""Farmers struggle to find a buyer. If a farmer has no guaranteed market outlet, crops sit in suboptimal conditions and rot.
             In short, a lack of immediate marketability creates the post-harvest crisis and reduces the income for the farmer.  Further more, farmers burn agriculture waste such as maize cob , rice husk etc and this a major contribution to the climate change affecting us currently.
             As a group, we have decided to tackle this issue by building a digital market place that connects farmers directly with buyers and industry processors. 
             Thereby cutting down on food waste within the supply chain ensuring that more produced food actually reaches the market, supporting food security and promoting sustainable food systems.
             This is how **Team Tera** was born.""")
with col2:
    st.image('../app/images/group.jpg')
