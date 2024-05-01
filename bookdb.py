import mysql.connector
from ibookdb import IBOOKDB
from queryresult import QueryResult

class BOOKDB(IBOOKDB):

    def __init__(self,user,password,host,database,port):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.port = port
        self.connection = None

    def initialize(self):
        self.connection = mysql.connector.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database,
            port=self.port
        )
        
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()


    def createTables(self):
        create_table_queries = [
            """
            CREATE TABLE IF NOT EXISTS author (
                author_id INT PRIMARY KEY,
                author_name VARCHAR(60)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS publisher (
                publisher_id INT PRIMARY KEY,
                publisher_name VARCHAR(50)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS book (
                isbn CHAR(13) PRIMARY KEY,
                book_name VARCHAR(120),
                publisher_id INT,
                first_publish_year CHAR(4),
                page_count INT,
                category VARCHAR(25),
                rating FLOAT,
                FOREIGN KEY (publisher_id) REFERENCES publisher(publisher_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS author_of (
                isbn CHAR(13),
                author_id INT,
                FOREIGN KEY (isbn) REFERENCES book(isbn),
                FOREIGN KEY (author_id) REFERENCES author(author_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS phw1 (
                isbn CHAR(13),
                book_name VARCHAR(120),
                rating FLOAT
            )
            """
        ]
        self.initialize()
        created_tables = 0
        for query in create_table_queries:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            created_tables += 1
        return created_tables

    def dropTables(self):
        drop_table_queries = [
            "DROP TABLE IF EXISTS author_of",
            "DROP TABLE IF EXISTS book",
            "DROP TABLE IF EXISTS author",
            "DROP TABLE IF EXISTS publisher",
            "DROP TABLE IF EXISTS phw1"
        ]
        dropped_tables = 0
        for query in drop_table_queries:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            dropped_tables += 1
        
        # Bağlantıyı kapat
        self.disconnect()
        
        return dropped_tables
    def insertAuthor(self,authors):
        try:
            # Veritabanı bağlantısını kontrol et
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # Her bir yazarı döngüyle işle
                for author in authors:
                    # SQL sorgusu oluştur ve yürüt
                    sql_query = "INSERT INTO author (author_id, author_name) VALUES (%s, %s)"
                    cursor.execute(sql_query, (author.author_id, author.author_name))
                    
                # Veritabanı işlemlerini kaydet
                self.connection.commit()
                cursor.close()
                return len(authors)
        except mysql.connector.Error as e:
            print("Hata:", e)

      
    def insertBook(self,books):
        try:
            # Veritabanı bağlantısını kontrol et
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                for book in books:
                    # SQL sorgusu oluştur ve yürüt
                    sql_query = "INSERT INTO book (isbn, book_name, publisher_id, first_publish_year, page_count, category, rating) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql_query, (book.isbn, book.book_name, book.publisher_id, book.first_publish_year, book.page_count, book.category, book.rating))
                    
                # Veritabanı işlemlerini kaydet
                self.connection.commit()
                return len(books)
        except mysql.connector.Error as e:
            print("Hata:", e)
            
    def insertPublisher(self,publishers):
        try:
            # Veritabanı bağlantısını kontrol et
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                for publisher in publishers:
                    sql_query = "INSERT INTO publisher (publisher_id, publisher_name) VALUES (%s, %s)"
                    cursor.execute(sql_query, (publisher.publisher_id, publisher.publisher_name))
                
                self.connection.commit()
                return len(publishers)
        except mysql.connector.Error as e:
            print("Hata:", e)
            
    def insertAuthor_of(self,author_ofs):
        try:
            # Veritabanı bağlantısını kontrol et
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                for author_of in author_ofs:
                    sql_query = "INSERT INTO author_of (isbn, author_id) VALUES (%s, %s)"
                    cursor.execute(sql_query, (author_of.isbn, author_of.author_id))
                
                self.connection.commit()
                return len(author_ofs)
        except mysql.connector.Error as e:
            print("Hata:", e)
            
    def functionQ1(self):
        results = []
        try:
            # Veritabanı bağlantısını kontrol et
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # SQL sorgusunu hazırla ve yürüt
                query = """
                    SELECT isbn, first_publish_year, page_count, publisher_name
                    FROM book b
                    JOIN publisher p on b.publisher_id=p.publisher_id
                    WHERE b.page_count = (
                        SELECT MAX(page_count) FROM book
                    )
                    ORDER BY isbn ASC;
                """
                cursor.execute(query)

                # Sonuçları al
                rows = cursor.fetchall()

                # Her bir satır için sonuçları dönüştür ve listeye ekle
                for row in rows:
                    result = QueryResult.ResultQ1(
                        isbn=row[0],
                        first_publish_year=row[1],
                        page_count=row[2],
                        publisher_name=row[3]
                    )
                    results.append(result)

                cursor.close()

        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:
            return results

    def functionQ2(self,author_id1, author_id2):
        results = []
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                query = """   
                SELECT b.publisher_id, AVG(b.page_count) AS avg_page_count
                FROM book b
                JOIN (
                    SELECT b1.publisher_id
                    FROM author_of ao1
                    JOIN author_of ao2 ON ao1.isbn = ao2.isbn
                    JOIN book b1 ON ao1.isbn = b1.isbn
                    WHERE ao1.author_id = %s AND ao2.author_id = %s
                ) AS joint_books ON b.publisher_id = joint_books.publisher_id
                GROUP BY b.publisher_id
                ORDER BY b.publisher_id ASC;
                """
                cursor.execute(query, (author_id1, author_id2))
                rows = cursor.fetchall()

                for row in rows:
                    result = QueryResult.ResultQ2(
                        publisher_id=row[0],
                        average_page_count=row[1]
                    )
                    results.append(result)

                cursor.close()
                    
        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:    
            return results

    def functionQ3(self,author_name):
        results = []
        try:
            # Veritabanı bağlantısını kontrol et
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # Input bir string bu nedenle (,)'e gore split edelim.
                authors = [author.strip() for author in author_name.split(',')]

                # Sadece bir isim varsa, SQL sorgusunu dogrudan oluştur
                if len(authors) == 1:
                    query = """
                        SELECT b.book_name, b.category, b.first_publish_year
                        FROM author a
                        JOIN author_of ao ON a.author_id = ao.author_id
                        JOIN book b ON ao.isbn = b.isbn
                        WHERE a.author_name = %s
                        ORDER BY b.first_publish_year ASC, b.book_name ASC, b.category ASC;
                    """
                    cursor.execute(query, (authors[0],))
                else:
                    # Eğer birden fazla isim varsa, SQL sorgusunu oluştur
                    query = """
                        SELECT b.book_name, b.category, b.first_publish_year
                        FROM author a
                        JOIN author_of ao ON a.author_id = ao.author_id
                        JOIN book b ON ao.isbn = b.isbn
                        WHERE a.author_name IN ({})
                        ORDER BY b.first_publish_year ASC, b.book_name ASC, b.category ASC;
                    """.format(', '.join(['%s']*len(authors)))
                    cursor.execute(query, tuple(authors))

                rows = cursor.fetchall()

                # Uygun output olusturma
                for row in rows:
                    result = QueryResult.ResultQ3(
                        book_name=row[0],
                        category=row[1],
                        first_publish_year=row[2]
                    )
                    results.append(result)
                cursor.close()
                

        except mysql.connector.Error as e:
            print("Hata:", e)
            results.append(e)
        finally:
            return results

    def functionQ4(self):
        results = []
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # SQL sorgusu
                query = """
                    SELECT DISTINCT publisher_id, category
                    FROM book
                    WHERE publisher_id IN (
                            SELECT publisher_id
                            FROM publisher
                            WHERE LENGTH(publisher_name) - LENGTH(REPLACE(publisher_name, ' ', '')) + 1 >= 3
                        )
                        AND publisher_id IN (
                            SELECT publisher_id
                            FROM book
                            GROUP BY publisher_id
                            HAVING AVG(rating) > 3 AND COUNT(*) >= 3
                        )
                    ORDER BY publisher_id ASC, category ASC;
                """
                cursor.execute(query)

                # Sonuçları al
                rows = cursor.fetchall()

                # Her bir satır için sonuçları dönüştür ve listeye ekle
                for row in rows:
                    result = QueryResult.ResultQ4(
                        publisher_id=row[0],
                        category=row[1]
                    )
                    results.append(result)

                cursor.close()
                
        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:
            return results 
        
    def functionQ5(self,author_id):
        results = []
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # SQL sorgusu
                query = """
                    SELECT a.author_id, a.author_name
                    FROM author a
                    JOIN author_of ao ON a.author_id = ao.author_id
                    JOIN book b ON ao.isbn = b.isbn
                    WHERE b.publisher_id IN (
                            SELECT DISTINCT publisher_id
                            FROM book
                            WHERE isbn IN (
                                    SELECT isbn
                                    FROM author_of
                                    WHERE author_id = %s
                                )
                        )
                    GROUP BY a.author_id, a.author_name
                    ORDER BY a.author_id ASC;
                """
                cursor.execute(query, (author_id,))

                # Sonuçları al
                rows = cursor.fetchall()

                # Her bir satır için sonuçları dönüştür ve listeye ekle
                for row in rows:
                    result = QueryResult.ResultQ5(
                        author_id=row[0],
                        author_name=row[1]
                    )
                    results.append(result)

                cursor.close()

        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:
            return results
    # ----------------------------------------------------------------------------------
    # HATALI
    def functionQ6(self):
        results = []
        try:
            # Veritabanı bağlantısını kontrol et
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # SQL sorgusunu hazırla ve yürüt
                query = """
                SELECT ao.author_id, ao.isbn
   FROM author_of ao 
   WHERE author_id NOT IN (
   SELECT DISTINCT
    author_id
FROM 
    author_of
JOIN book b ON b.isbn = author_of.isbn 
WHERE 
    b.publisher_id IN (
        SELECT 
            publisher_id
        FROM (
            SELECT 
                b.publisher_id,
                COUNT(DISTINCT author_id) AS author_count
            FROM 
                author_of
            JOIN book b ON b.isbn = author_of.isbn 
            GROUP BY 
                publisher_id
        ) AS publisher_authors
        WHERE 
            author_count > 1
    )
   );
                """
                cursor.execute(query)

                # Sonuçları al
                rows = cursor.fetchall()

                # Her bir satır için sonuçları dönüştür ve listeye ekle
                for row in rows:
                    result = QueryResult.ResultQ6(
                        author_id=row[0],
                        isbn=row[1]
                    )
                    results.append(result)

                cursor.close()

        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:
            return results

    def functionQ7(self,rating):
        results = []
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                query = """
                    SELECT publisher.publisher_id, publisher.publisher_name
                    FROM publisher
                    JOIN book ON publisher.publisher_id = book.publisher_id
                    WHERE book.category = 'Roman'
                    GROUP BY publisher.publisher_id, publisher.publisher_name
                    HAVING COUNT(book.isbn) >= 2 AND AVG(book.rating) > %s
                    ORDER BY publisher.publisher_id ASC;
                """
                cursor.execute(query, (rating,))
                rows = cursor.fetchall()

                for row in rows:
                    result = QueryResult.ResultQ7(
                        publisher_id=row[0],
                        publisher_name=row[1]
                    )
                    results.append(result)

                cursor.close()

        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:
            return results
    # ----------------------------------------------------------------------------------
    # HATALI
    def functionQ8(self):
        results = []
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # En düşük puanlı kitapların ISBN, kitap adı ve puanlarını bulma
                sql_query = """
                    SELECT 
                        isbn, 
                        book_name, 
                        rating
                    FROM 
                        book
                    WHERE 
                        (book_name, rating) IN (
                            SELECT 
                                book_name, 
                                MIN(rating)
                            FROM 
                                book
                            GROUP BY 
                                book_name
                        );
                """
                cursor.execute(sql_query)
                rows = cursor.fetchall()

                # Bulunan verileri phw1 tablosuna eklemek için BULK INSERT sorgusu oluşturma
                bulk_insert_query = """
                    INSERT INTO phw1 (isbn, book_name, rating) VALUES (%s, %s, %s);
                """
                bulk_insert_data = [(row[0], row[1], row[2]) for row in rows]
                cursor.executemany(bulk_insert_query, bulk_insert_data)
                self.connection.commit()

                # phw1 tablosundaki tüm satırları ISBN'ye göre sıralayarak listeleme
                list_query = """
                    SELECT 
                        isbn, 
                        book_name, 
                        rating
                    FROM 
                        phw1
                    ORDER BY 
                        isbn ASC;
                """
                cursor.execute(list_query)
                rows = cursor.fetchall()

                for row in rows:
                    result = QueryResult.ResultQ8(
                        isbn=row[0],
                        book_name=row[1],
                        rating=row[2]
                    )
                    results.append(result)

                cursor.close()

        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:
            return results 
    # ----------------------------------------------------------------------------------   
    def functionQ9(self,keyword):
        total_ratings = 0.0
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # Anahtar kelimeyi içeren kitapları bulma ve derecelerini güncelleme
                sql_query = """
                    UPDATE book
                    SET rating = CASE
                        WHEN rating < 4 THEN LEAST(5, rating + 1)
                        ELSE rating
                    END
                    WHERE book_name LIKE %s
                """
                cursor.execute(sql_query, ('%' + keyword + '%',))
                self.connection.commit()

                # Tüm kitapların derecelerinin toplamını bulma
                sum_query = """
                    SELECT SUM(rating)
                    FROM book
                """
                cursor.execute(sum_query)
                total_ratings = cursor.fetchone()[0]

                cursor.close()

        except mysql.connector.Error as e:
            print("Hata:", e)
        finally:
            return total_ratings
        
    def function10(self):
        try:
            result = -1
            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # Hiç kitap yayımlamamış yayınevlerini silme işlemi
                delete_query = """
                    DELETE FROM publisher
                    WHERE publisher_id NOT IN (
                        SELECT publisher_id
                        FROM book
                    )
                """
                cursor.execute(delete_query)

                # Kalan publisher gosterimi
                count_query = "SELECT COUNT(*) FROM publisher"
                cursor.execute(count_query)
                result = cursor.fetchone()[0]

                self.connection.commit()

                cursor.close()

                return result

        except mysql.connector.Error as e:
            print("Hata:", e)
            return result

