import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Thiết lập trang
st.set_page_config(page_title="Công Cụ Mô Phỏng Đầu Tư Tích Sản", layout="wide")
st.title("Công Cụ Mô Phỏng Hành Trình Đầu Tư Tích Sản")

# Sidebar cho các tham số đầu vào
st.sidebar.header("Thông Số Đầu Tư")

# Thông số đầu tư
initial_investment = st.sidebar.number_input("Số tiền đầu tư ban đầu (VND)", min_value=0, value=10000000, step=1000000)
monthly_contribution = st.sidebar.number_input("Số tiền đầu tư hàng tháng (VND)", min_value=0, value=1000000, step=500000)
years = st.sidebar.slider("Thời gian đầu tư (năm)", min_value=1, max_value=40, value=10)
expected_return = st.sidebar.slider("Lợi nhuận kỳ vọng hàng năm (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.5)
risk_level = st.sidebar.selectbox("Mức độ rủi ro", ["Thấp", "Trung bình", "Cao"])

# Thêm tùy chọn cho biến động thị trường
market_volatility = st.sidebar.checkbox("Mô phỏng biến động thị trường")
if market_volatility:
    volatility = st.sidebar.slider("Độ biến động (%)", min_value=1.0, max_value=30.0, value=15.0, step=0.5)
else:
    volatility = 0.0

# Tính toán kết quả đầu tư
def calculate_investment(initial, monthly, years, annual_return, volatility=0):
    months = years * 12
    monthly_return = (1 + annual_return/100) ** (1/12) - 1
    
    # Khởi tạo mảng kết quả
    balance = np.zeros(months + 1)
    investment = np.zeros(months + 1)
    dates = [datetime.now() + timedelta(days=30*i) for i in range(months + 1)]
    
    # Giá trị ban đầu
    balance[0] = initial
    investment[0] = initial
    
    # Mô phỏng theo từng tháng
    for i in range(1, months + 1):
        # Thêm khoản đóng góp hàng tháng
        investment[i] = investment[i-1] + monthly
        
        # Tính lợi nhuận với biến động (nếu có)
        if volatility > 0:
            # Tạo biến động ngẫu nhiên theo phân phối chuẩn
            random_return = np.random.normal(monthly_return, volatility/100/np.sqrt(12))
            balance[i] = balance[i-1] * (1 + random_return) + monthly
        else:
            balance[i] = balance[i-1] * (1 + monthly_return) + monthly
    
    return pd.DataFrame({
        'Thời gian': dates,
        'Số tiền đầu tư': investment,
        'Giá trị tài sản': balance
    })

# Tính toán kết quả
results = calculate_investment(initial_investment, monthly_contribution, years, expected_return, volatility)

# Hiển thị kết quả
st.header("Kết Quả Mô Phỏng")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Thông tin tổng quan")
    final_balance = results['Giá trị tài sản'].iloc[-1]
    total_invested = results['Số tiền đầu tư'].iloc[-1]
    profit = final_balance - total_invested
    roi = (profit / total_invested) * 100
    
    st.metric("Tổng số tiền đầu tư", f"{total_invested:,.0f} VND")
    st.metric("Giá trị tài sản cuối kỳ", f"{final_balance:,.0f} VND")
    st.metric("Lợi nhuận", f"{profit:,.0f} VND", f"{roi:.2f}%")

with col2:
    st.subheader("Phân bổ tài sản")
    labels = ['Số tiền gốc đầu tư', 'Lợi nhuận']
    values = [total_invested, profit]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
    st.plotly_chart(fig)

# Biểu đồ hành trình đầu tư
st.subheader("Biểu đồ hành trình đầu tư")
fig = go.Figure()
fig.add_trace(go.Scatter(x=results['Thời gian'], y=results['Giá trị tài sản'], 
                         mode='lines', name='Giá trị tài sản'))
fig.add_trace(go.Scatter(x=results['Thời gian'], y=results['Số tiền đầu tư'], 
                         mode='lines', name='Số tiền đầu tư'))
fig.update_layout(title='Hành trình đầu tư tích sản theo thời gian',
                  xaxis_title='Thời gian',
                  yaxis_title='Giá trị (VND)')
st.plotly_chart(fig, use_container_width=True)

# Hiển thị bảng dữ liệu theo từng năm
st.subheader("Bảng dữ liệu theo từng năm")
yearly_data = results.iloc[::12].copy()  # Lấy dữ liệu theo năm
yearly_data['Năm'] = range(years + 1)
yearly_data['Lợi nhuận'] = yearly_data['Giá trị tài sản'] - yearly_data['Số tiền đầu tư']
yearly_data['Tỷ suất sinh lời'] = (yearly_data['Lợi nhuận'] / yearly_data['Số tiền đầu tư']) * 100

st.dataframe(yearly_data[['Năm', 'Số tiền đầu tư', 'Giá trị tài sản', 'Lợi nhuận', 'Tỷ suất sinh lời']].round(2))

# Thêm phần phân tích rủi ro dựa trên mức độ rủi ro đã chọn
st.header("Phân Tích Rủi Ro")

risk_descriptions = {
    "Thấp": "Danh mục đầu tư có rủi ro thấp thường bao gồm trái phiếu chính phủ, tiền gửi có kỳ hạn và các quỹ đầu tư cố định. Lợi nhuận kỳ vọng thường thấp hơn nhưng ổn định hơn.",
    "Trung bình": "Danh mục đầu tư có rủi ro trung bình thường là sự kết hợp giữa cổ phiếu, trái phiếu và tiền mặt với tỷ lệ phân bổ cân đối. Lợi nhuận kỳ vọng và rủi ro ở mức vừa phải.",
    "Cao": "Danh mục đầu tư có rủi ro cao thường tập trung vào cổ phiếu, đặc biệt là cổ phiếu tăng trưởng, các quỹ ETF ngành, hoặc các tài sản thay thế. Lợi nhuận kỳ vọng cao nhưng đi kèm với biến động lớn."
}

st.write(f"**Mức độ rủi ro đã chọn: {risk_level}**")
st.write(risk_descriptions[risk_level])

# Mô phỏng các kịch bản khác nhau
if market_volatility:
    st.header("Mô Phỏng Các Kịch Bản")
    
    # Tạo 10 kịch bản khác nhau
    num_scenarios = 10
    scenario_results = []
    
    for i in range(num_scenarios):
        scenario = calculate_investment(initial_investment, monthly_contribution, years, expected_return, volatility)
        scenario_results.append(scenario['Giá trị tài sản'])
    
    # Vẽ biểu đồ các kịch bản
    fig = go.Figure()
    
    for i, scenario in enumerate(scenario_results):
        fig.add_trace(go.Scatter(x=results['Thời gian'], y=scenario, 
                                mode='lines', name=f'Kịch bản {i+1}',
                                opacity=0.5))
    
    # Thêm đường trung bình
    avg_scenario = pd.DataFrame(scenario_results).mean()
    fig.add_trace(go.Scatter(x=results['Thời gian'], y=avg_scenario, 
                            mode='lines', name='Trung bình',
                            line=dict(color='red', width=3)))
    
    fig.update_layout(title='Mô phỏng các kịch bản đầu tư khác nhau',
                    xaxis_title='Thời gian',
                    yaxis_title='Giá trị (VND)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Thống kê từ các kịch bản
    final_values = [scenario.iloc[-1] for scenario in scenario_results]
    min_value = min(final_values)
    max_value = max(final_values)
    avg_value = sum(final_values) / len(final_values)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Giá trị tối thiểu", f"{min_value:,.0f} VND")
    col2.metric("Giá trị trung bình", f"{avg_value:,.0f} VND")
    col3.metric("Giá trị tối đa", f"{max_value:,.0f} VND")

# Thêm phần so sánh với các chiến lược đầu tư khác
st.header("So Sánh Các Chiến Lược Đầu Tư")

# Tính toán cho các chiến lược khác
conservative_return = expected_return * 0.5  # Chiến lược bảo thủ
aggressive_return = expected_return * 1.5  # Chiến lược tích cực

conservative_results = calculate_investment(initial_investment, monthly_contribution, years, conservative_return)
base_results = calculate_investment(initial_investment, monthly_contribution, years, expected_return)
aggressive_results = calculate_investment(initial_investment, monthly_contribution, years, aggressive_return)

# Vẽ biểu đồ so sánh
fig = go.Figure()
fig.add_trace(go.Scatter(x=conservative_results['Thời gian'], y=conservative_results['Giá trị tài sản'], 
                        mode='lines', name=f'Bảo thủ ({conservative_return:.1f}%)'))
fig.add_trace(go.Scatter(x=base_results['Thời gian'], y=base_results['Giá trị tài sản'], 
                        mode='lines', name=f'Cân bằng ({expected_return:.1f}%)'))
fig.add_trace(go.Scatter(x=aggressive_results['Thời gian'], y=aggressive_results['Giá trị tài sản'], 
                        mode='lines', name=f'Tích cực ({aggressive_return:.1f}%)'))

fig.update_layout(title='So sánh các chiến lược đầu tư',
                xaxis_title='Thời gian',
                yaxis_title='Giá trị (VND)')
st.plotly_chart(fig, use_container_width=True)

# Bảng so sánh kết quả cuối cùng
comparison_data = {
    'Chiến lược': ['Bảo thủ', 'Cân bằng', 'Tích cực'],
    'Lợi nhuận kỳ vọng (%)': [conservative_return, expected_return, aggressive_return],
    'Giá trị cuối kỳ (VND)': [
        conservative_results['Giá trị tài sản'].iloc[-1],
        base_results['Giá trị tài sản'].iloc[-1],
        aggressive_results['Giá trị tài sản'].iloc[-1]
    ],
    'Tổng đầu tư (VND)': [
        conservative_results['Số tiền đầu tư'].iloc[-1],
        base_results['Số tiền đầu tư'].iloc[-1],
        aggressive_results['Số tiền đầu tư'].iloc[-1]
    ]
}

comparison_df = pd.DataFrame(comparison_data)
comparison_df['Lợi nhuận (VND)'] = comparison_df['Giá trị cuối kỳ (VND)'] - comparison_df['Tổng đầu tư (VND)']
comparison_df['ROI (%)'] = (comparison_df['Lợi nhuận (VND)'] / comparison_df['Tổng đầu tư (VND)']) * 100

st.table(comparison_df.round(2))

# Lời khuyên đầu tư
st.header("Lời Khuyên Đầu Tư")
st.write("""
1. **Đầu tư đều đặn**: Đầu tư tích sản hiệu quả nhất khi bạn đóng góp đều đặn theo kỳ, bất kể thị trường đang lên hay xuống. [[4]](#__4)
2. **Đa dạng hóa danh mục**: Phân bổ tài sản vào nhiều loại khác nhau để giảm thiểu rủi ro.
3. **Đầu tư dài hạn**: Thời gian là yếu tố quan trọng trong đầu tư tích sản, càng đầu tư lâu dài, lợi nhuận kép càng phát huy tác dụng.
4. **Tái cân bằng định kỳ**: Điều chỉnh danh mục đầu tư định kỳ để đảm bảo phân bổ tài sản phù hợp với mục tiêu và khả năng chịu rủi ro.
5. **Tận dụng công nghệ**: Các công cụ AI và phần mềm mô phỏng có thể giúp bạn phân tích và đưa ra quyết định đầu tư tốt hơn. [[5]](#__5)
""")

st.markdown("---")
st.caption("Công cụ mô phỏng này chỉ mang tính chất tham khảo và không đảm bảo kết quả đầu tư trong tương lai.")
