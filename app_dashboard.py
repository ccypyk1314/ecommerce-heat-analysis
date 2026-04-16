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
    .reset-btn {
        background-color: #f3f4f6;
        color: #374151;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 4px 12px;
        font-size: 0.8rem;
        cursor: pointer;
        width: 100%;
        margin-top: 10px;
    }
    .reset-btn:hover {
        background-color: #e5e7eb;
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
    
    # 筛选统计卡片
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = df.copy()
    
    selected_cat = st.multiselect(
        "类目筛选", 
        options=sorted(df['cat_id'].unique()),
        default=[],
        help="选择特定类目查看数据"
    )
    
    # 动态范围计算
    heat_min, heat_max = float(df['heat_score'].min()), float(df['heat_score'].max())
    heat_range = st.slider(
        "热度得分区间",
        heat_min, 
        heat_max,
        (heat_min, heat_max),
        help="拖动滑块筛选热度范围"
    )
    
    # 实时统计
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
        selected_cat = []
        heat_range = (heat_min, heat_max)
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
# 页面1：全景数据大屏（保持优化）
# ==========================================
if page == "🏠 全景数据大屏":
    st.markdown('<h1 class="hero-title">电商商品热度全景大屏</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">基于统计学的商品表现可视化分析 | 当前展示: {len(filtered_df):,}件商品</p>', unsafe_allow_html=True)
    
    # 关键指标（基于筛选数据）
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

    # 图表行1
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

    # 散点图
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
# 页面2：热度多维分析（重大改进）
# ==========================================
elif page == "🔥 热度多维分析":
    st.markdown('<h1 class="hero-title">商品热度多维透视</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 平行坐标对比", "🎯 指标子弹图", "🗂️ 类目树状图"])
    
    # Tab1: 平行坐标图（替代雷达图）
    with tab1:
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b; font-size: 1.1rem;">📊 多维度平行坐标对比（Top10商品）</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.85rem; margin-bottom: 15px;">每条线代表一个商品，不同颜色表示不同热度等级</p>', unsafe_allow_html=True)
        
        # 准备数据：取Top10商品，进行Z-score标准化使各维度可比
        top_items = filtered_df.nlargest(10, 'heat_score').copy()
        
        # 标准化处理（让各维度在同一尺度）
        dims = ['heat_score', 'uv', 'clicks', 'favorites', 'carts', 'overall_conversion']
        for dim in dims:
            if dim in top_items.columns and top_items[dim].std() > 0:
                top_items[f'{dim}_norm'] = (top_items[dim] - top_items[dim].min()) / (top_items[dim].max() - top_items[dim].min())
            else:
                top_items[f'{dim}_norm'] = 0
        
        # 创建平行坐标图
        fig_parallel = go.Figure(data=go.Parcoords(
            line=dict(color=top_items['heat_score'],
                     colorscale='RdYlBu_r',
                     showscale=True,
                     cmin=top_items['heat_score'].min(),
                     cmax=top_items['heat_score'].max()),
            dimensions=[
                dict(range=[0, 1], label='热度得分', values=top_items['heat_score_norm']),
                dict(range=[0, 1], label='UV', values=top_items['uv_norm']),
                dict(range=[0, 1], label='点击数', values=top_items['clicks_norm']),
                dict(range=[0, 1], label='收藏数', values=top_items['favorites_norm']),
                dict(range=[0, 1], label='加购数', values=top_items['carts_norm']),
                dict(range=[0, 1], label='转化率', values=top_items['overall_conversion_norm'])
            ],
            unselected=dict(line=dict(color='lightgray', opacity=0.3))
        ))
        
        fig_parallel.update_layout(
            height=450,
            margin=dict(l=80, r=80, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=11)
        )
        st.plotly_chart(fig_parallel, use_container_width=True, config={'displayModeBar': False})
        
        # 添加说明
        st.info("💡 **使用提示**：拖动坐标轴上的筛选框可以高亮特定范围的商品，点击图例可查看具体商品在各维度的表现。")
    
    # Tab2: 子弹图（替代雷达图做对比）
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
                # 创建子弹图（Bullet Chart）
                fig_bullet = go.Figure()
                
                colors = ['#2563eb', '#dc2626']
                cat_means = filtered_df[metrics_compare].mean()
                
                for idx, item_id in enumerate(selected_items[:2]):
                    item = filtered_df[filtered_df['item_id'] == item_id].iloc[0]
                    
                    for metric_idx, metric in enumerate(metrics_compare):
                        actual = item[metric]
                        target = cat_means[metric]
                        
                        # 归一化到0-100显示
                        max_val = filtered_df[metric].max()
                        normalized_actual = (actual / max_val) * 100 if max_val > 0 else 0
                        normalized_target = (target / max_val) * 100 if max_val > 0 else 0
                        
                        fig_bullet.add_trace(go.Bar(
                            x=[normalized_actual],
                            y=[f"{metric}_{idx}"],
                            orientation='h',
                            name=f'商品{item_id}',
                            marker_color=colors[idx],
                            text=f'{actual:.1f}',
                            textposition='outside',
                            showlegend=(metric_idx == 0)
                        ))
                        
                        # 添加目标线（类目均值）
                        fig_bullet.add_vline(
                            x=normalized_target,
                            line_dash="dash",
                            line_color="#64748b",
                            annotation_text=f"均值: {target:.1f}",
                            annotation_position="top"
                        )
                
                fig_bullet.update_layout(
                    barmode='group',
                    height=300 + len(metrics_compare) * 50,
                    margin=dict(l=150, r=50, t=30, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                    xaxis=dict(title="相对表现(%)", range=[0, 110])
                )
                st.plotly_chart(fig_bullet, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("请选择至少一个商品和指标进行对比")
    
    # Tab3: 树状图（替代热力图）
    with tab3:
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b; font-size: 1.1rem;">🗂️ 类目×热度层级树状图</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.85rem; margin-bottom: 15px;">矩形大小表示商品数量，颜色深浅表示平均热度</p>', unsafe_allow_html=True)
        
        # 准备树状图数据
        df_temp = filtered_df.copy()
        df_temp['heat_level'] = pd.cut(df_temp['heat_score'], 
                                      bins=[0, 2, 5, 10, 20, float('inf')],
                                      labels=['冷门(0-2)', '一般(2-5)', '热门(5-10)', '爆款(10-20)', '超级爆款(20+)'])
        
        # 按类目和热度等级聚合
        treemap_data = df_temp.groupby(['cat_id', 'heat_level']).agg({
            'item_id': 'count',
            'heat_score': 'mean'
        }).reset_index()
        treemap_data.columns = ['cat_id', 'heat_level', 'count', 'avg_heat']
        
        # 只保留商品数>10的类目避免过碎
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
# 页面3：转化漏斗洞察（桑基图美化）
# ==========================================
elif page == "🎯 转化漏斗洞察":
    st.markdown('<h1 class="hero-title">用户行为转化漏斗</h1>', unsafe_allow_html=True)
    
    total_clicks = filtered_df['clicks'].sum()
    total_favorites = filtered_df['favorites'].sum()
    total_carts = filtered_df['carts'].sum()
    total_purchases = filtered_df['purchases'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("👆 总点击", total_clicks, "#3b82f6"),
        ("❤️ 总收藏", total_favorites, "#ec4899"),
        ("🛒 总加购", total_carts, "#f59e0b"),
        ("💰 总购买", total_purchases, "#10b981")
    ]
    
    for col, (label, value, color) in zip([col1, col2, col3, col4], metrics):
        col.markdown(f"""
        <div class="glass-card" style="border-top: 3px solid {color}; text-align: center; padding: 15px;">
            <h3 style="margin: 0; color: #64748b; font-size: 0.8rem;">{label}</h3>
            <p style="font-size: 1.6rem; font-weight: 700; color: {color}; margin: 8px 0;">{value:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 漏斗图
    with st.container():
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b;">📉 行为转化漏斗</div>', unsafe_allow_html=True)
        
        funnel_values = [total_clicks, total_favorites, total_carts, total_purchases]
        funnel_labels = ["点击", "收藏", "加购", "购买"]
        funnel_colors = ["#3b82f6", "#ec4899", "#f59e0b", "#10b981"]
        
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_labels,
            x=funnel_values,
            textposition="inside",
            textinfo="value+percent initial",
            texttemplate="%{value:,.0f}<br>(%{percentInitial:.1%})",
            opacity=0.9,
            marker=dict(color=funnel_colors, line=dict(width=2, color='white')),
            connector=dict(line=dict(color="#e5e7eb", width=2))
        ))
        fig_funnel.update_layout(
            template='plotly_white',
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': False})
    
    # 美化版桑基图
    with st.container():
        st.markdown('<div style="padding: 10px 0; font-weight: 600; color: #1e293b;">🌊 用户行为流量桑基图（美化版）</div>', unsafe_allow_html=True)
        
        # 抽样计算各阶段人数
        sample_size = min(5000, len(filtered_df))
        sample_df = filtered_df.sample(sample_size, random_state=42)
        
        # 计算各阶段留存（基于行为>0）
        exposure = sample_size  # 曝光 = 样本量
        click_n = (sample_df['clicks'] > 0).sum()
        fav_n = (sample_df['favorites'] > 0).sum()
        cart_n = (sample_df['carts'] > 0).sum()
        buy_n = (sample_df['purchases'] > 0).sum()
        
        # 流失人数
        loss_click = exposure - click_n
        loss_fav = click_n - fav_n
        loss_cart = fav_n - cart_n
        loss_buy = cart_n - buy_n
        
        # 创建节点和连接（优化布局）
        fig_sankey = go.Figure(data=[go.Sankey(
            arrangement="snap",  # 优化节点对齐
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color="white", width=1),
                label=["📢 曝光", "👆 点击", "❤️ 收藏", "🛒 加购", "💰 购买", "💨 流失"],
                color=["#94a3b8", "#3b82f6", "#ec4899", "#f59e0b", "#10b981", "#cbd5e1"],
                x=[0.05, 0.25, 0.45, 0.65, 0.85, 0.65],  # 流失节点放在右侧
                y=[0.5, 0.5, 0.3, 0.5, 0.5, 0.2]
            ),
            link=dict(
                source=[0, 1, 1, 2, 2, 3, 3],
                target=[1, 2, 5, 3, 5, 4, 5],
                value=[click_n, fav_n, loss_click, cart_n, loss_fav, buy_n, loss_cart],
                color=[
                    "rgba(59, 130, 246, 0.5)",   # 曝光->点击（蓝）
                    "rgba(236, 72, 153, 0.5)",   # 点击->收藏（粉）
                    "rgba(203, 213, 225, 0.3)",  # 点击->流失（灰）
                    "rgba(245, 158, 11, 0.5)",   # 收藏->加购（橙）
                    "rgba(203, 213, 225, 0.3)",  # 收藏->流失（灰）
                    "rgba(16, 185, 129, 0.6)",   # 加购->购买（绿，粗）
                    "rgba(203, 213, 225, 0.3)"   # 加购->流失（灰）
                ],
                hovertemplate='从 %{source.label} 到 %{target.label}<br>人数: %{value}<br>占比: %{percent:.1%}<extra></extra>'
            )
        )])
        
        fig_sankey.update_layout(
            template='plotly_white',
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, family="Arial"),
            title=dict(
                text="用户流量流向图（基于抽样数据）",
                font=dict(size=14, color="#374151"),
                x=0.5
            )
        )
        st.plotly_chart(fig_sankey, use_container_width=True, config={'displayModeBar': False})
        
        # 添加转化率说明
        col_conv1, col_conv2, col_conv3 = st.columns(3)
        with col_conv1:
            st.metric("点击转化率", f"{click_n/exposure*100:.1f}%", f"{click_n}人")
        with col_conv2:
            st.metric("收藏→加购率", f"{cart_n/fav_n*100:.1f}%" if fav_n > 0 else "0%", f"{cart_n}人")
        with col_conv3:
            st.metric("加购→购买率", f"{buy_n/cart_n*100:.1f}%" if cart_n > 0 else "0%", f"{buy_n}人")

# 其他页面保持类似风格...

# ==========================================
# 页脚
# ==========================================
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 20px;">
    © 2026 电商商品热度分析系统 · 基于统计学方法构建 · 信息可视化设计类参赛作品
</p>
""", unsafe_allow_html=True)
