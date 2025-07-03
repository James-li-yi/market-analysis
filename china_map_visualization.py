import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 页面配置
st.set_page_config(page_title="保利物业市场拓展分析", layout="wide")

# 标题
st.title(" 保利物业2024-2025年市场拓展对比分析")

# 侧边栏 - 文件上传
st.sidebar.header("📁 数据文件上传")
file_2024 = st.sidebar.file_uploader("上传2024年数据", type=['csv'])
file_2025 = st.sidebar.file_uploader("上传2025年数据", type=['csv'])

def load_data(file, year):
    """加载并处理数据"""
    if file is not None:
        try:
            # 首先尝试UTF-8编码
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # 如果UTF-8失败，尝试GBK编码
                file.seek(0)  # 重置文件指针
                df = pd.read_csv(file, encoding='gbk')
            except UnicodeDecodeError:
                try:
                    # 如果GBK也失败，尝试GB2312编码
                    file.seek(0)  # 重置文件指针
                    df = pd.read_csv(file, encoding='gb2312')
                except UnicodeDecodeError:
                    # 最后尝试ISO-8859-1编码
                    file.seek(0)  # 重置文件指针
                    df = pd.read_csv(file, encoding='iso-8859-1')
        
        # 数据清洗：移除空行和无效行
        df = df.dropna(how='all')  # 删除完全空白的行
        df = df.dropna(subset=['业绩金额'])  # 删除业绩金额为空的行
        
        # 确保业绩金额为数值型
        df['业绩金额'] = pd.to_numeric(df['业绩金额'], errors='coerce')
        
        # 移除业绩金额转换失败的行
        df = df.dropna(subset=['业绩金额'])
        
        # 移除重复行（如果存在）
        df = df.drop_duplicates()
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 添加年份列
        df['年份'] = year
        
        return df
    return None

# 加载数据
df_2024 = load_data(file_2024, 2024)
df_2025 = load_data(file_2025, 2025)

if df_2024 is not None and df_2025 is not None:
    # 合并数据
    df_all = pd.concat([df_2024, df_2025], ignore_index=True)
    
    # 数据概览
    st.header("数据概览")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_2024 = df_2024['业绩金额'].sum()
        st.metric("2024年总业绩", f"{total_2024:.0f}万元")
    
    with col2:
        total_2025 = df_2025['业绩金额'].sum()
        st.metric("2025年总业绩", f"{total_2025:.0f}万元")
    
    with col3:
        growth_rate = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else 0
        st.metric("增长率", f"{growth_rate:.1f}%")
    
    with col4:
        project_count = len(df_2024) + len(df_2025)
        st.metric("总项目数", f"{project_count}")
    
    # 主要分析
    st.header("核心分析")
    
    # 1. 年度业绩对比
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("年度业绩对比")
        # 重新计算年度数据，确保准确性
        yearly_performance = []
        yearly_performance.append({'年份': 2024, '总业绩': df_2024['业绩金额'].sum(), '项目数量': len(df_2024)})
        yearly_performance.append({'年份': 2025, '总业绩': df_2025['业绩金额'].sum(), '项目数量': len(df_2025)})
        yearly_data = pd.DataFrame(yearly_performance)
        yearly_data['年份'] = yearly_data['年份'].astype(str)
        fig1 = px.bar(yearly_data, x='年份', y='总业绩', 
                      title="年度总业绩对比",
                      text='总业绩',width=800,  # 设置图片宽度
              height=500,  # 设置图片高度
              # 设置柱子颜色
              color='年份',  # 按年份分组颜色
              color_discrete_sequence=px.colors.qualitative.Plotly 
              )
              
        fig1.update_traces(texttemplate='%{text:.1f}万', textposition='outside')
        fig1.update_layout(xaxis=dict(tickmode='array', tickvals=[2024, 2025]))
        st.plotly_chart(fig1, use_container_width=True)
        
        # 分析结果
        st.info(f"**业绩分析**：{'增长' if growth_rate > 0 else '下降'}{abs(growth_rate):.1f}%，总业绩差额{abs(total_2025-total_2024):.0f}万元")
    
    with col2:
        st.subheader("项目数量对比")
        yearly_data['年份'] = yearly_data['年份'].astype(str)
        fig2 = px.bar(yearly_data, x='年份', y='项目数量',
                      title="年度项目数量对比",
                      text='项目数量',width=800,  # 设置图片宽度
              height=500,  # 设置图片高度
              # 设置柱子颜色
              color='年份',  # 按年份分组颜色
              color_discrete_sequence=px.colors.qualitative.Plotly )
        fig2.update_traces(texttemplate='%{text}个', textposition='outside')
        fig2.update_layout(xaxis=dict(tickmode='array', tickvals=[2024, 2025]))
        st.plotly_chart(fig2, use_container_width=True)
        
        # 分析结果
        project_change = len(df_2025) - len(df_2024)
        st.info(f"**项目分析**：项目数量{'增加' if project_change > 0 else '减少'}{abs(project_change)}个，平均项目业绩2024年{total_2024/len(df_2024):.1f}万元，2025年{total_2025/len(df_2025):.1f}万元")
    
    # 2. 城市分析
    st.subheader("城市市场分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 按业绩平台分析
        platform_analysis = df_all.groupby(['业绩平台', '年份'])['业绩金额'].sum().reset_index()
        # 确保年份为字符串，避免小数点显示
        platform_analysis['年份'] = platform_analysis['年份'].astype(str)
        
        fig3 = px.bar(platform_analysis, x='业绩平台', y='业绩金额', color='年份',
                      title="各业绩平台年度业绩对比", barmode='group')
        fig3.update_layout(
            legend=dict(title="年份"),
            xaxis_tickangle=45
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # 分析结果
        top_platform_2024 = df_2024.groupby('业绩平台')['业绩金额'].sum().idxmax()
        top_platform_2025 = df_2025.groupby('业绩平台')['业绩金额'].sum().idxmax()
        st.info(f"**平台分析**：2024年最佳平台为{top_platform_2024}，2025年为{top_platform_2025}")
    
    with col2:
        # 按城市分析 - 优化显示效果
        st.write("**城市业绩分析**")
        
        # 交互式筛选器
        col2_1, col2_2 = st.columns([1, 1])
        with col2_1:
            city_count = st.selectbox("选择显示城市数量", [5, 8, 10, 15, 20], index=2)
        with col2_2:
            chart_type = st.radio("图表类型", ["柱状图", "饼图"], horizontal=True)
        
        city_analysis = df_all.groupby(['城市', '年份'])['业绩金额'].sum().reset_index()
        
        # 计算各城市总业绩，筛选出前N名城市
        city_total = df_all.groupby('城市')['业绩金额'].sum().sort_values(ascending=False).head(city_count)
        top_cities = city_total.index.tolist()
        
        if chart_type == "柱状图":
            # 筛选前N城市的数据
            city_analysis_filtered = city_analysis[city_analysis['城市'].isin(top_cities)].copy()
            city_analysis_filtered['年份'] = city_analysis_filtered['年份'].astype(str)
            
            # 按总业绩排序城市显示顺序
            city_order = city_total.index.tolist()
            city_analysis_filtered['城市'] = pd.Categorical(city_analysis_filtered['城市'], 
                                                            categories=city_order, ordered=True)
            city_analysis_filtered = city_analysis_filtered.sort_values('城市')
            
            fig4 = px.bar(city_analysis_filtered, x='城市', y='业绩金额', color='年份',
                          title=f"前{city_count}大城市年度业绩对比", barmode='group')
            fig4.update_layout(
                legend=dict(title="年份"),
                xaxis_tickangle=45,
                height=400
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        else:
            # 饼图显示城市业绩占比
            col2_pie1, col2_pie2 = st.columns(2)
            
            with col2_pie1:
                # 2024年城市业绩占比
                city_2024 = df_2024.groupby('城市')['业绩金额'].sum().sort_values(ascending=False).head(city_count)
                fig4_1 = px.pie(values=city_2024.values, names=city_2024.index,
                                title=f"2024年前{city_count}大城市业绩占比")
                st.plotly_chart(fig4_1, use_container_width=True)
            
            with col2_pie2:
                # 2025年城市业绩占比
                city_2025 = df_2025.groupby('城市')['业绩金额'].sum().sort_values(ascending=False).head(city_count)
                fig4_2 = px.pie(values=city_2025.values, names=city_2025.index,
                                title=f"2025年前{city_count}大城市业绩占比")
                st.plotly_chart(fig4_2, use_container_width=True)
        
        # 添加其他城市汇总信息
        total_cities = len(df_all['城市'].unique())
        other_cities_count = total_cities - city_count
        if other_cities_count > 0:
            other_cities_performance = df_all[~df_all['城市'].isin(top_cities)]['业绩金额'].sum()
            st.info(f"其他{other_cities_count}个城市总业绩: {other_cities_performance:.0f}万元 (占比: {other_cities_performance/df_all['业绩金额'].sum()*100:.1f}%)")
    
    # 城市分析总结
    top_city_2024 = df_2024.groupby('城市')['业绩金额'].sum().idxmax()
    top_city_2025 = df_2025.groupby('城市')['业绩金额'].sum().idxmax()
    st.success(f"**城市重点**：2024年表现最佳城市为{top_city_2024}，2025年为{top_city_2025}")
    
    # 3. 业态分析
    st.subheader("业态结构分析")
    
    # 获取所有业态类型，为相同业态设置统一颜色
    all_business_types = list(set(df_2024['一级业态'].unique()) | set(df_2025['一级业态'].unique()))
    
    # 定义颜色映射
    colors = px.colors.qualitative.Set3
    if len(all_business_types) > len(colors):
        colors = colors * (len(all_business_types) // len(colors) + 1)
    
    color_map = {business: colors[i] for i, business in enumerate(all_business_types)}
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 2024年业态分布
        business_2024 = df_2024.groupby('一级业态')['业绩金额'].sum()
        fig5 = px.pie(values=business_2024.values, names=business_2024.index,
                      title="2024年业态分布",
                      color=business_2024.index,
                      color_discrete_map=color_map)
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # 2025年业态分布
        business_2025 = df_2025.groupby('一级业态')['业绩金额'].sum()
        fig6 = px.pie(values=business_2025.values, names=business_2025.index,
                      title="2025年业态分布",
                      color=business_2025.index,
                      color_discrete_map=color_map)
        st.plotly_chart(fig6, use_container_width=True)
    
    # 业态分析结果
    top_business_2024 = df_2024.groupby('一级业态')['业绩金额'].sum().idxmax()
    top_business_2025 = df_2025.groupby('一级业态')['业绩金额'].sum().idxmax()
    st.info(f" **业态重点**：2024年主要业态为{top_business_2024}，2025年为{top_business_2025}")
    
    # 新增：业态下的业绩平台结构图
    st.subheader("各业绩平台一级业态结构分析")
    
    # 选择年份
    year_select = st.selectbox("选择分析年份", [2024, 2025], key="business_platform")
    
    if year_select == 2024:
        data_selected = df_2024
    else:
        data_selected = df_2025
    
    # 检查数据是否为空
    if len(data_selected) > 0:
        # 计算各业绩平台下的业态分布
        platform_business = data_selected.groupby(['业绩平台', '一级业态'])['业绩金额'].sum().unstack(fill_value=0)
        
        # 按总业绩排序业绩平台
        platform_totals = platform_business.sum(axis=1).sort_values(ascending=True)
        platform_business = platform_business.loc[platform_totals.index]
        
        # 使用plotly创建水平堆叠柱状图
        fig = go.Figure()
        
        # 为每个业态添加一个柱状图
        business_types = platform_business.columns
        platforms = platform_business.index
        
        # 创建一个颜色映射
        colors = px.colors.qualitative.Set3
        if len(business_types) > len(colors):
            colors = colors * (len(business_types) // len(colors) + 1)
        
        for i, business in enumerate(business_types):
            values = platform_business[business].values
            fig.add_trace(go.Bar(
                name=business,
                y=platforms,
                x=values,
                orientation='h',
                marker_color=colors[i % len(colors)],
                text=[f'{v:.0f}万' if v > 0 else '' for v in values],
                textposition='inside',
                textfont=dict(size=10, color='white')
            ))
        
        fig.update_layout(
            title=f'{year_select}年各业绩平台一级业态结构分布',
            xaxis_title='业绩金额 (万元)',
            yaxis_title='业绩平台',
            barmode='stack',
            height=max(400, len(platforms) * 50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(0,0,0,0.8)'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # 设置网格线样式
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 业态平台分析结果 - 按图表中从上到下的顺序显示
        st.markdown("**📊 平台业态分析：**")
        
        # 按照图表中的顺序（从上到下）来显示分析结果
        for platform in reversed(platform_totals.index):
            platform_data = data_selected[data_selected['业绩平台'] == platform]
            business_summary = platform_data.groupby('一级业态')['业绩金额'].sum().sort_values(ascending=False)
            
            if len(business_summary) > 0:
                total_amount = business_summary.sum()
                main_business = business_summary.index[0]
                main_percentage = (business_summary.iloc[0] / total_amount * 100)
                business_count = len(business_summary)
                
                # 构建业态分布描述
                if business_count == 1:
                    business_desc = f"专注于{main_business}"
                elif business_count == 2:
                    business_desc = f"以{main_business}为主({main_percentage:.1f}%)，同时涉及{business_summary.index[1]}"
                else:
                    business_desc = f"以{main_business}为主({main_percentage:.1f}%)，涉及{business_count}个业态"
                
                st.write(f"- **{platform}**：{business_desc}，总业绩{total_amount:.0f}万元")
    else:
        st.warning(f"{year_select}年暂无数据")
    
    # 4. 行业分析
    st.subheader("行业布局分析")
    industry_analysis = df_all.groupby(['行业', '年份'])['业绩金额'].sum().reset_index()
    # 确保年份为字符串，避免小数点显示
    industry_analysis['年份'] = industry_analysis['年份'].astype(str)
    
    fig7 = px.bar(industry_analysis, x='行业', y='业绩金额', color='年份',
                  title="各行业年度业绩对比", barmode='group')
    fig7.update_layout(xaxis_tickangle=45, legend=dict(title="年份"))
    st.plotly_chart(fig7, use_container_width=True)
    
    # 行业分析结果
    top_industry_2024 = df_2024.groupby('行业')['业绩金额'].sum().idxmax()
    top_industry_2025 = df_2025.groupby('行业')['业绩金额'].sum().idxmax()
    industry_count = len(df_all['行业'].unique())
    st.info(f"**行业布局**：共涉及{industry_count}个行业，2024年重点行业为{top_industry_2024}，2025年为{top_industry_2025}")
    
    # 5. 重点客户分析
    st.subheader("重点客户分析")
    
    # 筛选选项
    year_filter = st.selectbox("选择年份", [2024, 2025, "全部"])
    
    if year_filter == "全部":
        client_data = df_all.groupby('客户')['业绩金额'].sum().sort_values(ascending=False).head(10)
    else:
        if year_filter == 2024:
            client_data = df_2024.groupby('客户')['业绩金额'].sum().sort_values(ascending=False).head(10)
        else:
            client_data = df_2025.groupby('客户')['业绩金额'].sum().sort_values(ascending=False).head(10)
    
    fig8 = px.bar(x=client_data.values, y=client_data.index, orientation='h',
                  title=f"前10大客户业绩排名 ({year_filter}年)")
    fig8.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig8, use_container_width=True)
    
    # 客户分析结果
    if year_filter == "全部":
        top_client = df_all.groupby('客户')['业绩金额'].sum().idxmax()
        client_count = len(df_all['客户'].unique())
    elif year_filter == 2024:
        top_client = df_2024.groupby('客户')['业绩金额'].sum().idxmax()
        client_count = len(df_2024['客户'].unique())
    else:
        top_client = df_2025.groupby('客户')['业绩金额'].sum().idxmax()
        client_count = len(df_2025['客户'].unique())
    
    st.info(f"**客户分析**：{year_filter}年最重要客户为{top_client}，共服务{client_count}个客户")
    
    # 6. 数据表格
    st.header("详细数据")
    
    # 显示选项
    show_year = st.radio("选择显示数据", ["2024年", "2025年", "全部"])
    
    if show_year == "2024年":
        st.dataframe(df_2024, use_container_width=True)
    elif show_year == "2025年":
        st.dataframe(df_2025, use_container_width=True)
    else:
        st.dataframe(df_all, use_container_width=True)
    
    # 总结报告
    st.header("分析总结")
    
    # 计算关键指标
    top_city_2024 = df_2024.groupby('城市')['业绩金额'].sum().idxmax()
    top_city_2025 = df_2025.groupby('城市')['业绩金额'].sum().idxmax()
    top_business_2024 = df_2024.groupby('一级业态')['业绩金额'].sum().idxmax()
    top_business_2025 = df_2025.groupby('一级业态')['业绩金额'].sum().idxmax()
    
    st.write(f"""
    **关键发现：**
    
    - **业绩增长：** 2025年相比2024年增长 {growth_rate:.1f}%
    - **重点城市：** 2024年表现最佳城市为{top_city_2024}，2025年为{top_city_2025}
    - **核心业态：** 2024年主要业态为{top_business_2024}，2025年为{top_business_2025}
    - **项目规模：** 2024年{len(df_2024)}个项目，2025年{len(df_2025)}个项目
    - **平台布局：** 各业态在不同业绩平台上呈现差异化分布特征
    """)

else:
    st.info("请在左侧上传2024年和2025年的CSV数据文件开始分析")
    
    st.markdown("""
    ### 📋 使用说明
    
    1. **上传数据文件**：在左侧上传2024.csv和2025.csv文件
    2. **数据格式要求**：确保CSV文件包含以下列：
        - 城市
        - 一级业态  
        - 客户
        - 行业
        - 业绩金额
        - 业绩平台
    3. **开始分析**：上传完成后自动生成分析报告
    
    ### 🎯 分析内容
    - 年度业绩对比
    - 城市市场分析
    - 业态结构变化
    - 业态业绩平台结构分析（新增）
    - 行业布局分析
    - 重点客户排名
    - 详细数据查看
    """)
