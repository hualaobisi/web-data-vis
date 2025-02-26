import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False

# 设置网页标题
st.title('数据分析网页')

# 文件上传组件，支持多文件上传
uploaded_files = st.file_uploader("上传CSV或Excel文件", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    dfs = []
    for uploaded_file in uploaded_files:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='gbk')
        else:
            df = pd.read_excel(uploaded_file)
        
        # 删除数据中空的列
        df = df.dropna(axis=1, how='all')
        
        # 将第一列的列名赋给第二列的列名，然后将第一列的列名重命名为“时间”

        df.columns =  (['时间'] + list(df.columns))[:len(df.columns)]
        # df.rename(columns={df.columns[1]: second_column_name}, inplace=True)

        # 对“时间”列进行时间化处理
        df['时间'] = pd.to_datetime(df['时间'])
        
        dfs.append(df)
    
    # 根据时间列合并所有文件
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='时间', how='inner')

    # 删除空行和空列
    merged_df = merged_df.dropna(axis=0, how='all')
    
    # 显示数据
    st.dataframe(merged_df)


    # 选择列进行可视化
    columns = [col for col in merged_df.columns.tolist() if col != '时间']  # 排除“时间”列
    selected_columns = st.multiselect("选择要对比的列（最多两列）", columns, default=columns[:2])

    if len(selected_columns) == 1:
        # 添加X轴和Y轴的可修改功能
        x_label = st.text_input("X轴标签", "时间")
        y_label = st.text_input("Y轴标签", selected_columns[0])
        line_style_options = ['-', '--', '-.', ':']
        line_color_options = ['g', 'b', 'r', 'c', 'm', 'y', 'k']
        line_style = st.selectbox(f"{selected_columns[0]} 线条样式", line_style_options, index=0)
        line_color = st.selectbox(f"{selected_columns[0]} 线条颜色", line_color_options, index=0)

        # 绘制单Y轴折线图
        st.write(f"{y_label} 的曲线图：（保存图片请使用右键“另存为”或者直接复制）")
        fig, ax = plt.subplots()
        
        ax.plot(merged_df['时间'], merged_df[selected_columns[0]], linestyle=line_style, color=line_color, label=f"{y_label}(MW)")
        
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label, color=line_color)
        ax.set_title(f"{y_label}曲线图")  # 添加图标题

        # 计算整体数据的面积，正负分开，并转换为MWh
        time_diff = merged_df['时间'].diff().dt.total_seconds() / 3600  # 计算时间差并转换为小时
        positive_area = (merged_df[merged_df[selected_columns[0]] > 0][selected_columns[0]] * time_diff[merged_df[selected_columns[0]] > 0]).sum()
        negative_area = (merged_df[merged_df[selected_columns[0]] < 0][selected_columns[0]] * time_diff[merged_df[selected_columns[0]] < 0]).sum()
        st.write(f"整体电能量：放电量 = {positive_area:.2f} MWh, 充电量 = {negative_area:.2f} MWh")

        # 旋转X轴文字以避免拥挤
        ax.tick_params(axis='x', rotation=45)

        st.pyplot(fig)

        # 绘制每天的日曲线图
        st.write("日曲线图：")
        unique_dates = merged_df['时间'].dt.date.unique()
        for date in unique_dates:
            daily_df = merged_df[merged_df['时间'].dt.date == date]
            fig, ax = plt.subplots()
            
            ax.plot(daily_df['时间'], daily_df[selected_columns[0]], linestyle=line_style, color=line_color, label=f"{y_label}(MW)")
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label, color=line_color)
            ax.set_title(f" {date} - {y_label}曲线图")  # 添加图标题

            # 计算每天的面积，正负分开，并转换为MWh
            time_diff = daily_df['时间'].diff().dt.total_seconds() / 3600  # 计算时间差并转换为小时
            daily_positive_area = (daily_df[daily_df[selected_columns[0]] > 0][selected_columns[0]] * time_diff[daily_df[selected_columns[0]] > 0]).sum()
            daily_negative_area = (daily_df[daily_df[selected_columns[0]] < 0][selected_columns[0]] * time_diff[daily_df[selected_columns[0]] < 0]).sum()
            st.write(f"日期 {date} 电能量：放电量 = {daily_positive_area:.2f} MWh, 充电量 = {daily_negative_area:.2f} MWh")

            # 旋转X轴文字以避免拥挤
            ax.tick_params(axis='x', rotation=45)

            st.pyplot(fig)

    elif len(selected_columns) == 2:
        # 添加X轴和Y轴的可修改功能
        x_label = st.text_input("X轴标签", "时间")
        # 创建双栏布局
        col1, col2 = st.columns(2)

        # 在第一栏设置 Y1 轴相关选项
        with col1:
            y1_label = st.text_input("Y1轴标签", selected_columns[0])
            line_style_options = ['-', '--', '-.', ':']
            line_color_options = ['g', 'b', 'r', 'c', 'm', 'y', 'k']
            y1_line_style = st.selectbox(f"{selected_columns[0]} 线条样式", line_style_options, index=0)
            y1_line_color = st.selectbox(f"{selected_columns[0]} 线条颜色", line_color_options, index=0)

        # 在第二栏设置 Y2 轴相关选项
        with col2:
            y2_label = st.text_input("Y2轴标签", selected_columns[1])
            y2_line_style = st.selectbox(f"{selected_columns[1]} 线条样式", line_style_options, index=0)
            y2_line_color = st.selectbox(f"{selected_columns[1]} 线条颜色", line_color_options, index=1)


        # 绘制双Y轴折线图
        st.write(f"{y1_label} 和 {y2_label} 的对比图：（保存图片请使用右键“另存为”或者直接复制）")
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        
        ax1.plot(merged_df['时间'], merged_df[selected_columns[0]], linestyle=y1_line_style, color=y1_line_color, label=f"{y1_label}(MW)")
        ax2.plot(merged_df['时间'], merged_df[selected_columns[1]], linestyle=y2_line_style, color=y2_line_color, label=f"{y2_label}(MW)")
        
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y1_label, color=y1_line_color)
        ax2.set_ylabel(y2_label, color=y2_line_color)
        ax1.set_title(f"{y1_label} VS {y2_label}")  # 添加图标题

        # 旋转X轴文字以避免拥挤
        ax1.tick_params(axis='x', rotation=45)

        st.pyplot(fig)

        # 绘制每天的日曲线图
        st.write("每天的日曲线图：")
        unique_dates = merged_df['时间'].dt.date.unique()
        for date in unique_dates:
            daily_df = merged_df[merged_df['时间'].dt.date == date]
            fig, ax1 = plt.subplots()
            ax2 = ax1.twinx()
            
            ax1.plot(daily_df['时间'], daily_df[selected_columns[0]], linestyle=y1_line_style, color=y1_line_color, label=f"{y1_label}(MW)")
            ax2.plot(daily_df['时间'], daily_df[selected_columns[1]], linestyle=y2_line_style, color=y2_line_color, label=f"{y2_label}(MW)")
            
            ax1.set_xlabel(x_label)
            ax1.set_ylabel(y1_label, color=y1_line_color)
            ax2.set_ylabel(y2_label, color=y2_line_color)
            ax1.set_title(f" {date} - {y1_label} VS {y2_label}")  # 添加图标题

            # 旋转X轴文字以避免拥挤
            ax1.tick_params(axis='x', rotation=45)

            st.pyplot(fig)

    else:
        st.write("请选择一列或两列进行对比。")
else:
    st.write("请上传CSV和Excel文件以开始分析。")
