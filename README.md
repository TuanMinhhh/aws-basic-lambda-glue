1.	Mục đích:
Trong bối cảnh thị trường việc làm ngày càng phát triển và cạnh tranh, việc có được cái nhìn tổng quan và chi tiết về các thông tin việc làm là vô cùng quan trọng. Để đáp ứng nhu cầu này, tôi cần xây dựng một hệ thống tự động để tổng hợp và phân tích thông tin việc làm trong mảng data từ các web tuyển dụng như vietnamwork, topcv… từ đó xây dựng một dashboard có thể cung cấp thông tin và trả lời các câu hỏi sau:
-	Hiện có bao nhiêu job liên quan đến lĩnh vực data trên thị trường?
-	Trên thị trường đang tuyển các dụng vị trí nào và tỉ lệ của chúng?
-	Khu vực nào có thị trường tuyển dụng sôi nổi nhất?
-	Những kỹ năng/tools nào đang được nhà tuyển dụng quan tâm?
2.	Kiến trúc:
 ![image](https://github.com/user-attachments/assets/aad343c9-52d3-4da8-94cf-f76664daf2f3)

Gồm các bước:
-	Tạo lambda và sử dụng thư viện Bs4 và Selenium để crawl dữ liệu sau đó lưu trữ tại tầng Raw Zone trên S3 bucket dưới dạng Json
-	ETL lần 1: Tạo Glue làm sạch và chuẩn hóa dữ liệu thông qua các bước loại bỏ dữ liệu thừa (Các công việc không liên quan đến mảng data) và định dạng lại các kiểu dữ liệu. Sau đó chuyển dữ liệu đã qua xử lí vào tầng Golden Zone
-	ETL lần 2: Tạo Glue để tiến hành ETL dữ liệu từ Golden Zone sang Insight Zone theo dạng OLAP gồm các bảng fact và dim. Áp dụng SCD type 2 để theo dõi lịch sử dữ liệu.
-	Sử dụng Glue catalog để lấy thông tin metadata tại tầng Insight Zone
-	Sử dụng BI tools để visualize dữ liệu

3.	Tạo step function
	![image](https://github.com/user-attachments/assets/3ccea7e5-0731-483a-a375-78425c1136fb)

4.	Visualization
![image](https://github.com/user-attachments/assets/c22c798a-332d-4e87-835e-2b53f87d8cf9)

Trả lời các câu hỏi ở mục 1:
-	Hiện tại trên thị trường chỉ có 147 job về data (tính trên TopCV và Vietnamwork)
-	Data Engineer và Data Analyst là 2 công việc có tỷ lệ tuyển dụng lớn nhất, chiếm gần 80% trên các công việc về data
-	Hiện tại Hà Nội đang là khu vực có nhu cầu về nhân lực data chiếm ~75% cả nước
-	SQL và Python là 2 công cụ được yêu cầu nhiều nhất trong thời điểm hiện tại
5.	Một số khó khăn khi thực hiện project
-	Trong quá trình crawl dữ liệu từ TopCV bị hạn chế bởi Cloudflare 
 Giải pháp dùng Selenium, khi xuất hiện cloudflare sẽ tự dộng chờ đến khi chuyển sang trang đích

-	Không thể dùng request để get nội dung html Vietnamwork do phải đợi 1 thời gian ngắn mới xuất hiện. 
 Giải pháp dùng Selenium

-	Sau khi crawl dữ liệu từ VietnamWork, đến thời điểm hiện tại web đã đổi source code html ☹

