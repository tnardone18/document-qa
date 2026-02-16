import streamlit as st
st.title('IST 488 Labs')
lab1 = st.Page('Labs/Lab1.py', title = 'Lab1', icon = '💻')
lab2 = st.Page('Labs/Lab2.py', title = 'Lab2', icon = '💻')
lab3 = st.Page('Labs/Lab3.py', title = 'Lab3', icon = '💻')
lab4 = st.Page('Labs/Lab4.py', title = 'Lab4', icon = '💻')
lab5 = st.Page('Labs/Lab5.py', title = 'Lab5', icon = '💻', default = True)


pg = st.navigation([lab1, lab2, lab3, lab4, lab5])
st.set_page_config(page_title = 'IST 488 Labs',
                   initial_sidebar_state='expanded')
pg.run()
