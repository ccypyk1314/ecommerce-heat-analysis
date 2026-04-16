import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats

# ==========================================
# 页面配置与全局样式
# ==========================================
st.set_page_config(
    page_title="电商商品热度洞察系统",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 100%;
    }
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 4px 20px 0 rgba(31, 38, 135, 0.08);
        margin-bottom: 16px;
    }
    .hero-title {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
    }
    .tag-hot { background: #fee2e2; color: #dc2626; }
    .tag-warm { background: #fef3c7; color: #d97706; }
    .tag-cold { background: #dbeafe; color: #2563eb; }
    .filter-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 数据加载
# ==========================================
@st.cache_data(persist=True, show_spinner=False)
def load_data():
    df = pd.read_csv('item_features.csv')
    numeric_cols = ['heat_score', 'uv', 'clicks', 'favorites', 'carts', 'purchases', 
                   'overall_conversion', 'cat_id']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()

# ==========================================
# 侧边栏 - 优化筛选器
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #1e3a8a; margin: 0; font-size: 1.4rem;">📊 电商洞察</h2>
        <p style="color: #64748b; font-size: 0.8rem; margin-top: 5px;">智能决策支持系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio("导航菜单", [
        "🏠 全景数据大屏", 
        "🔥 热度多维分析", 
        "🎯 转化漏斗洞察",
        "📈 统计检验报告",
        "🔍 智能商品探查"
    ], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### ⚡ 快速筛选")
    
    selected_cat = st.multiselect(
        "类目筛选", 
        options=sorted(df['cat_id'].unique()),
        default=[],
        help="选择特定类目查看数据"
    )
    
    heat_min, heat_max = float(df['heat_score'].min()), float(df['heat_score'].max())
    heat_range = st.slider(
        "热度得分区间",
        heat_min, 
        heat_max,
        (heat_min, heat_max),
        help="拖动滑块筛选热度范围"
    )
    
    temp_df = df.copy()
    if selected_cat:
        temp_df = temp_df[temp_df['cat_id'].isin(selected_cat)]
    temp_df = temp_df[(temp_df['heat_score'] >= heat_range[0]) & (temp_df['heat_score'] <= heat_range[1])]
    
    st.markdown(f"""
    <div class="filter-stats">
        <div style="font-size: 0.8rem; opacity: 0.9;">当前筛选结果</div>
        <div style="font-size: 1.5rem; font-weight: 700;">{len(temp_df):,}</div>
        <div style="font-size: 0.75rem; opacity: 0.8;">件商品</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 重置筛选", key="reset_filter"):
        st.rerun()

# 应用筛选
filtered_df = df.copy()
if selected_cat:
    filtered_df = filtered_df[filtered_df['cat_id'].isin(selected_cat)]
filtered_df = filtered_df[
    (filtered_df['heat_score'] >= heat_range[0]) & 
    (filtered_df['heat_score'] <= heat_range[1])
]

# ==========================================
# 页面1：全景数据大屏
# ==========================================
if page == "🏠 全景数据大屏":
    st.markdown('<h1 class="hero-title">电商商品热度全景大屏</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">基于统计学的商品表现可视化分析 | 当前展示: {len(filtered_df):,}件商品</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_data = [
        ("总商品数", f"{len(filtered_df):,}", f"覆盖{filtered_df['cat_id'].nunique()}个类目", "#3b82f6"),
        ("热度变异系数", f"{filtered_df['heat_score'].std() / filtered_df['heat_score'].mean():.2f}", "离散程度指标", "#f59e0b"),
        ("平均热度得分", f"{filtered_df['heat_score'].mean():.2f}", "加权行为分", "#10b981"),
        ("最热类目", f"#{int(filtered_df.groupby('cat_id')['heat_score'].mean().idxmax()) if len(filtered_df) > 0 else 'N/A'}", "平均热度领先", "#8b5cf6")
    ]
    
    for col, (title, value, subtitle, color) in zip([col1, col2, col3, col4], metrics_data):
        col.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid {color};">
            <h3 style="margin: 0; color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">{title}</h3>
            <p style="font-size: 1.6rem; font-weight: 700; color: #1e293b; margin: 6px 0;">{value}</p>
            <span style="font-size: 0.7rem; color: {color}; font-weight: 500;">{subtitle}</span>
        </div>
        """, unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        with st.container():
            st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b;">📊 热度分布直方图</div>', unsafe_allow_html=True)
            
            fig1 = px.histogram(
                filtered_df, x='heat_score', nbins=50,
                labels={'heat_score': '热度得分', 'count': '商品数量'},
                color_discrete_sequence=['#3b82f6'],
                template='plotly_white'
            )
            fig1.add_vline(x=filtered_df['heat_score'].mean(), line_dash="dash", line_color="#dc2626",
                          annotation_text=f"均值: {filtered_df['heat_score'].mean():.2f}", annotation_font_size=10)
            fig1.add_vline(x=filtered_df['heat_score'].median(), line_dash="dot", line_color="#059669",
                          annotation_text=f"中位数: {filtered_df['heat_score'].median():.2f}", annotation_font_size=10)
            fig1.update_layout(
                height=350,
                margin=dict(l=40, r=20, t=30, b=40),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    
    with col_right:
        with st.container():
            st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b;">🏆 类目热度TOP10</div>', unsafe_allow_html=True)
            
            cat_stats = filtered_df.groupby('cat_id').agg({
                'heat_score': 'mean',
                'item_id': 'count'
            }).reset_index()
            cat_stats.columns = ['cat_id', 'avg_heat', 'item_count']
            cat_stats = cat_stats.nlargest(10, 'avg_heat').sort_values('avg_heat', ascending=True)
            
            fig2 = px.bar(
                cat_stats, 
                y='cat_id', 
                x='avg_heat',
                orientation='h',
                color='avg_heat',
                color_continuous_scale='Blues',
                text=cat_stats['avg_heat'].round(2),
                template='plotly_white'
            )
            fig2.update_traces(textposition='outside', textfont_size=9)
            fig2.update_layout(
                height=350,
                margin=dict(l=60, r=20, t=30, b=40),
                yaxis_title="",
                xaxis_title="平均热度",
                coloraxis_showscale=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(type='category', tickfont=dict(size=9))
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    with st.container():
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b;">🫧 商品表现三维散点图（UV × 转化率 × 热度）</div>', unsafe_allow_html=True)
        
        sample_df = filtered_df.sample(min(1500, len(filtered_df)), random_state=42)
        
        fig3 = px.scatter(
            sample_df,
            x='uv',
            y='overall_conversion',
            size='heat_score',
            color='heat_score',
            color_continuous_scale='RdYlBu_r',
            hover_name='item_id',
            hover_data={'cat_id': True, 'clicks': True, 'purchases': True, 'heat_score': ':.2f'},
            labels={'uv': '独立访客数 (UV)', 'overall_conversion': '转化率', 'heat_score': '热度得分'},
            template='plotly_white'
        )
        fig3.update_layout(
            title=dict(text='气泡大小=热度得分 · 颜色=热度等级', font=dict(size=11, color='#64748b'), x=0.5),
            height=420,
            margin=dict(l=50, r=50, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_colorbar=dict(title="热度", thickness=12, len=0.6)
        )
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

# ==========================================
# 页面2：热度多维分析（修复版）
# ==========================================
elif page == "🔥 热度多维分析":
    st.markdown('<h1 class="hero-title">商品热度多维透视</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 平行坐标对比", "🎯 指标子弹图", "🗂️ 类目树状图"])
    
    # Tab1: 平行坐标图（修复版 - 移除width属性）
    with tab1:
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b; font-size: 1.1rem;">📊 多维度平行坐标对比（Top10商品）</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.85rem; margin-bottom: 15px;">悬停查看具体数值，拖动坐标轴筛选框可高亮特定范围</p>', unsafe_allow_html=True)
        
        top_items = filtered_df.nlargest(10, 'heat_score').copy()
        
        dims = ['heat_score', 'uv', 'clicks', 'favorites', 'carts', 'overall_conversion']
        dim_labels = {
            'heat_score': '热度得分',
            'uv': 'UV访问量',
            'clicks': '点击次数',
            'favorites': '收藏数量',
            'carts': '加购数量',
            'overall_conversion': '整体转化率'
        }
        
        for dim in dims:
            if dim in top_items.columns and top_items[dim].std() > 0:
                top_items[f'{dim}_norm'] = (top_items[dim] - top_items[dim].min()) / (top_items[dim].max() - top_items[dim].min())
            else:
                top_items[f'{dim}_norm'] = 0
        
        dimensions_list = []
        for dim in dims:
            dimensions_list.append(
                dict(
                    range=[0, 1],
                    label=dim_labels[dim],
                    values=top_items[f'{dim}_norm'],
                    tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1],
                    ticktext=['0%', '20%', '40%', '60%', '80%', '100%']
                )
            )
        
        # 修复：Parcoords不支持width和opacity属性
        fig_parallel = go.Figure(data=go.Parcoords(
            line=dict(
                color=top_items['heat_score'],
                colorscale='Viridis',
                showscale=True,
                cmin=top_items['heat_score'].min(),
                cmax=top_items['heat_score'].max(),
                colorbar=dict(title="热度得分", thickness=15)
            ),
            dimensions=dimensions_list,
            unselected=dict(line=dict(color='lightgray', opacity=0.2)),
            labelfont=dict(size=13, color="#1e293b", family="Arial Black"),
            tickfont=dict(size=11, color="#475569"),
            rangefont=dict(size=10, color="#64748b")
        ))
        
        fig_parallel.update_layout(
            height=500,
            margin=dict(l=120, r=100, t=50, b=60),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title=dict(
                text="颜色深浅代表热度得分高低 | 各维度已归一化处理",
                font=dict(size=12, color="#64748b"),
                x=0.5,
                y=0.02
            )
        )
        st.plotly_chart(fig_parallel, use_container_width=True, config={'displayModeBar': False})
        
        with st.expander("📋 查看Top10商品详细数据"):
            display_cols = ['item_id', 'cat_id'] + dims
            st.dataframe(
                top_items[display_cols].rename(columns=dim_labels),
                use_container_width=True,
                hide_index=True
            )
    
    # Tab2: 子弹图（简化版）
    with tab2:
        col_select, col_chart = st.columns([1, 4])
        
        with col_select:
            st.markdown("**选择对比商品**")
            item_options = filtered_df.nlargest(20, 'heat_score')['item_id'].tolist()
            selected_items = st.multiselect(
                "商品ID(最多2个)",
                options=item_options,
                default=item_options[:1] if len(item_options) >= 1 else [],
                max_selections=2
            )
            
            st.markdown("**对比指标**")
            metrics_compare = st.multiselect(
                "选择指标",
                options=['heat_score', 'uv', 'clicks', 'favorites', 'carts', 'overall_conversion'],
                default=['heat_score', 'uv', 'overall_conversion'],
                format_func=lambda x: {'heat_score': '热度得分', 'uv': 'UV', 'clicks': '点击数', 
                                     'favorites': '收藏数', 'carts': '加购数', 'overall_conversion': '转化率'}[x]
            )
        
        with col_chart:
            if selected_items and metrics_compare:
                fig_bullet = go.Figure()
                
                colors = ['#2563eb', '#dc2626']
                
                for idx, item_id in enumerate(selected_items[:2]):
                    item = filtered_df[filtered_df['item_id'] == item_id].iloc[0]
                    
                    for metric_idx, metric in enumerate(metrics_compare):
                        actual = item[metric]
                        
                        max_val = filtered_df[metric].max()
                        normalized_actual = (actual / max_val) * 100 if max_val > 0 else 0
                        
                        fig_bullet.add_trace(go.Bar(
                            x=[100],
                            y=[f"{metric}_{idx}"],
                            orientation='h',
                            marker_color='#e2e8f0',
                            showlegend=False,
                            width=0.6,
                            hoverinfo='skip'
                        ))
                        
                        fig_bullet.add_trace(go.Bar(
                            x=[normalized_actual],
                            y=[f"{metric}_{idx}"],
                            orientation='h',
                            name=f'商品{item_id}',
                            marker_color=colors[idx],
                            text=f'{actual:.1f}',
                            textposition='outside',
                            showlegend=(metric_idx == 0),
                            width=0.6
                        ))
                
                y_labels = []
                for metric in metrics_compare:
                    label = {'heat_score': '热度得分', 'uv': 'UV', 'clicks': '点击数', 
                            'favorites': '收藏数', 'carts': '加购数', 'overall_conversion': '转化率'}[metric]
                    for i in range(len(selected_items[:2])):
                        y_labels.append(f"{label}")
                
                fig_bullet.update_layout(
                    barmode='overlay',
                    height=300 + len(metrics_compare) * 80,
                    margin=dict(l=100, r=50, t=50, b=50),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
                    xaxis=dict(title="相对表现(%)", range=[0, 110], gridcolor='#e2e8f0'),
                    yaxis=dict(showticklabels=False),
                    showlegend=True
                )
                st.plotly_chart(fig_bullet, use_container_width=True, config={'displayModeBar': False})
                
                comparison_data = []
                for item_id in selected_items[:2]:
                    item = filtered_df[filtered_df['item_id'] == item_id].iloc[0]
                    row = {'商品ID': item_id}
                    for metric in metrics_compare:
                        row[metric] = item[metric]
                    comparison_data.append(row)
                
                comp_df = pd.DataFrame(comparison_data)
                comp_df = comp_df.rename(columns={
                    'heat_score': '热度得分', 'uv': 'UV', 'clicks': '点击数',
                    'favorites': '收藏数', 'carts': '加购数', 'overall_conversion': '转化率'
                })
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
            else:
                st.info("请选择至少一个商品和指标进行对比")
    
    # Tab3: 树状图（修复Interval序列化问题）
    with tab3:
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b; font-size: 1.1rem;">🗂️ 类目×热度层级树状图</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.85rem; margin-bottom: 15px;">矩形大小表示商品数量，颜色深浅表示平均热度</p>', unsafe_allow_html=True)
        
        df_temp = filtered_df.copy()
        
        # 修复：使用pd.cut并转换为字符串，避免Interval类型JSON序列化错误
        try:
            df_temp['heat_level'] = pd.cut(df_temp['heat_score'], 
                                          bins=[0, 2, 5, 10, 20, float('inf')],
                                          labels=['冷门(0-2)', '一般(2-5)', '热门(5-10)', '爆款(10-20)', '超级爆款(20+)'])
            # 关键修复：转换为字符串类型
            df_temp['heat_level'] = df_temp['heat_level'].astype(str)
        except:
            # 备用方案：手动分类
            df_temp['heat_level'] = '未知'
            df_temp.loc[df_temp['heat_score'] <= 2, 'heat_level'] = '冷门(0-2)'
            df_temp.loc[(df_temp['heat_score'] > 2) & (df_temp['heat_score'] <= 5), 'heat_level'] = '一般(2-5)'
            df_temp.loc[(df_temp['heat_score'] > 5) & (df_temp['heat_score'] <= 10), 'heat_level'] = '热门(5-10)'
            df_temp.loc[(df_temp['heat_score'] > 10) & (df_temp['heat_score'] <= 20), 'heat_level'] = '爆款(10-20)'
            df_temp.loc[df_temp['heat_score'] > 20, 'heat_level'] = '超级爆款(20+)'
        
        treemap_data = df_temp.groupby(['cat_id', 'heat_level']).agg({
            'item_id': 'count',
            'heat_score': 'mean'
        }).reset_index()
        treemap_data.columns = ['cat_id', 'heat_level', 'count', 'avg_heat']
        
        cat_counts = df_temp['cat_id'].value_counts()
        top_cats = cat_counts.head(20).index
        treemap_data = treemap_data[treemap_data['cat_id'].isin(top_cats)]
        
        fig_treemap = px.treemap(
            treemap_data,
            path=[px.Constant("全部类目"), 'cat_id', 'heat_level'],
            values='count',
            color='avg_heat',
            color_continuous_scale='RdYlBu_r',
            template='plotly_white',
            hover_data={'count': True, 'avg_heat': ':.2f'}
        )
        
        fig_treemap.update_traces(
            textinfo="label+value",
            textfont=dict(size=11),
            hovertemplate='<b>%{label}</b><br>商品数: %{value}<br>平均热度: %{color:.2f}<extra></extra>'
        )
        
        fig_treemap.update_layout(
            height=550,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_colorbar=dict(title="平均热度", thickness=15)
        )
        st.plotly_chart(fig_treemap, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# 页面3：转化漏斗洞察（修复版 - 收藏/加购分流）
# ==========================================
elif page == "🎯 转化漏斗洞察":
    st.markdown('<h1 class="hero-title">用户行为转化漏斗</h1>', unsafe_allow_html=True)
    
    total_uv = filtered_df['uv'].sum()
    total_clicks = filtered_df['clicks'].sum()
    total_favorites = filtered_df['favorites'].sum()
    total_carts = filtered_df['carts'].sum()
    total_purchases = filtered_df['purchases'].sum()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("👁️ 总曝光", total_uv, "#94a3b8"),
        ("👆 总点击", total_clicks, "#3b82f6"),
        ("❤️ 总收藏", total_favorites, "#ec4899"),
        ("🛒 总加购", total_carts, "#f59e0b"),
        ("💰 总购买", total_purchases, "#10b981")
    ]
    
    for col, (label, value, color) in zip([col1, col2, col3, col4, col5], metrics):
        col.markdown(f"""
        <div class="glass-card" style="border-top: 3px solid {color}; text-align: center; padding: 15px;">
            <h3 style="margin: 0; color: #64748b; font-size: 0.8rem;">{label}</h3>
            <p style="font-size: 1.4rem; font-weight: 700; color: {color}; margin: 8px 0;">{value:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

    # 分支桑基图：点击后分为"直接加购"和"收藏后加购"两条路径
    with st.container():
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b;">🌊 用户行为分流桑基图（点击后分两条路径）</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.85rem; margin-bottom: 15px;">蓝色=直接转化路径 | 粉色=收藏转化路径 | 灰色=流失</p>', unsafe_allow_html=True)
        
        sample_size = min(5000, len(filtered_df))
        sample_df = filtered_df.sample(sample_size, random_state=42)
        
        # 计算各节点人数
        exposure = sample_size
        click_n = (sample_df['clicks'] > 0).sum()
        
        # 点击后的分流
        fav_n = (sample_df['favorites'] > 0).sum()
        direct_cart_n = ((sample_df['carts'] > 0) & (sample_df['favorites'] == 0)).sum()
        fav_then_cart_n = ((sample_df['favorites'] > 0) & (sample_df['carts'] > 0)).sum()
        
        # 购买节点
        direct_buy_n = ((sample_df['purchases'] > 0) & (sample_df['favorites'] == 0)).sum()
        fav_buy_n = ((sample_df['purchases'] > 0) & (sample_df['favorites'] > 0)).sum()
        
        # 流失计算
        loss_click = exposure - click_n
        loss_after_click = click_n - fav_n - direct_cart_n
        loss_fav = fav_n - fav_then_cart_n
        total_cart = direct_cart_n + fav_then_cart_n
        total_buy = direct_buy_n + fav_buy_n
        loss_cart = total_cart - total_buy
        
        fig_sankey = go.Figure(data=[go.Sankey(
            arrangement="snap",
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color="white", width=2),
                label=["📢 曝光", "👆 点击", "❤️ 收藏", "🛒 直接加购", "🛒 收藏后加购", "💰 直接购买", "💰 收藏后购买", "💨 流失"],
                color=["#94a3b8", "#3b82f6", "#ec4899", "#f59e0b", "#f97316", "#10b981", "#059669", "#cbd5e1"],
                x=[0.05, 0.2, 0.4, 0.4, 0.6, 0.8, 0.8, 0.6],
                y=[0.5, 0.5, 0.25, 0.75, 0.5, 0.75, 0.25, 0.1]
            ),
            link=dict(
                source=[0, 1, 1, 2, 2, 3, 4, 3, 4],
                target=[1, 2, 3, 4, 7, 5, 6, 7, 7],
                value=[click_n, fav_n, direct_cart_n, fav_then_cart_n, loss_fav, direct_buy_n, fav_buy_n, 
                       direct_cart_n - direct_buy_n, fav_then_cart_n - fav_buy_n],
                color=[
                    "rgba(59, 130, 246, 0.6)",
                    "rgba(236, 72, 153, 0.6)",
                    "rgba(59, 130, 246, 0.6)",
                    "rgba(245, 158, 11, 0.6)",
                    "rgba(203, 213, 225, 0.3)",
                    "rgba(16, 185, 129, 0.8)",
                    "rgba(5, 150, 105, 0.8)",
                    "rgba(203, 213, 225, 0.3)",
                    "rgba(203, 213, 225, 0.3)"
                ],
                hovertemplate='从 %{source.label} 到 %{target.label}<br>人数: %{value}<extra></extra>'
            )
        )])
        
        fig_sankey.update_layout(
            template='plotly_white',
            height=550,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title=dict(
                text="点击后用户分流：直接加购 vs 先收藏后加购",
                font=dict(size=14, color="#374151"),
                x=0.5
            )
        )
        st.plotly_chart(fig_sankey, use_container_width=True, config={'displayModeBar': False})
        
        col_conv1, col_conv2, col_conv3 = st.columns(3)
        with col_conv1:
            direct_cart_rate = direct_cart_n/click_n*100 if click_n > 0 else 0
            st.metric("直接加购率", f"{direct_cart_rate:.1f}%", f"{direct_cart_n}人")
        with col_conv2:
            fav_rate = fav_n/click_n*100 if click_n > 0 else 0
            st.metric("收藏率", f"{fav_rate:.1f}%", f"{fav_n}人")
        with col_conv3:
            fav_to_cart_rate = fav_then_cart_n/fav_n*100 if fav_n > 0 else 0
            st.metric("收藏→加购转化", f"{fav_to_cart_rate:.1f}%", f"{fav_then_cart_n}人")
    
    # 横向条形图替代漏斗图（避免收藏数据被压缩）
    with st.container():
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b;">📊 关键转化步骤对比（横向条形图）</div>', unsafe_allow_html=True)
        
        stages = ["👁️ 曝光", "👆 点击", "❤️ 收藏", "🛒 总加购", "💰 购买"]
        values = [total_uv, total_clicks, total_favorites, total_carts, total_purchases]
        colors_bar = ["#94a3b8", "#3b82f6", "#ec4899", "#f59e0b", "#10b981"]
        
        fig_bar = go.Figure()
        
        for i, (stage, val, color) in enumerate(zip(stages, values, colors_bar)):
            fig_bar.add_trace(go.Bar(
                y=[stage],
                x=[val],
                orientation='h',
                marker_color=color,
                text=f"{val:,.0f}",
                textposition='outside',
                name=stage,
                showlegend=False
            ))
        
        fig_bar.update_layout(
            template='plotly_white',
            height=400,
            margin=dict(l=80, r=100, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="用户数量", gridcolor='#e2e8f0'),
            yaxis=dict(title="", autorange="reversed")
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# 页面4：统计检验报告（新增）
# ==========================================
elif page == "📈 统计检验报告":
    st.markdown('<h1 class="hero-title">统计学检验分析报告</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">基于假设检验的商品热度差异分析</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 T检验分析", "📈 方差分析", "📉 相关性分析"])
    
    with tab1:
        st.markdown("### 两独立样本T检验")
        st.markdown("检验不同热度等级商品在转化率上是否存在显著差异")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cat_list = sorted(filtered_df['cat_id'].unique())
            cat_a = st.selectbox("选择类目A（高热度组）", cat_list, index=0)
            cat_b = st.selectbox("选择类目B（对照组）", cat_list, index=min(1, len(cat_list)-1))
        
        with col2:
            metric = st.selectbox(
                "选择检验指标",
                ['heat_score', 'overall_conversion', 'uv', 'clicks'],
                format_func=lambda x: {'heat_score': '热度得分', 'overall_conversion': '转化率', 
                                     'uv': 'UV访问量', 'clicks': '点击数'}[x]
            )
        
        group_a = filtered_df[filtered_df['cat_id'] == cat_a][metric].dropna()
        group_b = filtered_df[filtered_df['cat_id'] == cat_b][metric].dropna()
        
        if len(group_a) > 1 and len(group_b) > 1:
            t_stat, p_value = stats.ttest_ind(group_a, group_b)
            
            result_col1, result_col2, result_col3 = st.columns(3)
            with result_col1:
                st.metric("T统计量", f"{t_stat:.3f}")
            with result_col2:
                st.metric("P值", f"{p_value:.4f}", 
                         "显著" if p_value < 0.05 else "不显著",
                         delta_color="inverse" if p_value < 0.05 else "normal")
            with result_col3:
                significance = "差异显著" if p_value < 0.05 else "差异不显著"
                st.metric("检验结论", significance)
            
            fig = go.Figure()
            fig.add_trace(go.Box(y=group_a, name=f'类目{cat_a}', marker_color='#3b82f6'))
            fig.add_trace(go.Box(y=group_b, name=f'类目{cat_b}', marker_color='#f59e0b'))
            
            fig.update_layout(
                title=f"{metric}分布对比",
                yaxis_title=metric,
                height=400,
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            **检验说明**：  
            - 原假设H₀：类目{cat_a}与类目{cat_b}的{metric}均值无显著差异  
            - 备择假设H₁：两者存在显著差异  
            - 显著性水平α=0.05  
            - 结论：{'拒绝原假设，两组存在统计学显著差异' if p_value < 0.05 else '不拒绝原假设，两组无显著差异'}
            """)
    
    with tab2:
        st.markdown("### 单因素方差分析（ANOVA）")
        st.markdown("检验多个类目间热度得分是否存在显著差异")
        
        top_cats = filtered_df['cat_id'].value_counts().head(5).index.tolist()
        cat_groups = [filtered_df[filtered_df['cat_id'] == cat]['heat_score'].dropna() for cat in top_cats]
        
        if all(len(g) > 1 for g in cat_groups):
            f_stat, p_value = stats.f_oneway(*cat_groups)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("F统计量", f"{f_stat:.3f}")
            with col2:
                st.metric("P值", f"{p_value:.4f}",
                         "显著" if p_value < 0.05 else "不显著",
                         delta_color="inverse" if p_value < 0.05 else "normal")
            
            cat_means = filtered_df[filtered_df['cat_id'].isin(top_cats)].groupby('cat_id')['heat_score'].agg(['mean', 'std', 'count'])
            st.markdown("#### 各类目热度统计")
            st.dataframe(cat_means, use_container_width=True)
            
            fig_violin = px.violin(
                filtered_df[filtered_df['cat_id'].isin(top_cats)],
                x='cat_id', y='heat_score',
                box=True, points="all",
                color='cat_id',
                template='plotly_white',
                title="各类目热度分布小提琴图"
            )
            fig_violin.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_violin, use_container_width=True)
    
    with tab3:
        st.markdown("### Pearson相关性分析")
        st.markdown("探索各指标间的线性相关关系")
        
        corr_cols = ['heat_score', 'uv', 'clicks', 'favorites', 'carts', 'purchases', 'overall_conversion']
        corr_matrix = filtered_df[corr_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            template='plotly_white',
            title="指标相关性热力图",
            labels=dict(color="相关系数")
        )
        fig_corr.update_traces(texttemplate="%{z:.2f}", textfont=dict(size=10))
        fig_corr.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.markdown("#### 强相关指标对（|r| > 0.7）")
        strong_corr = []
        for i in range(len(corr_cols)):
            for j in range(i+1, len(corr_cols)):
                r = corr_matrix.iloc[i, j]
                if abs(r) > 0.7:
                    strong_corr.append({
                        '指标1': corr_cols[i],
                        '指标2': corr_cols[j],
                        '相关系数': f"{r:.3f}",
                        '相关强度': '极强正相关' if r > 0.9 else ('强正相关' if r > 0.7 else '强负相关')
                    })
        
        if strong_corr:
            st.dataframe(pd.DataFrame(strong_corr), use_container_width=True, hide_index=True)
        else:
            st.info("未发现强相关指标对（|r| > 0.7）")

# ==========================================
# 页面5：智能商品探查（新增）
# ==========================================
elif page == "🔍 智能商品探查":
    st.markdown('<h1 class="hero-title">智能商品探查引擎</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">深度挖掘商品特征与潜在价值</p>', unsafe_allow_html=True)
    
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_id = st.text_input("🔍 输入商品ID搜索", placeholder="例如：800913")
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("开始探查", type="primary", use_container_width=True)
    
    if not search_id:
        st.markdown("### 🔥 热度榜TOP10")
        top10 = filtered_df.nlargest(10, 'heat_score')[['item_id', 'cat_id', 'heat_score', 'uv', 'overall_conversion']]
        
        top10.insert(0, '排名', range(1, len(top10)+1))
        
        st.dataframe(
            top10,
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.NumberColumn("🏆", width="small"),
                "item_id": st.column_config.TextColumn("商品ID"),
                "cat_id": st.column_config.NumberColumn("类目"),
                "heat_score": st.column_config.ProgressColumn(
                    "热度得分",
                    min_value=0,
                    max_value=float(filtered_df['heat_score'].max()),
                    format="%.2f"
                ),
                "uv": st.column_config.NumberColumn("UV", format="%d"),
                "overall_conversion": st.column_config.NumberColumn("转化率", format="%.2f%%")
            }
        )
    
    if search_id and search_btn:
        item_data = filtered_df[filtered_df['item_id'].astype(str) == str(search_id)]
        
        if len(item_data) == 0:
            st.error(f"未找到商品ID: {search_id}")
        else:
            item = item_data.iloc[0]
            
            st.markdown(f"### 📦 商品 #{search_id} 详情报告")
            
            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
            with info_col1:
                st.metric("所属类目", f"类目{item['cat_id']}")
            with info_col2:
                heat_rank = (filtered_df['heat_score'] > item['heat_score']).sum() + 1
                st.metric("热度排名", f"第{heat_rank}名", f"Top {heat_rank/len(filtered_df)*100:.1f}%")
            with info_col3:
                st.metric("热度得分", f"{item['heat_score']:.2f}")
            with info_col4:
                st.metric("整体转化率", f"{item['overall_conversion']:.2f}%")
            
            st.markdown("#### 📊 详细指标")
            
            metric_cols = st.columns(5)
            metrics_display = [
                ("UV访问量", int(item['uv']), "👁️"),
                ("点击数", int(item['clicks']), "👆"),
                ("收藏数", int(item['favorites']), "❤️"),
                ("加购数", int(item['carts']), "🛒"),
                ("购买数", int(item['purchases']), "💰")
            ]
            
            for col, (name, value, icon) in zip(metric_cols, metrics_display):
                with col:
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div style="font-size: 1.5rem;">{icon}</div>
                        <div style="font-size: 0.8rem; color: #64748b; margin-top: 5px;">{name}</div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: #1e293b;">{value:,}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("#### 🏷️ 同类目表现对比")
            same_cat = filtered_df[filtered_df['cat_id'] == item['cat_id']]
            
            if len(same_cat) > 1:
                compare_metrics = ['heat_score', 'uv', 'overall_conversion', 'favorites', 'carts']
                
                fig_radar = go.Figure()
                
                item_values = [item[m] for m in compare_metrics]
                cat_means = [same_cat[m].mean() for m in compare_metrics]
                cat_top10 = [same_cat[m].quantile(0.9) for m in compare_metrics]
                
                max_vals = [same_cat[m].max() for m in compare_metrics]
                item_norm = [item_values[i]/max_vals[i]*100 for i in range(len(compare_metrics))]
                cat_norm = [cat_means[i]/max_vals[i]*100 for i in range(len(compare_metrics))]
                top_norm = [cat_top10[i]/max_vals[i]*100 for i in range(len(compare_metrics))]
                
                labels = ['热度得分', 'UV访问量', '转化率', '收藏数', '加购数']
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=item_norm + [item_norm[0]],
                    theta=labels + [labels[0]],
                    fill='toself',
                    name=f'商品{search_id}',
                    line_color='#2563eb',
                    fillcolor='rgba(37, 99, 235, 0.3)'
                ))
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=cat_norm + [cat_norm[0]],
                    theta=labels + [labels[0]],
                    fill='toself',
                    name='类目均值',
                    line_color='#94a3b8',
                    fillcolor='rgba(148, 163, 184, 0.2)'
                ))
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=top_norm + [top_norm[0]],
                    theta=labels + [labels[0]],
                    fill='none',
                    name='类目Top10%',
                    line_color='#f59e0b',
                    line_dash='dash'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    showlegend=True,
                    template='plotly_white',
                    height=450,
                    paper_bgcolor='rgba(0,0,0,0)',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, x=0.5, xanchor="center")
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                
                st.markdown("#### 💡 智能诊断")
                
                insights = []
                if item['heat_score'] > same_cat['heat_score'].mean():
                    insights.append("✅ 该商品热度**高于**类目平均水平")
                else:
                    insights.append("⚠️ 该商品热度**低于**类目平均水平，建议优化")
                
                if item['overall_conversion'] > same_cat['overall_conversion'].mean():
                    insights.append("✅ 转化率表现**优秀**")
                else:
                    insights.append("⚠️ 转化率有待提升，建议优化详情页或价格策略")
                
                if item['favorites'] > same_cat['favorites'].mean():
                    insights.append("✅ 收藏表现**良好**，用户兴趣度高")
                
                for insight in insights:
                    st.markdown(insight)
            else:
                st.info("该类目下商品数量不足，无法生成对比分析")

# ==========================================
# 页脚
# ==========================================
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 20px;">
    © 2026 电商商品热度分析系统 · 基于统计学方法构建 · 信息可视化设计类参赛作品
</p>
""", unsafe_allow_html=True)
