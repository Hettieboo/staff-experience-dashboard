# ----- CORRELATION ANALYSIS -----
with tab3:
    st.markdown("### Correlation Analysis: Numeric Survey Metrics")
    
    mapping = {
        'Not at all':1, 'Slightly':2, 'Somewhat':3, 'Moderately':4, 'Extremely':5,
        'No':0, 'Yes':1
    }
    
    numeric_df = filtered_df.copy()
    for col in ['Work_Fulfillment', 'Recognition', 'Growth_Potential']:
        numeric_df[col+'_Score'] = numeric_df[col].map(lambda x: mapping.get(str(x), np.nan))
    
    numeric_cols = ['Work_Fulfillment_Score', 'Recognition_Score', 'Growth_Potential_Score', 'Recommendation_Score']
    corr_matrix = numeric_df[numeric_cols].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdYlGn',
        title="Correlation Analysis of Survey Metrics",
        aspect="auto"
    )
    fig_corr.update_layout(
        margin=dict(l=50, r=50, t=100, b=50),
        height=500
    )
    st.plotly_chart(fig_corr, use_container_width=True)
