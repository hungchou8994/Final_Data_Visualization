from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm

# Tên file PDF
file_name = 'traffic_accident_report.pdf'

def create_pdf(file_name, text):
    # Tạo file PDF
    pdf = SimpleDocTemplate(file_name, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Tùy chỉnh các style
    title_style = styles['Title']
    body_style = styles['BodyText']
    body_style.leading = 14  # Khoảng cách giữa các dòng
    custom_style = ParagraphStyle(
        'CustomStyle', parent=body_style, alignment=0, spaceAfter=10
    )
    
    # Nội dung PDF
    content = []
    content.append(Paragraph('Báo Cáo Tai Nạn Giao Thông', title_style))
    content.append(Spacer(1, 0.5 * cm))
    
    # Tự động chia đoạn văn theo dấu ngắt dòng
    paragraphs = text.split('\n')
    for para in paragraphs:
        if para.strip():
            content.append(Paragraph(para.strip(), custom_style))
            content.append(Spacer(1, 0.2 * cm))
    
    # Xuất PDF
    pdf.build(content)

# Văn bản đầy đủ
full_text = '''Bản báo cáo sau giới thiệu sơ lược về tập dữ liệu của các vụ tai nạn giao thông đã xảy ra ở Việt Nam. Tập dữ liệu này chứa thông tin chi tiết về thời gian, địa điểm, nguyên nhân và lỗi vi phạm liên quan đến từng vụ tai nạn.

Tập dữ liệu gồm 4069 mục, ngụ ý rằng đã có ít nhất 4069 vụ tai nạn giao thông được ghi chép.

"Thời gian xảy ra tai nạn": Đây là thuộc tính dạng thời gian, cho biết thời điểm mà tai nạn đã xảy ra trong ngày. Có thể sử dụng phép toán thống kê như mode (giá trị xuất hiện nhiều nhất) để xác định khoảng thời gian mà nhiều tai nạn nhất xảy ra.

"Nguyên nhân và Lỗi vi phạm": Đây là một thuộc tính danh mục, mô tả nguyên nhân gây ra tai nạn và hành vi vi phạm của tài xế (nếu có). Đây có thể là một thuộc tính rất hữu ích trong việc xác định các nguyên nhân chính của tai nạn giao thông. Phép toán thống kê có thể được áp dụng như tính frequency để xác định những lỗi vi phạm thường gặp.

Giữa các cột dữ liệu còn có 22 cột khác không được đề cập trong đoạn trích. Tuy nhiên, chúng có thể chứa các thông tin quan trọng khác như địa điểm tai nạn, loại phương tiện liên quan.'''

# Gọi hàm tạo PDF
create_pdf(file_name, full_text)
print(f"File PDF đã được tạo: {file_name}")
