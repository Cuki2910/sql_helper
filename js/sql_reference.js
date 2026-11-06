window.NW_SQL_REFERENCE = [
  {
    title: 'Chọn cột, nhóm và tổng hợp',
    entries: [
      {
        title: '1. DISTINCT vs GROUP BY', place: 'SELECT / GROUP BY',
        explanation: 'DISTINCT bỏ các bộ giá trị trùng trong các cột SELECT. GROUP BY gom dòng để tính tổng hợp; không có tổng hợp thì hai cách có thể cho cùng tập kết quả.',
        sql: 'SELECT DISTINCT City FROM customers;\nSELECT City FROM customers GROUP BY City;',
        note: 'Không mặc định cách nào nhanh hơn. Chọn theo ý nghĩa; xem EXPLAIN để so kế hoạch thực thi.'
      },
      {
        title: '2. SELECT * vs Specific Columns', place: 'SELECT',
        explanation: 'Chỉ liệt kê các cột cần dùng để tránh lấy dữ liệu thừa. SELECT * không tự động sai nhưng dễ phụ thuộc thay đổi cấu trúc bảng.',
        sql: 'SELECT `Order ID`, `Customer ID`, `Order Date`\nFROM orders\nWHERE `Order Date` >= \'2006-04-25\';',
        note: 'Lấy ít cột có thể giảm dữ liệu truyền, bộ nhớ và giúp dùng covering index; hiệu quả cụ thể tùy query và index.'
      },
      {
        title: '4. WHERE vs HAVING', place: 'WHERE trước GROUP BY; HAVING sau GROUP BY',
        explanation: 'WHERE lọc các dòng đầu vào; HAVING lọc kết quả theo nhóm. Điều kiện COUNT/SUM của nhóm thuộc HAVING.',
        sql: 'SELECT `Customer ID`, COUNT(*) AS order_count\nFROM orders\nWHERE `Order Date` >= \'2006-01-01\'\nGROUP BY `Customer ID`\nHAVING COUNT(*) >= 2;',
        note: 'Điều kiện lọc dòng không phụ thuộc tổng hợp nên đặt ở WHERE khi phù hợp, thay vì chờ đến HAVING.'
      },
      {
        title: '10. COUNT(*) vs COUNT(column)', place: 'SELECT / HAVING',
        explanation: 'COUNT(*) đếm mọi dòng kết quả. COUNT(cột) chỉ đếm dòng có giá trị khác NULL ở cột đó.',
        sql: 'SELECT c.ID, COUNT(*) AS joined_rows,\n       COUNT(o.`Order ID`) AS order_count\nFROM customers AS c\nLEFT JOIN orders AS o ON o.`Customer ID` = c.ID\nGROUP BY c.ID;',
        note: 'LEFT JOIN giữ một dòng cho khách không có đơn: COUNT(*) là 1 nhưng COUNT(o.`Order ID`) là 0.'
      },
      {
        title: '11. COUNT vs COUNT(DISTINCT)', place: 'SELECT / HAVING',
        explanation: 'COUNT(cột) tính cả giá trị lặp khác NULL; COUNT(DISTINCT cột) chỉ đếm giá trị khác nhau, khác NULL.',
        sql: 'SELECT COUNT(`Order ID`) AS detail_rows,\n       COUNT(DISTINCT `Order ID`) AS distinct_orders\nFROM `order details`;',
        note: 'COUNT(DISTINCT) cần khi đếm đối tượng duy nhất, không phải cách che lỗi JOIN thiếu điều kiện.'
      },
      {
        title: '12. ORDER BY vs GROUP BY', place: 'GROUP BY / ORDER BY',
        explanation: 'GROUP BY tạo nhóm để tổng hợp; ORDER BY quyết định thứ tự hiển thị. GROUP BY không bảo đảm sắp xếp kết quả.',
        sql: 'SELECT Category, COUNT(*) AS product_count\nFROM products\nGROUP BY Category\nORDER BY product_count DESC, Category;',
        note: 'Muốn vừa nhóm vừa xếp hạng số lượng thì dùng cả hai, theo đúng thứ tự trên.'
      },
      {
        title: '18. ORDER BY + LIMIT vs MAX()', place: 'SELECT / ORDER BY / LIMIT',
        explanation: 'MAX() trả giá trị lớn nhất, không tự chọn bản ghi đi kèm. ORDER BY DESC LIMIT 1 chọn tối đa một bản ghi; so với MAX() trong subquery sẽ lấy tất cả bản ghi đồng hạng.',
        sql: 'SELECT MAX(`List Price`) AS max_price FROM products;\n\nSELECT ID, `Product Name`, `List Price`\nFROM products\nWHERE `List Price` IS NOT NULL\nORDER BY `List Price` DESC, ID\nLIMIT 1;\n\nSELECT ID, `Product Name`, `List Price`\nFROM products\nWHERE `List Price` = (SELECT MAX(`List Price`) FROM products);',
        note: 'Không viết SELECT ID, MAX(...) rồi kỳ vọng ID thuộc dòng có giá cao nhất.'
      }
    ]
  },
  {
    title: 'Điều kiện, chuỗi và NULL',
    entries: [
      {
        title: '14. = vs LIKE', place: 'WHERE / ON / HAVING',
        explanation: '= so sánh bằng; LIKE so khớp mẫu với % cho không hoặc nhiều ký tự, _ cho đúng một ký tự.',
        sql: 'SELECT ID, Company FROM customers WHERE Company = \'Company A\';\nSELECT ID, Company FROM customers WHERE Company LIKE \'Company %\';',
        note: 'Phân biệt hoa/thường và dấu phụ thuộc collation; = không có nghĩa luôn so khớp từng byte.'
      },
      {
        title: "15. LIKE 'abc%' vs LIKE '%abc'", place: 'WHERE',
        explanation: 'Mẫu abc% tìm chuỗi bắt đầu bằng abc; %abc tìm chuỗi kết thúc bằng abc. Mẫu %abc% tìm chuỗi chứa abc.',
        sql: 'SELECT ID, `Product Name`\nFROM products\nWHERE `Product Name` LIKE \'Northwind%\';',
        note: 'Tìm tiền tố có thể dùng B-tree index để quét khoảng nếu điều kiện phù hợp. Wildcard đầu chuỗi thường không dùng được cách quét khoảng đó; không đồng nghĩa tuyệt đối không bao giờ dùng index.'
      },
      {
        title: '16. IS NULL / IS NOT NULL vs = NULL', place: 'WHERE / ON / HAVING / CASE',
        explanation: 'NULL biểu thị thiếu hoặc chưa biết. Dùng IS NULL để tìm thiếu dữ liệu, IS NOT NULL để tìm có dữ liệu; = NULL và <> NULL không kiểm tra đúng điều này.',
        sql: 'SELECT `Order ID`, `Shipped Date`\nFROM orders\nWHERE `Shipped Date` IS NULL;\n\nSELECT `Order ID` FROM orders WHERE `Shipped Date` IS NOT NULL;',
        note: 'NULL khác số 0 và chuỗi rỗng. MySQL có <=> để so sánh bằng an toàn với NULL: NULL <=> NULL trả 1.'
      },
      {
        title: '17. BETWEEN vs >= AND <=', place: 'WHERE / HAVING',
        explanation: 'Với giá trị cùng kiểu, x BETWEEN a AND b là khoảng đóng: x >= a AND x <= b, có cả hai đầu. Mục 17 trong bản gửi bị thiếu nội dung; đây là phần bổ sung về khoảng giá trị.',
        sql: 'SELECT ID, `List Price` FROM products\nWHERE `List Price` BETWEEN 10 AND 30;\n\nSELECT `Order ID`, `Order Date` FROM orders\nWHERE `Order Date` >= \'2006-01-01\'\n  AND `Order Date` < \'2006-02-01\';',
        note: 'Lọc cả tháng trên DATETIME nên dùng khoảng nửa mở >= ngày đầu và < ngày đầu tháng sau, tránh bỏ sót giờ trong ngày cuối.'
      },
      {
        title: 'AND / OR / NOT và phép so sánh', place: 'WHERE / ON / HAVING',
        explanation: 'Kết hợp điều kiện bằng AND, OR, NOT; so sánh bằng =, <>, !=, >, >=, <, <=. AND có độ ưu tiên cao hơn OR; dùng ngoặc để rõ ý.',
        sql: 'SELECT ID, City, Company\nFROM customers\nWHERE (City = \'Seattle\' OR City = \'Boston\')\n  AND Company IS NOT NULL;',
        note: 'WHERE chỉ giữ điều kiện TRUE, không giữ UNKNOWN do NULL. NOT không biến UNKNOWN thành TRUE.'
      },
      {
        title: 'CASE WHEN THEN ELSE END', place: 'Biểu thức trong SELECT / ORDER BY / tổng hợp',
        explanation: 'Trả một giá trị theo điều kiện. CASE là biểu thức, không phải một mệnh đề đặt sau WHERE.',
        sql: 'SELECT `Order ID`,\n       CASE WHEN `Shipped Date` IS NULL THEN \'Chua giao\'\n            ELSE \'Da giao\' END AS shipping_status\nFROM orders;',
        note: 'Không có ELSE thì nhánh không khớp trả NULL. Có thể đếm có điều kiện bằng SUM(CASE WHEN ... THEN 1 ELSE 0 END).'
      },
      {
        title: 'COALESCE / IFNULL / NULLIF', place: 'Biểu thức trong SELECT / WHERE / phép tính',
        explanation: 'COALESCE chọn giá trị khác NULL đầu tiên; IFNULL(x, y) thay x bằng y khi x là NULL; NULLIF(x, y) trả NULL khi hai giá trị bằng nhau.',
        sql: 'SELECT `Order ID`, COALESCE(`Shipping Fee`, 0) AS shipping_fee,\n       IFNULL(Notes, \'No notes\') AS notes\nFROM orders;\n\nSELECT 10 / NULLIF(0, 0) AS safe_ratio;',
        note: 'NULLIF(mẫu_số, 0) tránh chia cho 0 nhưng trả NULL, không tự trả 0. Chỉ thay NULL bằng 0 khi đúng ý nghĩa dữ liệu.'
      }
    ]
  },
  {
    title: 'JOIN, EXISTS và truy vấn con',
    entries: [
      {
        title: '5. INNER JOIN vs LEFT JOIN', place: 'FROM / JOIN ... ON',
        explanation: 'INNER JOIN chỉ giữ bản ghi ghép được. LEFT JOIN giữ mọi dòng phía trái; phần cột bảng phải là NULL nếu không có dòng ghép.',
        sql: 'SELECT c.ID, c.Company, o.`Order ID`\nFROM customers AS c\nLEFT JOIN orders AS o\n  ON o.`Customer ID` = c.ID\n AND o.`Order Date` >= \'2006-01-01\';',
        note: 'Chuyển điều kiện ngày trên sang WHERE có thể loại các khách không có đơn phù hợp. ON xác định ghép, WHERE lọc kết quả sau ghép.'
      },
      {
        title: '6. JOIN vs Subquery', place: 'JOIN / WHERE / FROM',
        explanation: 'JOIN ghép dữ liệu bảng; subquery cung cấp một giá trị, tập giá trị hoặc bảng dẫn xuất cho query ngoài. Không có cách luôn nhanh hơn.',
        sql: 'SELECT p.ID, p.`Product Name`, p.`List Price`\nFROM products AS p\nWHERE p.`List Price` > (SELECT AVG(`List Price`) FROM products);',
        note: 'Query con vô hướng phải trả tối đa một dòng. Khi thay EXISTS bằng JOIN, cần chú ý JOIN có thể nhân dòng.'
      },
      {
        title: '7. EXISTS vs IN', place: 'WHERE / HAVING / CASE',
        explanation: 'EXISTS kiểm tra query con có ít nhất một dòng; IN kiểm tra giá trị thuộc tập. EXISTS hợp với câu hỏi có hay không một bản ghi liên quan.',
        sql: 'SELECT c.ID, c.Company\nFROM customers AS c\nWHERE EXISTS (\n  SELECT 1 FROM orders AS o WHERE o.`Customer ID` = c.ID\n);\n\nSELECT ID, Company FROM customers\nWHERE ID IN (SELECT `Customer ID` FROM orders);',
        note: 'EXISTS không cần lấy toàn bộ cột; SELECT 1 thể hiện ý kiểm tra tồn tại. Không khẳng định EXISTS luôn nhanh hơn IN.'
      },
      {
        title: '8. NOT EXISTS vs NOT IN', place: 'WHERE / HAVING',
        explanation: 'NOT EXISTS tìm bản ghi không có dòng liên quan thỏa điều kiện. NOT IN có bẫy khi tập query con chứa NULL: giá trị không khớp có thể cho UNKNOWN thay vì TRUE.',
        sql: 'SELECT c.ID, c.Company\nFROM customers AS c\nWHERE NOT EXISTS (\n  SELECT 1 FROM orders AS o WHERE o.`Customer ID` = c.ID\n);\n\nSELECT ID, Company FROM customers\nWHERE ID NOT IN (\n  SELECT `Customer ID` FROM orders WHERE `Customer ID` IS NOT NULL\n);',
        note: 'Ví dụ IN dùng customers.ID là khóa chính khác NULL. Nếu giá trị phía ngoài cũng có thể NULL, phải xác định thêm mong muốn với NULL; hai cách không tự động tương đương mọi trường hợp.'
      },
      {
        title: '19. Self JOIN vs Regular JOIN', place: 'FROM / JOIN cùng bảng với alias khác nhau',
        explanation: 'Self JOIN nối hai lần xuất hiện của cùng một bảng để so sánh các bản ghi trong bảng đó. Đây không phải từ khóa SELF JOIN riêng.',
        sql: 'SELECT c1.ID AS customer1, c2.ID AS customer2, c1.City\nFROM customers AS c1\nJOIN customers AS c2 ON c1.City = c2.City AND c1.ID < c2.ID;',
        note: 'c1.ID < c2.ID bỏ cặp tự ghép và cặp đảo ngược. Điều kiện này là cùng City, không phải cùng Company.'
      },
      {
        title: '20. LEFT JOIN + IS NULL vs NOT EXISTS', place: 'FROM / LEFT JOIN / WHERE',
        explanation: 'Hai mẫu đều có thể tìm bản ghi không có quan hệ ghép. Với LEFT JOIN, kiểm tra một cột chắc chắn khác NULL trên dòng phải nếu ghép thành công.',
        sql: 'SELECT c.ID, c.Company\nFROM customers AS c\nLEFT JOIN orders AS o ON o.`Customer ID` = c.ID\nWHERE o.`Order ID` IS NULL;',
        note: 'Order ID là khóa chính khác NULL. Kiểm tra một cột phải cho phép NULL như Notes sẽ lẫn cả đơn thực sự tồn tại nhưng thiếu ghi chú.'
      },
      {
        title: 'Self JOIN: cùng thành phố, cả hai không có đơn', place: 'Self JOIN + hai NOT EXISTS',
        explanation: 'Bản gửi ghi cùng company nhưng SQL so City; mẫu này đúng với yêu cầu cùng thành phố. Nếu muốn cùng công ty, đổi cả cột SELECT và điều kiện ghép sang Company.',
        sql: 'SELECT c1.ID AS customer1, c2.ID AS customer2, c1.City\nFROM customers AS c1\nJOIN customers AS c2 ON c1.City = c2.City AND c1.ID < c2.ID\nWHERE NOT EXISTS (\n  SELECT 1 FROM orders AS o WHERE o.`Customer ID` = c1.ID\n)\nAND NOT EXISTS (\n  SELECT 1 FROM orders AS o WHERE o.`Customer ID` = c2.ID\n);',
        note: 'Dùng hai LEFT JOIN như bản gửi cũng được. Phải kiểm tra không có đơn cho từng khách, không chỉ một phía.'
      },
      {
        title: 'RIGHT JOIN / CROSS JOIN', place: 'FROM / JOIN',
        explanation: 'RIGHT JOIN giữ mọi dòng bảng phải; có thể đổi thứ tự bảng để viết thành LEFT JOIN. CROSS JOIN tạo mọi tổ hợp giữa hai bảng.',
        sql: 'SELECT c.ID, o.`Order ID`\nFROM orders AS o\nRIGHT JOIN customers AS c ON o.`Customer ID` = c.ID;\n\nSELECT c.ID AS customer_id, s.ID AS shipper_id\nFROM customers AS c CROSS JOIN shippers AS s\nORDER BY c.ID, s.ID LIMIT 10;',
        note: 'CROSS JOIN có thể tạo số dòng bằng tích kích thước hai bảng. MySQL không có cú pháp FULL OUTER JOIN trực tiếp; có thể mô phỏng bằng LEFT JOIN, phần không khớp phía kia và UNION ALL.'
      }
    ]
  },
  {
    title: 'LIMIT, OFFSET và xếp hạng',
    entries: [
      {
        title: '3. LIMIT vs Subquery lấy top N', place: 'ORDER BY / LIMIT / WHERE với scalar subquery',
        explanation: 'ORDER BY ... LIMIT 3 lấy tối đa ba dòng. Lọc giá >= giá của dòng thứ ba có thể lấy thêm các sản phẩm đồng giá, nên không cùng ý nghĩa khi có ties.',
        sql: 'SELECT ID, `List Price` FROM products\nWHERE `List Price` IS NOT NULL\nORDER BY `List Price` DESC, ID LIMIT 3;\n\nSELECT ID, `List Price` FROM products\nWHERE `List Price` >= (\n  SELECT `List Price` FROM products\n  WHERE `List Price` IS NOT NULL\n  ORDER BY `List Price` DESC, ID LIMIT 1 OFFSET 2\n)\nORDER BY `List Price` DESC, ID;',
        note: 'Cần đúng số dòng nếu đủ dữ liệu: LIMIT hoặc ROW_NUMBER. Cần các mức giá khác nhau và giữ đồng hạng: DENSE_RANK.'
      },
      {
        title: '13. LIMIT có / không có ORDER BY', place: 'Cuối SELECT',
        explanation: 'LIMIT chỉ giới hạn số dòng. Không có ORDER BY thì không có bảo đảm dòng nào được chọn hoặc thứ tự nào được trả.',
        sql: 'SELECT `Order ID`, `Shipping Fee`\nFROM orders\nORDER BY `Shipping Fee` DESC, `Order ID`\nLIMIT 10;',
        note: 'Chỉ sắp theo phí chưa đủ xác định khi đồng phí. Order ID làm tiêu chí phá hòa; dữ liệu thay đổi vẫn có thể làm các trang thay đổi.'
      },
      {
        title: 'LIMIT ... OFFSET ... / LIMIT offset, count', place: 'Sau ORDER BY',
        explanation: 'LIMIT 3 OFFSET 5 bỏ qua năm dòng đầu của kết quả đã sắp xếp, rồi lấy tối đa ba dòng: vị trí 6, 7, 8. OFFSET bắt đầu từ 0 và không xóa dữ liệu.',
        sql: 'SELECT `Order ID`, `Shipping Fee`\nFROM orders\nORDER BY `Shipping Fee` DESC, `Order ID`\nLIMIT 3 OFFSET 5;\n\nSELECT `Order ID`, `Shipping Fee`\nFROM orders\nORDER BY `Shipping Fee` DESC, `Order ID`\nLIMIT 5, 3;',
        note: 'Trong dạng có dấu phẩy, số đầu là offset, số sau là số dòng. MySQL không dùng OFFSET đứng riêng không có LIMIT. Offset của trang = (số trang - 1) * kích thước trang.'
      },
      {
        title: 'DENSE_RANK: mức cao thứ 6 đến thứ 8', place: 'WITH / SELECT ... OVER / WHERE ở query ngoài',
        explanation: 'Xếp hạng các mức Shipping Fee khác nhau từ cao xuống thấp, không nhảy số khi đồng hạng; lấy hạng 6, 7, 8. Không giống lấy ba dòng bằng OFFSET.',
        sql: 'WITH ranked_orders AS (\n  SELECT `Order ID`, `Shipping Fee`,\n         DENSE_RANK() OVER (ORDER BY `Shipping Fee` DESC) AS fee_rank\n  FROM orders\n  WHERE `Shipping Fee` IS NOT NULL\n)\nSELECT `Order ID`, `Shipping Fee`, fee_rank\nFROM ranked_orders\nWHERE fee_rank BETWEEN 6 AND 8\nORDER BY fee_rank, `Order ID`;',
        note: 'Có thể trả nhiều hơn ba dòng nếu đồng phí; ít hơn nếu không đủ mức. Không thêm Order ID vào OVER của DENSE_RANK nếu cần giữ các đơn đồng phí cùng hạng.'
      },
      {
        title: 'ROW_NUMBER vs RANK vs DENSE_RANK', place: 'SELECT ... OVER (ORDER BY ...)',
        explanation: 'Với giá 100, 100, 90: ROW_NUMBER cho 1, 2, 3; RANK cho 1, 1, 3; DENSE_RANK cho 1, 1, 2.',
        sql: 'SELECT `Order ID`, `Shipping Fee`,\n       ROW_NUMBER() OVER (ORDER BY `Shipping Fee` DESC, `Order ID`) AS row_no,\n       RANK() OVER (ORDER BY `Shipping Fee` DESC) AS gap_rank,\n       DENSE_RANK() OVER (ORDER BY `Shipping Fee` DESC) AS dense_no\nFROM orders\nORDER BY `Shipping Fee` DESC, `Order ID`;',
        note: 'MySQL 8.0 có window functions. Không lọc trực tiếp alias xếp hạng trong WHERE/HAVING cùng cấp; dùng CTE hoặc derived table rồi lọc ở ngoài.'
      },
      {
        title: 'OVER / PARTITION BY: top N trong từng nhóm', place: 'SELECT với window function',
        explanation: 'PARTITION BY chia các dòng thành từng nhóm riêng cho phép tính cửa sổ nhưng không gộp mất dòng như GROUP BY. Ví dụ lấy hai đơn mới nhất của từng khách.',
        sql: 'WITH ranked AS (\n  SELECT `Order ID`, `Customer ID`, `Order Date`,\n         ROW_NUMBER() OVER (\n           PARTITION BY `Customer ID`\n           ORDER BY `Order Date` DESC, `Order ID` DESC\n         ) AS row_no\n  FROM orders\n  WHERE `Customer ID` IS NOT NULL\n)\nSELECT `Order ID`, `Customer ID`, `Order Date`\nFROM ranked WHERE row_no <= 2\nORDER BY `Customer ID`, row_no;',
        note: 'ORDER BY bên trong OVER quyết định thứ tự tính; ORDER BY ngoài cùng quyết định thứ tự hiển thị.'
      }
    ]
  },
  {
    title: 'Ngày giờ và DATE_FORMAT',
    entries: [
      {
        title: 'DATE_FORMAT: hiển thị ngày và nhóm theo tháng', place: 'SELECT / GROUP BY / ORDER BY',
        explanation: "DATE_FORMAT trả chuỗi theo mẫu, không sửa giá trị gốc. '%Y-%m' hiển thị năm-tháng, bỏ phần ngày khỏi chuỗi kết quả; không biến cột thành DATE.",
        sql: 'SELECT `Order ID`,\n       DATE_FORMAT(`Order Date`, \'%Y-%m\') AS order_month,\n       DATE_FORMAT(`Order Date`, \'%d/%m/%Y\') AS display_date,\n       DATE_FORMAT(`Order Date`, \'%Y-%m-%d %H:%i:%s\') AS display_time\nFROM orders;\n\nSELECT DATE_FORMAT(`Order Date`, \'%Y-%m\') AS order_month, COUNT(*) AS orders\nFROM orders\nGROUP BY DATE_FORMAT(`Order Date`, \'%Y-%m\')\nORDER BY order_month;',
        note: '%Y: năm bốn số; %m: tháng; %d: ngày; %H: giờ 24h; %i: phút; %s: giây. %M là tên tháng, không phải phút. Tránh bọc cột ngày trong hàm ở WHERE nếu muốn tận dụng index thường cho khoảng ngày.'
      },
      {
        title: 'DATE / YEAR / MONTH / DAY', place: 'Biểu thức trong SELECT / GROUP BY',
        explanation: 'DATE lấy phần ngày, bỏ phần giờ. YEAR, MONTH, DAY lấy từng thành phần dạng số.',
        sql: 'SELECT `Order ID`, DATE(`Order Date`) AS order_day,\n       YEAR(`Order Date`) AS order_year,\n       MONTH(`Order Date`) AS order_month,\n       DAY(`Order Date`) AS day_of_month\nFROM orders;',
        note: 'Nhóm nhiều năm chỉ bằng MONTH sẽ gộp tháng trùng giữa các năm. Dùng cả YEAR và MONTH hoặc DATE_FORMAT(..., \'%Y-%m\').'
      },
      {
        title: 'DATEDIFF / TIMESTAMPDIFF', place: 'Biểu thức trong SELECT / WHERE',
        explanation: 'DATEDIFF(kết_thúc, bắt_đầu) tính chênh lệch phần ngày, bỏ phần giờ. TIMESTAMPDIFF(đơn_vị, bắt_đầu, kết_thúc) tính chênh lệch theo đơn vị được chọn.',
        sql: 'SELECT `Order ID`,\n       DATEDIFF(`Shipped Date`, `Order Date`) AS shipping_days,\n       TIMESTAMPDIFF(HOUR, `Order Date`, `Shipped Date`) AS shipping_hours\nFROM orders\nWHERE `Shipped Date` IS NOT NULL;',
        note: 'Thứ tự đối số của hai hàm khác nhau. Đơn vị TIMESTAMPDIFF viết như DAY, HOUR, MONTH, YEAR, không đặt trong dấu nháy.'
      },
      {
        title: 'DATE_ADD / DATE_SUB / INTERVAL', place: 'Biểu thức ngày trong SELECT / WHERE',
        explanation: 'Cộng hoặc trừ một khoảng ngày giờ. Dùng mốc bắt đầu và mốc kết thúc để lọc khoảng thay vì định dạng chuỗi ngày.',
        sql: 'SELECT `Order ID`,\n       DATE_ADD(`Order Date`, INTERVAL 7 DAY) AS after_seven_days,\n       DATE_SUB(`Order Date`, INTERVAL 1 MONTH) AS previous_month\nFROM orders;',
        note: 'INTERVAL 1 MONTH là một tháng lịch, không cố định 30 ngày. Mốc ở cuối tháng có thể được điều chỉnh về ngày cuối tháng đích.'
      },
      {
        title: 'STR_TO_DATE: chuỗi thành ngày', place: 'Biểu thức chuyển đổi',
        explanation: 'Đọc chuỗi theo mẫu ngày giờ. Khác DATE_FORMAT là đổi giá trị ngày giờ thành chuỗi hiển thị.',
        sql: 'SELECT STR_TO_DATE(\'25/04/2006\', \'%d/%m/%Y\') AS parsed_date;',
        note: 'Chuỗi và mẫu phải khớp. Khi lưu dữ liệu, ưu tiên cột DATE/DATETIME thay cho text ngày tháng.'
      },
      {
        title: 'CURDATE / NOW: ngày và thời điểm hiện tại', place: 'Biểu thức trong SELECT / WHERE',
        explanation: 'CURDATE() trả ngày hiện tại; NOW() trả ngày và giờ theo múi giờ phiên kết nối MySQL.',
        sql: 'SELECT CURDATE() AS current_day, NOW() AS current_time_value,\n       DATE_SUB(CURDATE(), INTERVAL 30 DAY) AS thirty_days_ago;',
        note: 'Dữ liệu Northwind đi kèm là dữ liệu lịch sử; lọc theo ngày hiện tại có thể không có kết quả.'
      }
    ]
  },
  {
    title: 'Biểu thức, hàm chuỗi và phép tính',
    entries: [
      {
        title: 'CONCAT / CONCAT_WS / TRIM / LOWER / UPPER / SUBSTRING', place: 'Biểu thức trong SELECT / WHERE',
        explanation: 'Ghép chuỗi, bỏ khoảng trắng hai đầu, đổi chữ hoa/thường hoặc lấy một đoạn. CONCAT trả NULL nếu có đối số NULL; CONCAT_WS bỏ qua đối số NULL sau dấu phân cách.',
        sql: 'SELECT ID,\n       CONCAT_WS(\' \', `First Name`, `Last Name`) AS full_name,\n       UPPER(TRIM(Company)) AS company_upper,\n       LOWER(City) AS city_lower, SUBSTRING(Company, 1, 7) AS prefix,\n       LENGTH(Company) AS byte_count, CHAR_LENGTH(Company) AS character_count\nFROM customers;',
        note: 'SUBSTRING đánh vị trí dương từ 1. LENGTH đếm byte; CHAR_LENGTH đếm ký tự, có thể khác nhau với tiếng Việt.'
      },
      {
        title: 'ROUND / CAST và phép tính doanh thu', place: 'Biểu thức trong SELECT',
        explanation: 'ROUND làm tròn; CAST đổi kiểu dữ liệu. Tính giá trị dòng bán bằng Quantity * Unit Price * (1 - Discount) khi Discount lưu dạng tỷ lệ.',
        sql: 'SELECT `Order ID`, `Product ID`,\n       ROUND(Quantity * `Unit Price` * (1 - COALESCE(Discount, 0)), 2) AS line_revenue,\n       CAST(Quantity AS DECIMAL(12, 2)) AS quantity_decimal\nFROM `order details`;',
        note: 'Không làm tròn từng dòng trước khi cộng tổng trừ khi yêu cầu nghiệp vụ như vậy. Kiểm tra đơn vị chiết khấu: 0.1 khác với 10.'
      },
      {
        title: 'SUM / AVG / MIN / MAX và tổng hợp có điều kiện', place: 'SELECT / HAVING; OVER nếu dùng dạng cửa sổ',
        explanation: 'SUM cộng, AVG lấy trung bình, MIN/MAX lấy cực trị. Các hàm này bỏ qua giá trị NULL; một tập không có giá trị để tính thường cho NULL, còn COUNT cho 0.',
        sql: 'SELECT `Customer ID`, SUM(`Shipping Fee`) AS total_shipping,\n       AVG(`Shipping Fee`) AS average_shipping,\n       MIN(`Shipping Fee`) AS min_shipping, MAX(`Shipping Fee`) AS max_shipping,\n       SUM(CASE WHEN `Shipped Date` IS NULL THEN 1 ELSE 0 END) AS unshipped_orders\nFROM orders\nGROUP BY `Customer ID`;',
        note: 'AVG chỉ tính những giá trị khác NULL. AVG(COALESCE(cột, 0)) có thể cho kết quả khác AVG(cột).'
      }
    ]
  },
  {
    title: 'UNION, CTE và phép tập hợp',
    entries: [
      {
        title: '9. UNION vs UNION ALL', place: 'Giữa các query SELECT',
        explanation: 'UNION ghép kết quả rồi loại dòng trùng trên tất cả cột đã chọn. UNION ALL giữ cả dòng trùng, tránh bước khử trùng.',
        sql: 'SELECT City FROM customers\nUNION\nSELECT City FROM suppliers\nORDER BY City;\n\nSELECT City FROM customers\nUNION ALL\nSELECT City FROM suppliers\nORDER BY City;',
        note: 'Các nhánh cần cùng số cột, kiểu tương thích. ORDER BY cuối áp dụng cho kết quả chung; muốn ORDER BY/LIMIT riêng từng nhánh thì đặt nhánh trong ngoặc.'
      },
      {
        title: 'WITH ... AS: CTE và derived table', place: 'WITH trước SELECT; derived table trong FROM',
        explanation: 'CTE đặt tên một tập kết quả trong phạm vi câu lệnh để tách bước đọc query. Derived table là SELECT đặt trong FROM và cần alias.',
        sql: 'WITH customer_totals AS (\n  SELECT `Customer ID`, COUNT(*) AS order_count\n  FROM orders GROUP BY `Customer ID`\n)\nSELECT c.ID, c.Company, t.order_count\nFROM customers AS c\nJOIN customer_totals AS t ON t.`Customer ID` = c.ID\nWHERE t.order_count >= 2;',
        note: 'CTE không tự tạo bảng lưu trữ và không mặc định nhanh hơn subquery. MySQL 8.0 hỗ trợ WITH; query cuối vẫn có thứ tự SELECT/FROM/WHERE/... thông thường.'
      },
      {
        title: 'INTERSECT / EXCEPT và cách viết cho MySQL 8.0.28', place: 'Phép tập hợp hoặc WHERE EXISTS / NOT EXISTS',
        explanation: 'INTERSECT lấy phần giao; EXCEPT lấy phần có ở tập trái nhưng không ở tập phải. Hai toán tử này cần MySQL 8.0.31 trở lên, nên bản thi 8.0.28 dùng EXISTS/NOT EXISTS thay thế.',
        sql: 'SELECT DISTINCT c.City\nFROM customers AS c\nWHERE EXISTS (SELECT 1 FROM suppliers AS s WHERE s.City <=> c.City);\n\nSELECT DISTINCT c.City\nFROM customers AS c\nWHERE NOT EXISTS (SELECT 1 FROM suppliers AS s WHERE s.City <=> c.City);',
        note: 'Hai query minh họa giao và hiệu của tập City, bỏ trùng. Dùng <=> để NULL ở hai phía được coi là cùng giá trị trong phép tập hợp.'
      }
    ]
  }
];
