import streamlit as st


def show_events_list(events_data):
    def load_more():
        now_length = len(st.session_state['displayed_events'])
        se = events_data.sort_values(by='duration', ascending=False)
        st.session_state['displayed_events'].extend(se.iloc[now_length:now_length + 5].to_dict(orient='records'))

    if len(st.session_state['displayed_events']) == 0:
        load_more()
    st.title('Top Events')
    for event in st.session_state['displayed_events']:
        category_name = event['category_name'] if len(event['category_name']) != 0 else 'Uncategorized'
        label_text = f"{event['name'][11:]} - {category_name}"
        delta_color = 'normal' if event['category_score'] > 0 else 'inverse'
        st.metric(label=label_text,
                  value=event['start_datetime'].strftime('%Y-%m-%d %X'),
                  delta=str(event['duration']),
                  delta_color=delta_color,
                  help=event['data'],
                  border=True)
    st.button('Load More >>', type="tertiary", on_click=load_more, key='more_events')


def show_categories_list(category_duration):
    def load_more():
        now_length = len(st.session_state['displayed_categories'])
        sc = category_duration.sort_values(by='duration', ascending=False)
        st.session_state['displayed_categories'].extend(sc.iloc[now_length:now_length + 5].to_dict(orient='records'))

    if len(st.session_state['displayed_categories']) == 0:
        load_more()
    st.title('Top Categories')
    # print(category_duration)
    for category in st.session_state['displayed_categories']:
        delta_color = 'normal' if category['category_score'] > 0 else 'inverse'
        st.metric(
            label=f"Id: {category['category']}, Score: {category['category_score']}",
            value=category['category_name'],
            delta=str(category['duration']),
            delta_color=delta_color,
            border=True)
    st.button('Load More >>', type="tertiary", on_click=load_more, key='more_categories')
